from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView
from django.core.paginator import Paginator
from .models import User, Post, Like, Connection
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
    # Access the list of posts : 
    posts = Post.objects.all().order_by('date').reverse()
    # Set the pagination : 
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    liked_posts = []
    session_user = None
    # If the user is logged-in : 
    if request.user.id is not None :
        # Access the current logged-in user (session) :
        session_user = User.objects.get(id=request.user.id)
        # Access all the likes of the session user :
        likes = Like.objects.filter(liking_user=session_user, like_is_active=True)
        # Access the liked posts of this user
        for like in likes : 
            liked_posts.append(like.liked_post)
    return render(request, "network/index.html", {
        "session_user": session_user, 
        "liked_posts": liked_posts, 
        "page_obj": page_obj
    })

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

@login_required
def create_post(request):

    # Composing a new email must be via POST
    if request.method != "POST":
        return render(request, "network/create_post.html")
    if request.method == "POST":
        user_id = int(request.user.id)
        new_post = Post(content = request.POST["content"], post_author = User.objects.get(id=user_id), likes_count = 0)
        new_post.save()
        return HttpResponseRedirect('/')

def show_user(request, user_id):
    session_user = None
    
    # Access the user of this profile page (profile) :
    profile_user = User.objects.get(id=user_id)
    
    # Count the followers and following users :
    followers = Connection.objects.filter(followed_user=profile_user, connection_is_active=True).count()
    following = Connection.objects.filter(following_user=profile_user, connection_is_active=True).count()

    # List all posts from profile user (author)
    posts = Post.objects.filter(post_author=profile_user.id).order_by("-date")

    # If the user is logged-in : 
    if request.user.id is not None :
        # Access the current logged-in user (session) :
        session_user = User.objects.get(id=request.user.id)
    
        # Get or create the connection between profile user and session user : 
        connection, _ = Connection.objects.get_or_create(followed_user=profile_user, following_user=session_user)
        connection.save()

        # Access the liked posts of the logged-in user
        liked_posts = []
        likes = Like.objects.filter(liking_user=session_user, like_is_active=True)
        for like in likes : 
            liked_posts.append(like.liked_post)
    
    # Render the view :
    return render(request, "network/show_user.html", {
        'session_user': session_user,
        'profile_user': profile_user,
        'followers': followers, 
        'following': following,
        'connection': connection, 
        'posts': posts, 
        'liked_posts': liked_posts 
    })

def follow(request, user_id):

    # Access the user of this profile page (profile) :
    profile_user = User.objects.get(id=user_id)

    # Access the current logged-in user (session) :
    session_user = User.objects.get(id=request.user.id)

    # Get or create this connection : 
    connection = Connection.objects.get(followed_user=profile_user, following_user=session_user)

    # Toggle the status of the connection between profile user and session user : 
    if connection.connection_is_active == True:
        connection.connection_is_active = False
        connection.save()
    else :
        connection.connection_is_active = True
        connection.save()

    # Render the view :
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def following(request, user_id):
    # Access all the connections of the following user :
    connections = Connection.objects.filter(following_user=user_id, connection_is_active=True)
    # Access the followed users of these connections
    followed_users = []
    for connection in connections : 
        followed_users.append(connection.followed_user)
    # For each of these followed users, store all the posts in an empty list
    posts = []
    for user in followed_users :
        for post in Post.objects.filter(post_author=user) :
            posts.append(post)
    # Set the pagination : 
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Render the view :
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })

@login_required
def edit(request, post_id):
    if request.method == 'POST':
        # Access the selected post : 
        post = Post.objects.get(id=post_id)
        # Replace the new value of the post 
        post.content = request.POST["textarea"]
        post.save()
        # Redirect to the index page :
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def like(request, post_id):
    # Access the liked post : 
    liked_post = Post.objects.get(id=post_id)
    # Access the session user
    liking_user = request.user
    # Get or create this instance of Like :
    like, _= Like.objects.get_or_create(liked_post=liked_post, liking_user=liking_user) 
    like.save()

    # Toggle the status : 
    if like.like_is_active == True:
        like.like_is_active = False
        like.save()
        liked_post.likes_count -= 1
        liked_post.save()
    else :
        like.like_is_active = True
        like.save()
        liked_post.likes_count += 1
        liked_post.save()

    # Redirect to the index page :
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    