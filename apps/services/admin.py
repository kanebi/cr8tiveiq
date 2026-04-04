from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order')
    list_filter = ('created_at',)
    search_fields = ('title', 'short_description', 'description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'icon')
        }),
        ('Content', {
            'fields': ('description',)
        }),
        ('Settings', {
            'fields': ('order',)
        }),
    )
