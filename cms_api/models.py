from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('author', 'Author'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    profile_summary = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.username


class Post(models.Model):
    STATUS_CHOICES = (
        ('published', 'Published'),
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('reject', 'Reject'),
    )

    CATEGORY_CHOICES = (
        ('Event', 'Event'),
        ('Knowledge', 'Knowledge'),
        ('Course', 'Course'),
        ('News', 'News'),
    )

    title = models.CharField(max_length=255, null=False)
    content = models.TextField(null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_posts')
    editor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='edited_posts')
    categories_name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Knowledge')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tag = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    file = models.FileField(upload_to='post_files/', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[str(self.id)])

    def get_tags_list(self):
        if self.tag:
            return self.tag.split(',')
        return []
