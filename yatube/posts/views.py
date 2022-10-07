from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Follow, Post, Group, User, Comment
from .forms import PostForm, CommentForm
from .utils import add_paginator_on_page


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related('group')
    page_obj = add_paginator_on_page(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    post_list = group.posts.all()
    page_obj = add_paginator_on_page(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    post_count = post_list.count()
    page_obj = add_paginator_on_page(post_list, request)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author).filter(user=request.user)
    following = False
    context = {
        'page_obj': page_obj,
        'post_count': post_count,
        'author': author,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    post_count = author.posts.all().count()
    comments = Comment.objects.filter(post_id=post_id)
    context = {
        'form': CommentForm(),
        'post': post,
        'post_count': post_count,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author.username)

        return render(request, 'posts/create_post.html', {'form': form})

    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    is_edit = True
    if request.user != author:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    following = Follow.objects.filter(user=request.user)
    posts_list = Post.objects.filter(
        author__in=[*[follow.author for follow in following]]
    )
    page_obj = add_paginator_on_page(posts_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user)
    Unfollow = True
    for follow in following:
        if follow.author == author:
            Unfollow = False
    if request.user != author and Unfollow:
        follow = Follow()
        follow.user = request.user
        follow.author = author
        follow.save()
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    get_object_or_404(Follow, author=author, user=request.user).delete()
    return redirect('posts:follow_index')
