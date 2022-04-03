from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import User, Post, Comment, Attitude, ViewedPost


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

class HomePage(View):
    pass

class Profile(DetailView):
    model = User

class UpdateProfile(UpdateView):
    model = User

class ListFollowing(ListView):
    model = User
    
class ModifyFollowing(UpdateView):
    model = User

class ListPosts(ListView):
    model = Post
    pagination = 10

class ShowPost(DetailView):
    model = Post

class CreatePost(CreateView):
    model = Post

class UpdatePost(UpdateView):
    model = Post

class DeletePost(DeleteView):
    model = Post

class CreateReaction(CreateView):
    model = Attitude

class CommentDetails(DetailView):
    model = Comment

class ListComments(ListView):
    model = Comment

class CreateComment(CreateView):
    model = Comment

class ModifyComment(UpdateView):
    model = Comment

class DeleteComment(DeleteView):
    model = Comment
