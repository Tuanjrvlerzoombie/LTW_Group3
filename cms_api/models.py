from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone
import random


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('author', 'Author'),
        ('user', 'User'),
        ('viewer', 'Viewer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='author')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    profile_summary = models.TextField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now)

    @property
    def password_display(self):
        # Generate a random 10-digit number for display purposes only
        # This is not the actual password, just for UI display
        seed = self.id or 0
        random.seed(seed + 42)  # Add a constant to make it different from the ID
        return str(random.randint(1000000000, 9999999999))

    def __str__(self):
        return self.username


# Bản đã thêm category trên thanh điều hướng
class Post(models.Model):
    STATUS_CHOICES = (
        ('published', 'Published'),
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('reject', 'Reject'),
    )

    CATEGORY_CHOICES = (
        ('event', 'Event'),
        ('knowledge', 'Knowledge'),
        ('course', 'Course'),
        ('news', 'News'),
        ('vocabulary', 'Vocabulary'),
        ('grammar', 'Grammar'),
        ('listening', 'Listening'),
        ('speaking', 'Speaking'),
        ('reading', 'Reading'),
        ('writing', 'Writing'),
        ('exams', 'English Exams'),
        ('conversational', 'Conversational English'),
        ('business', 'Business English'),
        ('culture', 'English Culture'),
        ('resources', 'Free Resources'),
        ('community', 'Community'),
        ('ielts', 'IELTS'),
        ('toeic', 'TOEIC'),
        ('toefl', 'TOEFL'),
        ('cambridge', 'Cambridge'),
        ('pronunciation', 'Pronunciation'),
        ('idioms', 'Idioms'),
        ('phrasal_verbs', 'Phrasal Verbs'),
        ('podcasts', 'Podcasts'),
        ('videos', 'Videos'),
        ('apps', 'Apps'),
        ('books', 'Books'),
    )

    title = models.CharField(max_length=255, null=False)
    content = models.TextField(null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_posts')
    editor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='edited_posts')
    categories_name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='knowledge')
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


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('publish', 'Publish'),
        ('modify', 'Modify'),
        ('delete', 'Delete'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=20)  # Store the user's role at the time of the action
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    details = models.TextField(null=True, blank=True)  # Store additional details about the action

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
