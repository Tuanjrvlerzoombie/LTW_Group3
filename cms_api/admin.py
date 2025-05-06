from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Custom fields', {'fields': ('role', 'phone_number', 'location', 'profile_summary')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('username', 'email', 'role')
    ordering = ('username',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'categories_name', 'created_at')
    list_filter = ('status', 'categories_name', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'categories_name')
    date_hierarchy = 'created_at'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Post, PostAdmin)
