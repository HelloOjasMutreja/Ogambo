from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm

# Create your views here.

def home(request):
    posts = Post.objects.all()
    context = {'posts' : posts}
    return render(request, 'ogambo/home.html', context)

def post(request, pk):
    post = Post.objects.get(id=pk)
    context = {'post' : post}
    return render(request, 'ogambo/post.html', context)

def createPost(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form' : form}
    return render(request, 'ogambo/forms/post_form.html', context)

def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)

    if request.method  == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    context = {'form' : form}
    return render(request, 'ogambo/forms/post_form.html', context)

def deletePost(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'ogambo/delete.html', {'obj' : post})