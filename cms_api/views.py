from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordChangeForm
from .models import Post, User
from .forms import AuthorArticleForm
import random
import string
import os
from django.conf import settings


# Authentication views
def login_view(request):
    """View for user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)

            # Xử lý "Remember me"
            if not remember:
                request.session.set_expiry(0)  # Phiên sẽ hết hạn khi đóng trình duyệt

            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'cms_api/login.html')


def logout_view(request):
    """View for user logout"""
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('public_home')


# Public views
def public_home(request):
    """View for the public home page"""
    # Get only published articles
    published_articles = Post.objects.filter(status='published').order_by('-created_at')

    # Get a featured article (first one or random)
    featured_article = None
    if published_articles.exists():
        featured_article = published_articles.first()
        # Exclude the featured article from the regular list
        published_articles = published_articles.exclude(id=featured_article.id)

    context = {
        'featured_article': featured_article,
        'articles': published_articles,
    }

    return render(request, 'cms_api/public/home.html', context)


def public_article_detail(request, pk):
    """View for the public article detail page"""
    # Get the article and ensure it's published
    article = get_object_or_404(Post, pk=pk, status='published')

    # Get related articles (same category, excluding current)
    related_articles = Post.objects.filter(
        status='published',
        categories_name=article.categories_name
    ).exclude(id=article.id).order_by('-created_at')[:2]

    # If not enough related articles in the same category, get some random ones
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
    # Lấy tất cả bài viết (không chỉ published)
    posts = Post.objects.all().order_by('-created_at')

    # Thống kê số lượng bài viết theo trạng thái
    post_stats = {
        'published': Post.objects.filter(status='published').count(),
        'pending': Post.objects.filter(status='pending').count() + Post.objects.filter(status='draft').count(),
        'planned': Post.objects.filter(status='planned').count(),
        'reject': Post.objects.filter(status='reject').count(),
    }

    # Truyền dữ liệu vào template
    context = {
        'posts': posts,
        'post_stats': post_stats,
        'active_view': 'table',  # Mặc định hiển thị dạng bảng
    }

    return render(request, 'cms_api/home.html', context)


@login_required(login_url='login')
def article_detail(request, pk):
    # Lấy chi tiết bài viết
    post = get_object_or_404(Post, pk=pk)

    # Truyền dữ liệu vào template
    context = {
        'post': post,
    }

    return render(request, 'cms_api/article_detail.html', context)


@login_required(login_url='login')
def publish_article(request, pk):
    """View for editor to publish an article"""
    if request.method == 'POST' and (request.user.role == 'editor' or request.user.role == 'admin'):
        post = get_object_or_404(Post, pk=pk)
        post.status = 'published'
        post.editor = request.user
        post.save()
        messages.success(request, 'Article has been published successfully!')
    return redirect('article_detail', pk=pk)


@login_required(login_url='login')
def reject_article(request, pk):
    """View for editor to reject an article"""
    if request.method == 'POST' and (request.user.role == 'editor' or request.user.role == 'admin'):
        post = get_object_or_404(Post, pk=pk)
        post.status = 'reject'
        post.editor = request.user
        post.save()
        messages.success(request, 'Article has been rejected.')
    return redirect('article_detail', pk=pk)


@login_required(login_url='login')
def update_article(request, pk):
    """View for updating article information"""
    post = get_object_or_404(Post, pk=pk)

    # Check edit permissions (author or editor)
    if not (request.user == post.author or request.user.role == 'editor' or request.user.role == 'admin'):
        messages.error(request, 'You do not have permission to edit this article.')
        return redirect('article_detail', pk=pk)

    if request.method == 'POST':
        # Get data from form
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.categories_name = request.POST.get('categories_name')
        post.tag = request.POST.get('tag')

        # Update status if user is editor or admin
        if request.user.role == 'editor' or request.user.role == 'admin':
            post.status = request.POST.get('status')
            if post.status == 'published':
                post.editor = request.user

        # Handle image upload
        if 'image' in request.FILES:
            post.image = request.FILES['image']

        # Handle file upload
        if 'file' in request.FILES:
            post.file = request.FILES['file']

        post.save()
        messages.success(request, 'Article has been updated successfully!')

    return redirect('article_detail', pk=pk)


@login_required(login_url='login')
def add_article(request):
    """View for Author to add an article"""
    # Check if user is author or admin
    if not (request.user.role == 'author' or request.user.role == 'admin'):
        messages.error(request, 'You do not have permission to add articles.')
        return redirect('home')

    if request.method == 'POST':
        form = AuthorArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = 'pending'  # Changed from 'draft' to 'pending'
            article.save()
            messages.success(request, 'Article has been submitted for review!')
            return redirect('home')
    else:
        form = AuthorArticleForm()

    context = {
        'form': form,
    }
    return render(request, 'cms_api/add_article_author.html', context)


@login_required(login_url='login')
def delete_article(request, pk):
    """View for deleting an article"""
    post = get_object_or_404(Post, pk=pk)

    # Check delete permissions (author or editor)
    if not (request.user == post.author or request.user.role == 'editor' or request.user.role == 'admin'):
        messages.error(request, 'You do not have permission to delete this article.')
        return redirect('article_detail', pk=pk)

    if request.method == 'POST':
        # Delete the article
        post.delete()
        messages.success(request, 'Article has been deleted successfully!')
        return redirect('home')

    return redirect('article_detail', pk=pk)


@login_required(login_url='login')
def management_view(request):
    """View for management page (admin only)"""
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    # Get all users
    users = User.objects.all().order_by('username')

    context = {
        'users': users,
    }

    return render(request, 'cms_api/management.html', context)


@login_required(login_url='login')
def profile_view(request):
    """View for user profile"""
    # Get user's articles
    user_articles = Post.objects.filter(author=request.user).order_by('-created_at')

    context = {
        'user': request.user,
        'user_articles': user_articles,
    }

    return render(request, 'cms_api/profile.html', context)


@login_required(login_url='login')
def update_profile(request):
    """View for updating user profile"""
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'account':
            # Cập nhật thông tin cơ bản
            user = request.user
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone_number')
            user.location = request.POST.get('location')
            user.profile_summary = request.POST.get('profile_summary')
            user.save()

            messages.success(request, 'Profile has been updated successfully!')

        elif form_type == 'password':
            # Xử lý thay đổi mật khẩu
            user = request.user
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not current_password:
                messages.error(request, 'Current password is required.')
                return redirect('profile')

            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return redirect('profile')

            # Kiểm tra mật khẩu hiện tại
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return redirect('profile')

            # Đổi mật khẩu
            user.set_password(new_password)
            user.save()

            # Cập nhật session để không bị đăng xuất
            update_session_auth_hash(request, user)

            messages.success(request, 'Password has been changed successfully.')

    return redirect('profile')
