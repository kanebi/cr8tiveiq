from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import PortfolioProject
from apps.analytics.utils import track_event


class PortfolioListView(ListView):
    """Portfolio list view."""
    model = PortfolioProject
    template_name = 'portfolio/portfolio_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        queryset = PortfolioProject.objects.all()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PortfolioProject.CATEGORY_CHOICES
        return context


class PortfolioDetailView(DetailView):
    """Portfolio detail view."""
    model = PortfolioProject
    template_name = 'portfolio/portfolio_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context['previous_project'] = PortfolioProject.objects.filter(
            order__lt=project.order
        ).first()
        context['next_project'] = PortfolioProject.objects.filter(
            order__gt=project.order
        ).first()
        return context

    def get(self, request, *args, **kwargs):
        """Track portfolio view in database."""
        response = super().get(request, *args, **kwargs)
        project = self.get_object()
        
        # Get session ID from request
        session_id = request.session.session_key or request.META.get('REMOTE_ADDR', '')
        
        # Track portfolio view event
        track_event(
            event_type='portfolio_view',
            page_url=request.path,
            user_session_id=session_id,
            event_data={
                'portfolio_id': project.id,
                'portfolio_title': project.title,
                'portfolio_category': project.get_category_display(),
                'client_name': project.client_name,
            }
        )
        
        return response


@require_http_methods(["POST"])
@csrf_exempt
def track_portfolio_click(request):
    """API endpoint to track portfolio item clicks."""
    import json
    
    try:
        data = json.loads(request.body)
        portfolio_id = data.get('portfolio_id')
        portfolio_title = data.get('portfolio_title')
        portfolio_category = data.get('portfolio_category')
        
        # Get session ID from request
        session_id = request.session.session_key or request.META.get('REMOTE_ADDR', '')
        
        # Track portfolio view event
        track_event(
            event_type='portfolio_view',
            page_url=request.META.get('HTTP_REFERER', ''),
            user_session_id=session_id,
            event_data={
                'portfolio_id': portfolio_id,
                'portfolio_title': portfolio_title,
                'portfolio_category': portfolio_category,
            }
        )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
