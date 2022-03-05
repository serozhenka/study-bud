from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm

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
    topics = Topic.objects.all()
    room_count = rooms.count()
    return render(request, 'base/home.html', context={'rooms': rooms, 'topics': topics, 'room_count': room_count})

def room(request, pk):
    room_instance = Room.objects.get(id=pk)
    return render(request, 'base/room.html', context={'room': room_instance})

@login_required(login_url='login')
def create_room(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'base/room_form.html', context={'form': RoomForm()})

@login_required(login_url='login')
def update_room(request, pk):
    room_instance = Room.objects.get(id=pk)
    form = RoomForm(instance=room_instance)

    if request.user != room_instance.host:
        return HttpResponse("<h1>You are not allowed here</h1>")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room_instance)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'base/room_form.html', context={'form': form})

@login_required(login_url='login')
def delete_room(request, pk):
    room_instance = Room.objects.get(id=pk)

    if request.user != room_instance.host:
        return HttpResponse("<h1>You are not allowed here</h1>")

    if request.method == "POST":
        room_instance.delete()
        return redirect('home')
    return render(request, 'base/delete.html', context={'obj': room_instance})

