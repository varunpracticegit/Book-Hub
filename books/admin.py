from django.contrib import admin
from .models import Book, Recommendation, Comment, Like, CommentLike, CommentReply

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'rating', 'genre', 'published_date')
    search_fields = ('title', 'author', 'genre')
    list_filter = ('genre', 'published_date')

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'recommended_at')
    search_fields = ('user__username', 'book__title')
    list_filter = ('recommended_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at', 'content_preview')
    search_fields = ('user__username', 'book__title', 'content')
    list_filter = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50]  # Display only the first 50 characters of the comment
    content_preview.short_description = 'Content Preview'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at')
    search_fields = ('user__username', 'book__title')
    list_filter = ('created_at',)

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at')
    search_fields = ('user__username', 'comment__content')
    list_filter = ('created_at',)

@admin.register(CommentReply)
class CommentReplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at', 'content_preview')
    search_fields = ('user__username', 'comment__content', 'content')
    list_filter = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50]  # Display only the first 50 characters of the reply
    content_preview.short_description = 'Content Preview'
