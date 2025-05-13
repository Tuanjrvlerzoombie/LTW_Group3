from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Post, User


class AuthorArticleForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'categories_name', 'tag', 'image', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }


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
