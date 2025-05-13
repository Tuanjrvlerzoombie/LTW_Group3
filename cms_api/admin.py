from django.contrib import admin
from .models import User, Post, ActivityLog

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_online')
    list_filter = ('role', 'is_active', 'is_online')
    search_fields = ('username', 'email', 'first_name', 'last_name')

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'author__role')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'role', 'timestamp', 'post')
    list_filter = ('action', 'role')
    search_fields = ('user__username', 'details')
    date_hierarchy = 'timestamp'

admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
