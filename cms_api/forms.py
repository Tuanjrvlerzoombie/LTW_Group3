from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Post, User
from django import forms
from .models import Post


class AuthorArticleForm(forms.ModelForm):
    """Form cho Author để thêm bài viết với tùy chọn đơn giản hơn"""

    class Meta:
        model = Post
        fields = ['title', 'content', 'categories_name', 'tag', 'image', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter article title',
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Enter article content',
                'rows': 8,
                'class': 'form-control'
            }),
            'categories_name': forms.Select(attrs={
                'class': 'form-control category-select'
            }),
            'tag': forms.TextInput(attrs={
                'placeholder': 'Add tags (comma separated)',
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Chỉ đặt status='pending' cho bài viết mới (chưa có pk)
        if not self.instance.pk:
            self.instance.status = 'pending'

class AccountForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'avatar']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AccountAddForm(AccountForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
