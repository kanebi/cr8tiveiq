from django.contrib import admin
from .models import PortfolioProject


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_name', 'category', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'client_name', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('services_used',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'client_name', 'category')
        }),
        ('Content', {
            'fields': ('description', 'featured_image', 'gallery_images', 'videos')
        }),
        ('Details', {
            'fields': ('services_used', 'timeline', 'results')
        }),
        ('Settings', {
            'fields': ('is_featured', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
