from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Service


class ServiceListView(ListView):
    """Services list view."""
    model = Service
    template_name = 'services/services_list.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        return Service.objects.all().order_by('order', 'title')


class ServiceDetailView(DetailView):
    """Service detail view."""
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all services for sidebar
        context['services'] = Service.objects.all().order_by('order', 'title')
        return context
