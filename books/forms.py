from django import forms
from .models import Book, Recommendation, Comment, CommentReply

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'cover_image', 'rating', 'genre', 'published_date']

class RecommendationForm(forms.ModelForm):
    class Meta:
        model = Recommendation
        fields = ['book']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }

class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = CommentReply
        fields = ['content']  # Adjust this field list as needed
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Write a reply...', 'rows': 2}),
        }