from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm

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


def create_room(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'base/room_form.html', context={'form': RoomForm()})

def update_room(request, pk):
    room_instance = Room.objects.get(id=pk)
    form = RoomForm(instance=room_instance)

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room_instance)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'base/room_form.html', context={'form': form})

def delete_room(request, pk):
    room_instance = Room.objects.get(id=pk)
    if request.method == "POST":
        room_instance.delete()
        return redirect('home')
    return render(request, 'base/delete.html', context={'obj': room_instance})