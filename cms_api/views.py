from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
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
# def public_home(request):
#     published_articles = Post.objects.filter(status='published').order_by('-created_at')
#     featured_article = published_articles.first() if published_articles.exists() else None
#
#     if featured_article:
#         published_articles = published_articles.exclude(id=featured_article.id)
#
#     context = {
#         'featured_article': featured_article,
#         'articles': published_articles,
#     }
#     return render(request, 'cms_api/public/home.html', context)

def public_home(request):
    keyword = request.GET.get('search', '')
    category = request.GET.get('category', '')
    start_day = request.GET.get('start_day', '')
    end_day = request.GET.get('end_day', '')
    form_submitted = request.GET.get('form_submitted', '')

    articles = Post.objects.filter(status='published')

    # Áp dụng bộ lọc nếu form được submit hoặc có tham số search từ thanh search
    if form_submitted or keyword:
        if keyword:
            if keyword:
                if keyword.startswith("author:"):
                    author_name = keyword.split("author:")[1].strip()
                    articles = articles.filter(author__username__icontains=author_name)
                elif keyword.startswith("category:"):
                    category_name = keyword.split("category:")[1].strip()
                    articles = articles.filter(categories_name__iexact=category_name)
                else:
                    articles = articles.filter(
                        Q(title__icontains=keyword) |
                        Q(content__icontains=keyword)
                    )

        if category and category != 'all categories':
            articles = articles.filter(categories_name__iexact=category)

        if start_day or end_day:
            try:
                # Parse dates with timezone awareness
                start_date = datetime.strptime(start_day, '%d-%b-%Y') if start_day else None
                end_date = datetime.strptime(end_day, '%d-%b-%Y') if end_day else None

                # Adjust for full day coverage
                if start_date:
                    start_date = start_date.replace(hour=0, minute=0, second=0)
                if end_date:
                    end_date = end_date.replace(hour=23, minute=59, second=59)

                # Apply date filters
                if start_date and end_date:
                    if end_date < start_date:
                        messages.warning(request, "End date cannot be earlier than start date.")
                    else:
                        articles = articles.filter(created_at__range=(start_date, end_date))
                elif start_date:
                    articles = articles.filter(created_at__gte=start_date)
                elif end_date:
                    articles = articles.filter(created_at__lte=end_date)

            except ValueError as e:
                messages.warning(request, f"Invalid date format: {str(e)}. Please use DD-MMM-YYYY (e.g., 11-May-2025).")

    # Order and get featured article
    articles = articles.order_by('-created_at')
    featured_article = None
    articles_list = list(articles)
    if articles_list:
        featured_article = articles_list.pop(0)
        articles = articles_list
    else:
        articles = []

    # # Hiển thị thông báo nếu có bộ lọc và không tìm thấy bài viết
    # if (form_submitted or keyword) and not articles and not featured_article:
    #     messages.info(request, f"No matching articles found for {'category: ' + category if category and category != 'all categories' else ''}{'start date: ' + start_day + ', end date: ' + end_day if start_day and end_day else ''}{'search term: ' + keyword if keyword else ''}".strip())

    context = {
        'featured_article': featured_article,
        'articles': articles,
        'search_query': keyword,
        'selected_category': category,
        'start_day': start_day,
        'end_day': end_day,
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


# Public view (Thanh điều hướng)
# Thanh search
def search_view(request):
    query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    start_day = request.GET.get('start_day', '')
    end_day = request.GET.get('end_day', '')

    articles = Post.objects.filter(status='published')

    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(categories_name__icontains=query)
        )

    if category and category != 'all categories':
        articles = articles.filter(categories_name__iexact=category)

    if start_day:
        try:
            start_date = datetime.strptime(start_day, '%d-%b-%Y')
            articles = articles.filter(created_at__gte=start_date)
        except ValueError:
            pass

    if end_day:
        try:
            end_date = datetime.strptime(end_day, '%d-%b-%Y')
            articles = articles.filter(created_at__lte=end_date)
        except ValueError:
            pass

    articles = articles.order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)

    if query and not articles and not featured_article:
        messages.info(request, f"No matching articles found for search: '{query}'")

    context = {
        'featured_article': featured_article,
        'articles': articles,
        'search_query': query,
        'selected_category': category,
        'start_day': start_day,
        'end_day': end_day,
    }

    return render(request, 'cms_api/public/home.html', context)


# View cho từng category
def vocabulary_view(request):
    articles = Post.objects.filter(status='published', categories_name='vocabulary').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Vocabulary'
    })

def grammar_view(request):
    articles = Post.objects.filter(status='published', categories_name='grammar').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Grammar'
    })

def listening_view(request):
    articles = Post.objects.filter(status='published', categories_name='listening').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Listening'
    })

def speaking_view(request):
    articles = Post.objects.filter(status='published', categories_name='speaking').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Speaking'
    })

def reading_view(request):
    articles = Post.objects.filter(status='published', categories_name='reading').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Reading'
    })

def writing_view(request):
    articles = Post.objects.filter(status='published', categories_name='writing').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Writing'
    })

def exams_view(request):
    articles = Post.objects.filter(status='published', categories_name='exams').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'English Exams'
    })

def conversational_view(request):
    articles = Post.objects.filter(status='published', categories_name='conversational').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Conversational English'
    })

def business_view(request):
    articles = Post.objects.filter(status='published', categories_name='business').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Business English'
    })

def culture_view(request):
    articles = Post.objects.filter(status='published', categories_name='culture').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'English Culture'
    })

def resources_view(request):
    articles = Post.objects.filter(status='published', categories_name='resources').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Free Resources'
    })

def community_view(request):
    articles = Post.objects.filter(status='published', categories_name='community').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Community'
    })

def ielts_view(request):
    articles = Post.objects.filter(status='published', categories_name='ielts').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'IELTS'
    })

def toeic_view(request):
    articles = Post.objects.filter(status='published', categories_name='toeic').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'TOEIC'
    })

def toefl_view(request):
    articles = Post.objects.filter(status='published', categories_name='toefl').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'TOEFL'
    })

def cambridge_view(request):
    articles = Post.objects.filter(status='published', categories_name='cambridge').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Cambridge'
    })

def pronunciation_view(request):
    articles = Post.objects.filter(status='published', categories_name='pronunciation').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Pronunciation'
    })

def idioms_view(request):
    articles = Post.objects.filter(status='published', categories_name='idioms').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Idioms'
    })

def phrasal_verbs_view(request):
    articles = Post.objects.filter(status='published', categories_name='phrasal_verbs').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Phrasal Verbs'
    })

def podcasts_view(request):
    articles = Post.objects.filter(status='published', categories_name='podcasts').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Podcasts'
    })

def videos_view(request):
    articles = Post.objects.filter(status='published', categories_name='videos').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Videos'
    })

def apps_view(request):
    articles = Post.objects.filter(status='published', categories_name='apps').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Apps'
    })

def books_view(request):
    articles = Post.objects.filter(status='published', categories_name='books').order_by('-created_at')
    featured_article = articles.first() if articles.exists() else None
    if featured_article:
        articles = articles.exclude(id=featured_article.id)
    return render(request, 'cms_api/public/category_template.html', {
        'featured_article': featured_article,
        'articles': articles,
        'category_name': 'Books'
    })