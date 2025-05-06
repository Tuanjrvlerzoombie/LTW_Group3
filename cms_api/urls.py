from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Public URLs
    path('', views.public_home, name='public_home'),
    path('article/<int:pk>/', views.public_article_detail, name='public_article_detail'),

    # Admin URLs
    path('admin-dashboard/', views.home, name='home'),
    path('admin-dashboard/article/<int:pk>/', views.article_detail, name='article_detail'),
    path('admin-dashboard/add-article-author/', views.add_article, name='add_article_author'),
    path('admin-dashboard/article/<int:pk>/publish/', views.publish_article, name='publish_article'),
    path('admin-dashboard/article/<int:pk>/reject/', views.reject_article, name='reject_article'),
    path('admin-dashboard/article/<int:pk>/update/', views.update_article, name='update_article'),
    path('admin-dashboard/article/<int:pk>/delete/', views.delete_article, name='delete_article'),
    path('admin-dashboard/management/', views.management_view, name='management'),
    path('admin-dashboard/profile/', views.profile_view, name='profile'),
    path('admin-dashboard/profile/update/', views.update_profile, name='update_profile'),
]
