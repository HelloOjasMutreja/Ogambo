from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Vote
from .forms import PostForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request, "User not found")
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username OR Password combination is incorrect")
    context = {'page' : page}
    return render(request, 'ogambo/forms/user_auth.html', context)
def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid:
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured while registering')
    context = {'form' : form}
    return render(request, 'ogambo/forms/user_auth.html', context)

def userProfile(request, username):
    user = User.objects.get(username=username)
    posts = user.post_set.all() 
    context = { 
        'user_profile': user, 
        'posts': posts, 
        'username': user.username
        }
    return render(request, 'ogambo/profile.html', context)

@csrf_exempt  # Allowing CSRF for this example, consider safer methods in production
@require_POST
def vote(request, pk, vote_type):
    post = get_object_or_404(Post, id=pk)
    user = request.user if request.user.is_authenticated else None
    ip_address = request.META.get('REMOTE_ADDR') if not user else None

    existing_vote = Vote.objects.filter(post=post, user=user).first() if user else Vote.objects.filter(post=post, ip_address=ip_address).first()
    if existing_vote:
        if existing_vote.vote_type == (vote_type.lower() == 'upvote'):
            existing_vote.delete()
        else:
            existing_vote.vote_type = (vote_type.lower() == 'upvote')
            existing_vote.save()
    else:
        Vote.objects.create(post=post, user=user, ip_address=ip_address, vote_type=(vote_type.lower() == 'upvote'))
    
    return JsonResponse({'upvotes': post.upvotes(), 'downvotes': post.downvotes()})

def home(request):
    posts = Post.objects.all()
    context = {'posts' : posts}
    return render(request, 'ogambo/home.html', context)

def post(request, pk):
    post = Post.objects.get(id=pk)
    context = {'post' : post}
    return render(request, 'ogambo/post.html', context)

@login_required(login_url='login')
def createPost(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Include request.FILES to handle file uploads
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form' : form}
    return render(request, 'ogambo/forms/post_form.html', context)

@login_required(login_url='login')
def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)

    if request.user != post.user:
        messages.error(request, "Your are not allowed to do this!")
        return redirect('home')

    if request.method  == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    context = {'form' : form}
    return render(request, 'ogambo/forms/post_form.html', context)

@login_required(login_url='login')
def deletePost(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'ogambo/delete.html', {'obj' : post})