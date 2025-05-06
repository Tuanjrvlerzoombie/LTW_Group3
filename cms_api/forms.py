from django import forms
from .models import Post


class ArticleForm(forms.ModelForm):
    """Form cho Editor để thêm bài viết với đầy đủ tùy chọn xuất bản"""

    class Meta:
        model = Post
        fields = ['title', 'content', 'categories_name', 'tag', 'status', 'image', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter article title'}),
            'content': forms.Textarea(attrs={'placeholder': 'Enter article content', 'rows': 8}),
            'tag': forms.TextInput(attrs={'placeholder': 'Add tags (comma separated)'}),
        }


class AuthorArticleForm(forms.ModelForm):
    """Form cho Author để thêm bài viết với tùy chọn đơn giản hơn"""

    class Meta:
        model = Post
        fields = ['title', 'content', 'categories_name', 'tag', 'image', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter article title'}),
            'content': forms.Textarea(attrs={'placeholder': 'Enter article content', 'rows': 8}),
            'tag': forms.TextInput(attrs={'placeholder': 'Add tags (comma separated)'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Bài viết của author luôn có trạng thái là pending (chờ duyệt)
            self.instance.status = 'pending'
