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


# class AuthorArticleForm(forms.ModelForm):
#     """Form cho Author để thêm bài viết với tùy chọn đơn giản hơn"""
#
#     class Meta:
#         model = Post
#         fields = ['title', 'content', 'categories_name', 'tag', 'image', 'file']
#         widgets = {
#             'title': forms.TextInput(attrs={'placeholder': 'Enter article title'}),
#             'content': forms.Textarea(attrs={'placeholder': 'Enter article content', 'rows': 8}),
#             'tag': forms.TextInput(attrs={'placeholder': 'Add tags (comma separated)'}),
#         }
#
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             # Bài viết của author luôn có trạng thái là pending (chờ duyệt)
#             self.instance.status = 'pending'


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