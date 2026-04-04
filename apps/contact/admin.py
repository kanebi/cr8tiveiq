from django.contrib import admin
from .models import ContactInquiry, NewsletterSubscriber


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'company', 'project_description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Inquiry Details', {
            'fields': ('project_description', 'service_type')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at', 'updated_at')
