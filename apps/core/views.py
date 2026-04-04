from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from apps.core.models import Testimonial


def health_check(request):
    """Health check endpoint for Railway."""
    return JsonResponse({'status': 'healthy', 'service': 'cr8tiveiq'})


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get active testimonials ordered by order field
        context['testimonials'] = Testimonial.objects.filter(is_active=True)[:6]
        return context


class AboutView(TemplateView):
    """About page view."""
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
