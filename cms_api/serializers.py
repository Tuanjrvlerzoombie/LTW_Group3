from rest_framework import serializers
from .models import User, Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'location', 'profile_summary']


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    editor_name = serializers.ReadOnlyField(source='editor.username')

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'status', 'author', 'author_name',
            'editor', 'editor_name', 'categories_name', 'created_at',
            'updated_at', 'tag', 'image'
        ]