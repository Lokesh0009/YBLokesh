from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import BlogPost, Comment

class BlogPostForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the Title of the Blog',
            'class': 'create-title'
        })
    )
    content = forms.CharField(
        label='',
        widget=CKEditorWidget(attrs={
            'placeholder': 'Write the content here',
            'class': 'create-content'
        })
    )
    image = forms.ImageField(
        required=False,
        label='',
        widget=forms.ClearableFileInput(attrs={
            'class': 'create-image-file',
            'placeholder': 'Upload The Author Image but not mandatory '
        })
    )
    pdf = forms.FileField(
        required=False,
        label='',
        widget=forms.ClearableFileInput(attrs={
            'class': 'create-pdf-file',
            'placeholder': 'Upload The PDF but not mandatory '
        })
    )
    author = forms.CharField(
        max_length=100,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the Author Name',
            'class': 'create-author'
        })
    )

    def save(self):
        data = self.cleaned_data
        blog_post = BlogPost(
            title=data['title'],
            content=data['content'],
            image=data['image'],
            pdf=data['pdf'],
            author=data['author']
        )
        blog_post.save()

class CommentForm(forms.Form):
    author = forms.CharField(
        max_length=100,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Comment Author Name',
            'class': 'comment-author'
        })
    )
    
    text = forms.CharField(
            max_length=100,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Comment Text',
            'class': 'comment-text'
        })
    )

    blog_post_title = forms.CharField(widget=forms.HiddenInput())

    def save(self):
        data = self.cleaned_data
        comment = Comment(
            blog_post_title=data['blog_post_title'],
            author=data['author'],
            text=data['text']
        )
        comment.save()
        return comment
