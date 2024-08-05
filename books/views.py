import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Book
from rest_framework import generics
from .models import *
from .serializers import BookSerializer, RecommendationSerializer, CommentSerializer
from book_hub import settings
import requests
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from books.forms import BookForm, RecommendationForm, CommentForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import status
from .forms import *


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    return render(request, 'books/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful")
            return redirect('index')
        else:
            messages.error(request, "Registration failed. Please try again.")
    else:
        form = UserCreationForm()
    return render(request, 'books/register.html', {'form': form})

@login_required
def index(request):
    return render(request, 'books/index.html')
def book_list_create_view(request):
    if request.method == 'POST':
        if 'add_book' in request.POST:
            form = BookForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('book-list-create')
        elif 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                book_id = request.POST.get('book_id')
                book = get_object_or_404(Book, id=book_id)
                comment = comment_form.save(commit=False)
                comment.book = book
                comment.user = request.user
                comment.save()
                return redirect('book-list-create')
        elif 'like_book' in request.POST:
            book_id = request.POST.get('book_id')
            book = get_object_or_404(Book, id=book_id)
            Like.objects.get_or_create(book=book, user=request.user)
            return redirect('book-list-create')
        elif 'like_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id)
            CommentLike.objects.get_or_create(comment=comment, user=request.user)
            return redirect('book-list-create')
        elif 'reply_comment' in request.POST:
            reply_form = CommentReplyForm(request.POST)
            if reply_form.is_valid():
                comment_id = request.POST.get('comment_id')
                comment = get_object_or_404(Comment, id=comment_id)
                reply = reply_form.save(commit=False)
                reply.comment = comment
                reply.user = request.user
                reply.save()
                return redirect('book-list-create')
    else:
        form = BookForm()
        comment_form = CommentForm()
        reply_form = CommentReplyForm()

    books = Book.objects.all()
    book_comment_dict = {}
    comment_reply_dict = {}

    for book in books:
        book_comments = Comment.objects.filter(book=book)
        book_comment_dict[book.id] = book_comments
        for comment in book_comments:
            replies = CommentReply.objects.filter(comment=comment)
            comment_reply_dict[comment.id] = replies

    return render(request, 'books/book_list.html', {
        'books': books,
        'form': form,
        'comment_form': comment_form,
        'reply_form': reply_form,
        'book_comment_dict': book_comment_dict,
        'comment_reply_dict': comment_reply_dict,
    })




@login_required
def recommendation_list_create_view(request):
    # Get filter and sort criteria from request
    genre = request.GET.get('genre')
    rating = request.GET.get('rating')
    published_date = request.GET.get('published_date')
    sort_by = request.GET.get('sort_by')
    
    # Filter recommendations based on criteria
    recommendations = Recommendation.objects.all()
    
    if genre:
        recommendations = recommendations.filter(book__genre__icontains=genre)
    
    if rating:
        recommendations = recommendations.filter(book__rating__gte=rating)
    
    if published_date:
        recommendations = recommendations.filter(book__published_date__gte=published_date)
    
    # Sorting the recommendations
    if sort_by:
        recommendations = recommendations.order_by(sort_by)
    else:
        recommendations = recommendations.order_by('-recommended_at')  # Default sorting

    # Handle form submission for adding new recommendations
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            recommendation = form.save(commit=False)
            recommendation.user = request.user
            recommendation.save()
            return redirect('recommendation-list-create')
    else:
        form = RecommendationForm()

    return render(request, 'books/recommendation_list.html', {'recommendations': recommendations, 'form': form})

@login_required
def comment_list_create_view(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            return redirect('comment-list-create')
    else:
        form = CommentForm()

    comments = Comment.objects.all()
    return render(request, 'books/comment_list.html', {'comments': comments, 'form': form})

class BookSearchView(generics.GenericAPIView):
    serializer_class = BookSerializer

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q')
        response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}&key={settings.GOOGLE_BOOKS_API_KEY}")
        books = response.json().get('items', [])
        data = []
        for book in books:
            data.append({
                'id': book['id'],
                'title': book['volumeInfo'].get('title'),
                'author': ', '.join(book['volumeInfo'].get('authors', [])),
                'description': book['volumeInfo'].get('description'),
                'cover_image': book['volumeInfo'].get('imageLinks', {}).get('thumbnail'),
                'rating': book['volumeInfo'].get('averageRating'),
                'genre': ', '.join(book['volumeInfo'].get('categories', [])),
                'published_date': book['volumeInfo'].get('publishedDate'),
            })
        print(data)
        return Response(data)

def save_book(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        author = data.get('author')
        description = data.get('description')
        cover_image = data.get('cover_image')
        rating = data.get('rating')
        genre = data.get('genre')
        published_date = data.get('published_date')

        # Set a default rating if it is None
        if rating is None:
            rating = 0

        if not Book.objects.filter(title=title).exists():
            print("True")
            Book.objects.create(
                title=title,
                author=author,
                description=description,
                cover_image=cover_image,
                rating=rating,
                genre=genre,
                published_date=published_date,
            )
            return redirect('book-list-create')
        else:
            return JsonResponse({"message": "Book already exists!"}, status=400)

    return JsonResponse({"message": "Invalid request method."}, status=405)
