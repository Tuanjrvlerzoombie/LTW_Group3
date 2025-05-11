from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.http import HttpResponse
from django.conf import settings

from .models import Post, User
from .forms import AuthorArticleForm

import os


# Authentication views
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'cms_api/login.html')


def logout_view(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('public_home')


# Public views
def public_home(request):
    published_articles = Post.objects.filter(status='published').order_by('-created_at')
    featured_article = published_articles.first() if published_articles.exists() else None

    if featured_article:
        published_articles = published_articles.exclude(id=featured_article.id)

    context = {
        'featured_article': featured_article,
        'articles': published_articles,
    }
    return render(request, 'cms_api/public/home.html', context)


def public_article_detail(request, pk):
    article = get_object_or_404(Post, pk=pk, status='published')
    related_articles = Post.objects.filter(
        status='published',
        categories_name=article.categories_name
    ).exclude(id=article.id).order_by('-created_at')[:2]

    if related_articles.count() < 2:
        more_articles = Post.objects.filter(
            status='published'
        ).exclude(id=article.id).exclude(
            id__in=[a.id for a in related_articles]
        ).order_by('?')[:2 - related_articles.count()]
        related_articles = list(related_articles) + list(more_articles)

    context = {
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'cms_api/public/article_detail.html', context)


# Admin views
@login_required(login_url='login')
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    post_stats = {
        'published': Post.objects.filter(status='published').count(),
        'pending': Post.objects.filter(status__in=['pending', 'draft']).count(),
        'planned': Post.objects.filter(status='planned').count(),
        'reject': Post.objects.filter(status='reject').count(),
    }
    context = {
        'posts': posts,
        'post_stats': post_stats,
        'active_view': 'table',
    }
    return render(request, 'cms_api/home.html', context)


@login_required(login_url='login')
def article_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'cms_api/article_detail.html', {'post': post})


@login_required(login_url='login')
def publish_article(request, pk):
    if request.method == 'POST' and request.user.role in ['editor', 'admin']:
        post = get_object_or_404(Post, pk=pk)
        post.status = 'published'
        post.editor = request.user
        post.save()
        messages.success(request, 'Article has been published successfully!')
    return redirect('article_detail', pk=pk)


@login_required(login_url='login')
def reject_article(request, pk):
    if request.method == 'POST' and request.user.role in ['editor', 'admin']:
        post = get_object_or_404(Post, pk=pk)
        post.status = 'reject'
        post.editor = request.user
        post.save()
        messages.success(request, 'Article has been rejected.')
    return redirect('article_detail', pk=pk)


@login_required(login_url='login')
def update_article(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if not (request.user == post.author or request.user.role in ['editor', 'admin']):
        messages.error(request, 'You do not have permission to edit this article.')
        return redirect('article_detail', pk=pk)

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.categories_name = request.POST.get('categories_name')
        post.tag = request.POST.get('tag')

        if request.user.role in ['editor', 'admin']:
            post.status = request.POST.get('status')
            if post.status == 'published':
                post.editor = request.user

        if 'image' in request.FILES:
            post.image = request.FILES['image']
        if 'file' in request.FILES:
            post.file = request.FILES['file']

        post.save()
        messages.success(request, 'Article has been updated successfully!')

    return redirect('article_detail', pk=pk)


@login_required(login_url='login')
def add_article(request):
    if request.user.role not in ['author', 'admin']:
        messages.error(request, 'You do not have permission to add articles.')
        return redirect('home')

    if request.method == 'POST':
        form = AuthorArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = 'pending'
            article.save()
            messages.success(request, 'Article has been submitted for review!')
            return redirect('home')
    else:
        form = AuthorArticleForm()

    return render(request, 'cms_api/add_article_author.html', {'form': form})


@login_required(login_url='login')
def delete_article(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if not (request.user == post.author or request.user.role in ['editor', 'admin']):
        messages.error(request, 'You do not have permission to delete this article.')
        return redirect('article_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Article has been deleted successfully!')
        return redirect('home')

    return redirect('article_detail', pk=pk)


@login_required(login_url='login')
def management_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    users = User.objects.all().order_by('username')
    return render(request, 'cms_api/management.html', {'users': users})


@login_required(login_url='login')
def profile_view(request):
    user_articles = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'cms_api/profile.html', {
        'user': request.user,
        'user_articles': user_articles
    })


@login_required(login_url='login')
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        form_type = request.POST.get('form_type')

        if form_type == 'account':
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone_number')
            user.location = request.POST.get('location')
            user.profile_summary = request.POST.get('profile_summary')

            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']

            user.save()
            messages.success(request, "Profile updated successfully.")

        elif form_type == 'password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not current_password:
                messages.error(request, 'Current password is required.')
                return redirect('profile')

            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return redirect('profile')

            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return redirect('profile')

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password has been changed successfully.')

    return redirect('profile')
