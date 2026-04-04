from django.contrib import admin
from .models import BlogArticle


@admin.register(BlogArticle)
class BlogArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'published_at')
    list_filter = ('is_published', 'category', 'published_at', 'created_at')
    search_fields = ('title', 'summary', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('summary', 'content', 'featured_image'),
            'description': 'Use summary for card displays. Content supports rich text formatting.'
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at')
        }),
        ('Tags', {
            'fields': ('tags',)
        }),
    )
