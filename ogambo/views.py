from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Post, Vote, Tag, Profile, Bookmark
from .forms import PostForm, CustomUserCreationForm
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
import os

# Create your views here.

def userAuth(request):
    return render(request, 'ogambo/user_auth.html')

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
    return render(request, 'ogambo/forms/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured while registering')
    context = {'form' : form}
    return render(request, 'ogambo/forms/login_register.html', context)

def userProfile(request, username):
    user = User.objects.get(username=username)
    profile = user.profile
    posts = user.post_set.all()
    user_votes = {}
    if request.user.is_authenticated:
        votes = Vote.objects.filter(user=request.user)
        user_votes = {vote.post_id: vote.vote_type for vote in votes}

    for post in posts:
        post.is_upvoted = user_votes.get(post.id) is True
        post.is_downvoted = user_votes.get(post.id) is False
    tags = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:50]
    context = {
        'tags': tags,
        'user_profile': user,
        'profile': profile,
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

@csrf_exempt
def bookmark(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

    if not created:  # If the bookmark already exists, remove it
        bookmark.delete()
        return JsonResponse({'bookmarked': False})
    else:  # Otherwise, create the bookmark
        return JsonResponse({'bookmarked': True})

def home(request):
    q = request.GET.get('q', '')  # Get the search query or default to an empty string
    bookmarked_only = request.GET.get('bookmarked', 'false').lower() == 'true'

    posts = Post.objects.filter(
        Q(tags__name__icontains=q) |
        Q(title__icontains=q) |
        Q(user__username__icontains=q)
    ).distinct()

    if bookmarked_only and request.user.is_authenticated:
        posts = posts.filter(bookmarks__user=request.user)

    user_votes = {}
    if request.user.is_authenticated:
        votes = Vote.objects.filter(user=request.user)
        user_votes = {vote.post_id: vote.vote_type for vote in votes}

        for post in posts:
            post.is_upvoted = user_votes.get(post.id) is True
            post.is_downvoted = user_votes.get(post.id) is False
            post.is_bookmarked = post.bookmarks.filter(user=request.user).exists()

    tags = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:50]

    context = {'posts': posts, 'tags': tags}
    return render(request, 'ogambo/home.html', context)

def post(request, pk):
    post = Post.objects.get(id=pk)  # Get the specific post
    tags = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:50]

    posts = Post.objects.filter(
        tags__in=post.tags.all()
    ).exclude(id=post.id).distinct()

    context = {'post': post, 'tags': tags, 'posts': posts}
    return render(request, 'ogambo/post.html', context)

def generateMediaDownload(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if not post.image and not post.video:
        return HttpResponse("No media available for this post.", status=404)

    try:
        if post.video and os.path.exists(post.video.path):  # Ensure video file exists
            video_path = post.video.path
            video_filename = f"video_{post_id}.{post.video.path.split('.')[-1]}"
            return FileResponse(open(video_path, 'rb'), as_attachment=True, filename=video_filename)

        elif post.image and os.path.exists(post.image.path):  # Ensure image file exists
            image_path = post.image.path
            image_filename = f"image_{post_id}.png"
            return FileResponse(open(image_path, 'rb'), as_attachment=True, filename=image_filename)

        else:
            return HttpResponse("Media file does not exist on the server.", status=404)

    except Exception as e:
        return HttpResponse(f"Error downloading media: {str(e)}", status=500)

@login_required(login_url='user-auth')
def createPost(request):
    if request.method == 'POST':
        print("Received POST request")
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)

        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid")
            post = form.save(commit=False)
            post.user = request.user
            
            # Handle uploaded files
            if 'image' in request.FILES:
                post.image = request.FILES['image']
            if 'video' in request.FILES:
                post.video = request.FILES['video']
            
            post.save()

            # Process tags
            tags_input = form.cleaned_data['tags_input']
            tags = PostForm.parse_tags(tags_input)
            post.tags.set(tags)

            print("Post created successfully")
            return redirect('home')
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        print("GET request received")
        form = PostForm()

    context = {'form': form}
    return render(request, 'ogambo/forms/post_form.html', context)

@login_required(login_url='user-auth')
def updatePost(request, pk):
    post = get_object_or_404(Post, id=pk)
    
    if request.user != post.user:
        messages.error(request, "You are not allowed to do this!")
        return redirect('home')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PostForm(instance=post)
        form.fields['tags_input'].initial = '#' + ' #'.join(tag.name for tag in post.tags.all())

    context = {
        'form': form,
        'existing_image': post.image.url if post.image else None,
        'existing_video': post.video.url if post.video else None,
    }
    return render(request, 'ogambo/forms/post_form.html', context)

@login_required(login_url='user-auth')
def deletePost(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'ogambo/delete.html', {'obj' : post})

def explore(request):
    tags = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:50]

    context = {'tags': tags}
    return render(request, 'ogambo/discover.html', context)

@login_required(login_url='user-auth')
def bookmarksFeed(request):
    bookmarked_only = request.GET.get('bookmarked', 'false').lower() == 'true'

    posts = Post.objects.all()

    if bookmarked_only and request.user.is_authenticated:
        posts = Post.objects.filter(bookmarks__user=request.user)

    context = {'posts': posts}
    return render(request, 'ogambo/bookmarks.html', context)