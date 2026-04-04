"""
Context processors for services app.
"""

from .models import Service


def services_menu(request):
    """Add services to template context for navigation menu."""
    return {
        'header_services': Service.objects.all().order_by('order', 'title')[:6]
    }
