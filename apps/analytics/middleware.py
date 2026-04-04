"""Analytics middleware for tracking page views."""

import uuid
from django.utils.deprecation import MiddlewareMixin
from .utils import track_event


class AnalyticsMiddleware(MiddlewareMixin):
    """Middleware to track page views and user sessions."""

    def process_request(self, request):
        """Track page view on request."""
        # Generate or retrieve session ID
        if 'analytics_session_id' not in request.session:
            request.session['analytics_session_id'] = str(uuid.uuid4())
        
        # Store session ID in request for later use
        request.analytics_session_id = request.session['analytics_session_id']
        
        return None

    def process_response(self, request, response):
        """Track page view on response."""
        # Only track successful page views (status 200)
        if response.status_code == 200:
            # Skip tracking for admin pages, static files, and media
            path = request.path
            if not any(path.startswith(prefix) for prefix in ['/admin/', '/static/', '/media/']):
                # Track page view
                track_event(
                    event_type='page_view',
                    page_url=request.path,
                    user_session_id=getattr(request, 'analytics_session_id', None),
                    event_data={
                        'page_title': request.META.get('HTTP_REFERER', ''),
                        'page_location': request.build_absolute_uri(),
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'referrer': request.META.get('HTTP_REFERER', ''),
                    }
                )
        
        return response
