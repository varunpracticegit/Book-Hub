from django.urls import path
from .views import book_list_create_view, recommendation_list_create_view,save_book, comment_list_create_view, index, BookSearchView, login_view, logout_view, register_view

urlpatterns = [
    path('', login_view, name='login'),
    path('home/', index, name='index'),
    path('books/', book_list_create_view, name='book-list-create'),
    path('recommendations/', recommendation_list_create_view, name='recommendation-list-create'),
    path('comments/', comment_list_create_view, name='comment-list-create'),
    path('search/', BookSearchView.as_view(), name='book-search'),
    path('save-book/', save_book, name='save-book'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
]
