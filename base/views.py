from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm

def loginPage(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exists')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')

    return render(request, 'base/login_register.html', context={'pageName': 'login'})

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):

    if request.user.is_authenticated:
        return redirect('home')

    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Oops, something went wrong. Try again!')

    return render(request, 'base/login_register.html', context={'pageName': 'register', 'form': form})

def home(request):
    topicQuery = request.GET.get("topicQuery") if request.GET.get('topicQuery') else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=topicQuery) |
        Q(name__icontains=topicQuery) |
        Q(description__icontains=topicQuery)
    )
    topics = Topic.objects.all().annotate(count=Count('room')).order_by('-count')
    room_count = rooms.count()
    room_messages = Message.objects.filter(room__topic__name__icontains=topicQuery)

    return render(request, 'base/home.html', context={
                      'rooms': rooms,
                      'topics': topics,
                      'room_count': room_count,
                      'room_messages': room_messages
                  })

def room(request, pk):
    room_instance = Room.objects.get(id=pk)
    room_messages = room_instance.message_set.all().order_by('-created')
    participants = room_instance.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room_instance,
            body=request.POST.get('body')
        )

        room_instance.participants.add(request.user)
        return redirect("room", pk=room_instance.id)

    return render(request, 'base/room.html', context={'room': room_instance, 'room_messages': room_messages, 'participants': participants})

@login_required(login_url='login')
def create_room(request):
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room_instance = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        room_instance.participants.add(request.user)

        return redirect('room', pk=room_instance.id)

    return render(request, 'base/room_form.html', context={'form': RoomForm(), 'topics': topics})

@login_required(login_url='login')
def update_room(request, pk):
    topics = Topic.objects.all()
    room_instance = Room.objects.get(id=pk)
    form = RoomForm(instance=room_instance)

    if request.user != room_instance.host:
        return HttpResponse("<h1>You are not allowed here</h1>")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room_instance.name = request.POST.get('name')
        room_instance.topic = topic
        room_instance.description = request.POST.get('description')

        room_instance.save()

        return redirect('room', pk=room_instance.id)

    return render(request, 'base/room_form.html', context={'form': form, 'topics': topics, 'room': room_instance})

@login_required(login_url='login')
def delete_room(request, pk):
    room_instance = Room.objects.get(id=pk)

    if request.user != room_instance.host:
        return HttpResponse("<h1>You are not allowed here</h1>")

    if request.method == "POST":
        room_instance.delete()
        return redirect('home')
    return render(request, 'base/delete.html', context={'obj': room_instance})

@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    room_id = message.room_id

    if request.user != message.user:
        return HttpResponse("<h1>You are not allowed to delete someone's message</h1>")

    if request.method == "POST":
        message.delete()
        return redirect('room', pk=room_id)
    return render(request, 'base/delete.html', context={'obj': message})

def profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_count = rooms.count()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    return render(request, 'base/profile.html', context={
        'user': user,
        'rooms': rooms,
        'room_count': room_count,
        'room_messages': room_messages,
        'topics': topics,
    })

@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)
    return render(request, 'base/update_user.html', context={'form': form})
