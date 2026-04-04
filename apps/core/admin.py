from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Testimonial

# The default Django User model is used for admin/staff user management.
# No custom UserProfile extension is needed for CR8TIVEIQ.
# See apps/core/models.py for detailed rationale.

# Ensure User model is registered with default admin interface
if not admin.site.is_registered(User):
    admin.site.register(User, BaseUserAdmin)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'company', 'rating', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'rating', 'created_at')
    search_fields = ('client_name', 'company', 'testimonial_text')
    ordering = ('order', '-created_at')
    fieldsets = (
        ('Client Information', {
            'fields': ('client_name', 'company', 'role', 'photo')
        }),
        ('Testimonial Content', {
            'fields': ('testimonial_text', 'rating')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
