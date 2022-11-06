from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db.models import Q


from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


from .models import Room, Topic, Message
from .forms import RoomForm, UserForm


def loginPage(request: HttpRequest):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User  does no exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.error(request, "Username or password does not exist")

    return render(request, "base/login_register.html", {
        "page": page
    })


def registerPage(request: HttpRequest):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration")

    return render(request, 'base/login_register.html', {
        "form": form
    })


def logoutUser(request: HttpRequest):
    logout(request)
    return redirect("login")


def home(request: HttpRequest):
    q = request.GET.get("q") if request.GET.get("q") != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q),)
    # .order_by("-created")

    room_count = rooms.count()

    context = {
        "title": "Home",
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages
    }
    return render(request, "base/home.html", context)


def room(request: HttpRequest, id: int):
    room = Room.objects.get(id=id)

    roomMessages = room.message_set.all().order_by("-created")
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get("body"),
        )
        room.participants.add(request.user)
        return redirect("room", id=room.id)

    context = {
        "room": room,
        "roomMessages": roomMessages,
        "participants": participants
    }

    return render(request, "base/room.html", context)


def profilePage(request: HttpRequest, id: str):
    user = User.objects.get(id=id)
    userRooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {
        "user": user,
        "rooms": userRooms,
        "room_messages": room_messages,
        "topics": topics,
    }
    return render(request, "base/profile.html", context)


@login_required(login_url='login')
def createRoom(request: HttpRequest):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")

    context = {
        "form": form,
        "topics": topics,
    }
    return render(request, "base/room_form.html", context)


@login_required(login_url='login')
def updateRoom(request: HttpRequest, id: int):
    room = Room.objects.get(id=id)

    if request.user != room.host:
        return HttpResponse("You Not allow to update this room")

    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    context = {
        "form": form,
        "topics": topics,
        "room": room,
    }
    return render(request, "base/room_form.html", context)


@login_required(login_url='login')
def deleteRoom(request: HttpRequest, id: int):
    room = Room.objects.get(id=id)

    if request.user != room.host:
        return HttpResponse("You Not allow to delete this room")

    if request.method == 'POST':
        room.delete()
        return redirect("home")

    context = {"obj": room}
    return render(request, "base/delete.html", context)


@login_required(login_url='login')
def deleteMessage(request: HttpRequest, id: int):
    message = Message.objects.get(id=id)

    if request.user != message.user:
        return HttpResponse("You Not allow to delete this room")

    if request.method == 'POST':
        message.delete()
        return redirect("home")

    context = {"obj": message}
    return render(request, "base/delete.html", context)


@login_required(login_url="login")
def updateUser(request: HttpRequest):
    form = UserForm(instance=request.user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", id=request.user.id)
    context = {
        "form": form
    }
    return render(request, "base/update_user.html", context)


@login_required(login_url='login')
def activityPage(request: HttpRequest):
    q = request.GET.get("q") if request.GET.get("q") != None else ''

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q),)
    return render(request, "base/activity.html", {
        "room_messages": room_messages,
    })


@login_required(login_url='login')
def topicsPage(request: HttpRequest):

    topics = Topic.objects.all()
    return render(request, "base/topics.html", {
        "topics": topics,
    })
