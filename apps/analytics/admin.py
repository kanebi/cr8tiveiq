from django.contrib import admin
from .models import AnalyticsEvent


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'page_url', 'user_session_id', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('page_url', 'user_session_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Event Information', {
            'fields': ('event_type', 'page_url', 'user_session_id')
        }),
        ('Event Data', {
            'fields': ('event_data',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
