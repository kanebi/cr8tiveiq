from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import json
from .models import AnalyticsEvent
from .utils import track_event


@method_decorator(staff_member_required, name='dispatch')
class AnalyticsDashboardView(TemplateView):
    """Analytics dashboard view (admin only)."""
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Total events
        context['total_events'] = AnalyticsEvent.objects.count()
        
        # Unique sessions
        context['unique_sessions'] = AnalyticsEvent.objects.values('user_session_id').distinct().count()
        
        # Event breakdown by type
        event_breakdown = AnalyticsEvent.objects.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')
        context['event_breakdown'] = event_breakdown
        
        # Recent events (last 10)
        context['recent_events'] = AnalyticsEvent.objects.all()[:10]
        
        # Events by type (for display)
        event_types = dict(AnalyticsEvent.EVENT_TYPE_CHOICES)
        context['event_types'] = event_types
        
        # Events in last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        context['events_last_7_days'] = AnalyticsEvent.objects.filter(
            created_at__gte=seven_days_ago
        ).count()
        
        # Top pages
        context['top_pages'] = AnalyticsEvent.objects.filter(
            event_type='page_view'
        ).values('page_url').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return context


@csrf_exempt
@require_http_methods(["POST"])
def track_cta_click(request):
    """
    API endpoint to track CTA button clicks.
    
    Expected POST data:
    {
        "button_text": "Start Project",
        "button_url": "/contact/",
        "button_class": "btn-primary",
        "page_url": "/",
        "user_session_id": "session_id"
    }
    """
    try:
        data = json.loads(request.body)
        
        event_data = {
            'button_text': data.get('button_text', ''),
            'button_url': data.get('button_url', ''),
            'button_class': data.get('button_class', ''),
        }
        
        track_event(
            event_type='cta_click',
            page_url=data.get('page_url', ''),
            user_session_id=data.get('user_session_id', ''),
            event_data=event_data
        )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
