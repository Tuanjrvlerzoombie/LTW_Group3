from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Post, User, ActivityLog
from .forms import AuthorArticleForm, AccountForm, AccountAddForm

import os


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(user, action, post=None, details=None):
    """
    Log user activity
    """
    ActivityLog.objects.create(
        user=user,
        action=action,
        role=user.role,
        post=post,
        details=details,
        timestamp=timezone.now()
    )

    # Update user's online status and last activity
    user.is_online = True
    user.last_activity = timezone.now()
    user.save()


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

            # Set user as online
            user.is_online = True
            user.last_activity = timezone.now()
            user.save()

            log_activity(user, 'publish', details=f'User {username} logged in')
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'cms_api/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        log_activity(request.user, 'delete', details=f'User {request.user.username} logged out')

        # Set user as offline
        request.user.is_online = False
        request.user.save()

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
        log_activity(request.user, 'publish', post, f'Published: {post.title}')
        messages.success(request, 'Article has been published successfully!')
    return redirect('article_detail', pk=pk)


@login_required(login_url='login')
def reject_article(request, pk):
    if request.method == 'POST' and request.user.role in ['editor', 'admin']:
        post = get_object_or_404(Post, pk=pk)
        post.status = 'reject'
        post.editor = request.user
        post.save()
        log_activity(request.user, 'delete', post, f'Rejected: {post.title}')
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
        log_activity(request.user, 'modify', post, f'Modified: {post.title}')
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
            log_activity(request.user, 'publish', article, f'Created: {article.title}')
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
        title = post.title
        log_activity(request.user, 'delete', post, f'Deleted: {title}')
        post.delete()
        messages.success(request, 'Article has been deleted successfully!')
        return redirect('home')

    return redirect('article_detail', pk=pk)


@login_required(login_url='login')
def management_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    # Redirect to account management
    return redirect('account_management')


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
            log_activity(user, 'modify', details='Updated profile information')
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
            log_activity(user, 'modify', details='Changed password')
            messages.success(request, 'Password has been changed successfully.')

    return redirect('profile')


# Account Management Views
@login_required(login_url='login')
def account_management(request):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    users = User.objects.all().order_by('id')

    # Filter by role if specified
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)

    context = {
        'users': users,
    }
    return render(request, 'cms_api/account_management.html', context)


@login_required(login_url='login')
def account_add(request):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    if request.method == 'POST':
        # Create a new user
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = request.POST.get('role')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone_number = request.POST.get('phone_number')
            location = request.POST.get('location')
            profile_summary = request.POST.get('profile_summary')
            is_active = 'is_active' in request.POST

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Set additional fields
            user.role = role
            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = phone_number
            user.location = location
            user.profile_summary = profile_summary
            user.is_active = is_active

            # Handle avatar upload
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']

            user.save()

            log_activity(request.user, 'publish', details=f'Created new account: {user.username}')
            messages.success(request, f'Account for {user.username} has been created successfully!')
            return redirect('account_management')

        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('account_management')

    # If GET request, redirect to account management page with modal
    return redirect('account_management')


@login_required(login_url='login')
def account_edit(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        try:
            # Update user fields
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.phone_number = request.POST.get('phone_number')
            user.location = request.POST.get('location')
            user.profile_summary = request.POST.get('profile_summary')
            user.role = request.POST.get('role')
            user.is_active = 'is_active' in request.POST

            # Update password if provided
            password = request.POST.get('password')
            if password:
                user.set_password(password)

            # Handle avatar upload
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']

            user.save()

            log_activity(request.user, 'modify', details=f'Updated account: {user.username}')
            messages.success(request, f'Account for {user.username} has been updated successfully!')

        except Exception as e:
            messages.error(request, f'Error updating account: {str(e)}')

        return redirect('account_management')

    # If GET request, redirect to account management page
    return redirect('account_management')


@login_required(login_url='login')
def account_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')

    user = get_object_or_404(User, pk=pk)

    if request.user.id == user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('account_management')

    if request.method == 'POST':
        username = user.username
        log_activity(request.user, 'delete', details=f'Deleted account: {username}')
        user.delete()
        messages.success(request, f'Account for {username} has been deleted successfully!')
        return redirect('account_management')

    context = {
        'user': user
    }
    return render(request, 'cms_api/account_delete.html', context)


@login_required(login_url='login')
def get_user_data(request, pk):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)

    user = get_object_or_404(User, pk=pk)

    # Prepare user data for JSON response
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'phone_number': user.phone_number,
        'location': user.location,
        'profile_summary': user.profile_summary,
        'is_active': user.is_active,
    }

    # Add avatar URL if available
    if user.avatar:
        data['avatar'] = user.avatar.url

    return JsonResponse(data)


# Activity Management Views
@login_required(login_url='login')
def activity_management(request):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    activities = ActivityLog.objects.all().order_by('-timestamp')

    # Filter by role if specified
    role = request.GET.get('role')
    if role:
        activities = activities.filter(role=role)

    context = {
        'activities': activities,
    }
    return render(request, 'cms_api/activity_management.html', context)
