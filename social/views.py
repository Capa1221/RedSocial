from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Relationship
from .forms import UserRegisterForm, PostForm, ProfileUpdateForm


@login_required
def feed(request):
    posts = Post.objects.all().order_by('-timestamp')
    return render(request, 'social/feed.html', {'posts': posts})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Usuario {username} creado correctamente.')
            return redirect('feed')
    else:
        form = UserRegisterForm()
    return render(request, 'social/register.html', {'form': form})


@login_required
def post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post enviado correctamente.')
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'social/post.html', {'form': form})

@login_required
def profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
        posts = user.posts.all().order_by('-timestamp')
    else:
        user = request.user
        posts = user.posts.all().order_by('-timestamp')

    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, 'Your profile image has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user': user,
        'posts': posts,
        'p_form': p_form
    }
    return render(request, 'social/profile.html', context)


@login_required
def follow(request, username):
    to_user = get_object_or_404(User, username=username)
    
    if request.user == to_user:
        messages.error(request, 'No puedes seguirte a ti mismo.')
    else:
        rel, created = Relationship.objects.get_or_create(from_user=request.user, to_user=to_user)
        if created:
            messages.success(request, f'Sigues a {username}.')
        else:
            messages.info(request, f'Ya sigues a {username}.')
    
    return redirect('feed')


@login_required
def unfollow(request, username):
    to_user = get_object_or_404(User, username=username)
    
    try:
        rel = Relationship.objects.get(from_user=request.user, to_user=to_user)
        rel.delete()
        messages.success(request, f'Ya no sigues a {username}.')
    except Relationship.DoesNotExist:
        messages.info(request, f'No estabas siguiendo a {username}.')
    
    return redirect('feed')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Su cambio a sido exitoso')
            return redirect('profile', username=request.user.username)
    else:
        form = PostForm(instance=post)
    return render(request, 'social/edit_post.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Se elimino con exito')
        return redirect('profile', username=request.user.username)
    return render(request, 'social/confirm_delete.html', {'post': post})