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


    #thanh điều hướng tỏng public-home
    path('vocabulary/', views.vocabulary_view, name='vocabulary'),
    path('grammar/', views.grammar_view, name='grammar'),
    path('listening/', views.listening_view, name='listening'),
    path('speaking/', views.speaking_view, name='speaking'),
    path('reading/', views.reading_view, name='reading'),
    path('writing/', views.writing_view, name='writing'),
    path('exams/', views.exams_view, name='exams'),
    path('conversational/', views.conversational_view, name='conversational'),
    path('business/', views.business_view, name='business'),
    path('culture/', views.culture_view, name='culture'),
    path('resources/', views.resources_view, name='resources'),
    path('community/', views.community_view, name='community'),
    path('ielts/', views.ielts_view, name='ielts'),
    path('toeic/', views.toeic_view, name='toeic'),
    path('toefl/', views.toefl_view, name='toefl'),
    path('cambridge/', views.cambridge_view, name='cambridge'),
    path('pronunciation/', views.pronunciation_view, name='pronunciation'),
    path('idioms/', views.idioms_view, name='idioms'),
    path('phrasal_verbs/', views.phrasal_verbs_view, name='phrasal_verbs'),
    path('podcasts/', views.podcasts_view, name='podcasts'),
    path('videos/', views.videos_view, name='videos'),
    path('apps/', views.apps_view, name='apps'),
    path('books/', views.books_view, name='books'),
    path('search/', views.search_view, name='search'),
]
