"""Tests for analytics app."""

from django.test import TestCase, Client
from django.urls import reverse
from .models import AnalyticsEvent
from .utils import track_event
import json


class AnalyticsEventModelTest(TestCase):
    """Test AnalyticsEvent model."""

    def test_create_page_view_event(self):
        """Test creating a page view event."""
        event = AnalyticsEvent.objects.create(
            event_type='page_view',
            page_url='/portfolio/',
            user_session_id='test-session-123',
            event_data={
                'page_title': 'Portfolio',
                'page_location': 'http://localhost:8000/portfolio/',
            }
        )
        self.assertEqual(event.event_type, 'page_view')
        self.assertEqual(event.page_url, '/portfolio/')
        self.assertEqual(event.user_session_id, 'test-session-123')
        self.assertIn('page_title', event.event_data)

    def test_track_event_utility(self):
        """Test track_event utility function."""
        track_event(
            event_type='page_view',
            page_url='/services/',
            user_session_id='test-session-456',
            event_data={'page_title': 'Services'}
        )
        event = AnalyticsEvent.objects.get(page_url='/services/')
        self.assertEqual(event.event_type, 'page_view')
        self.assertEqual(event.page_url, '/services/')

    def test_event_ordering(self):
        """Test that events are ordered by created_at descending."""
        event1 = AnalyticsEvent.objects.create(
            event_type='page_view',
            page_url='/page1/'
        )
        event2 = AnalyticsEvent.objects.create(
            event_type='page_view',
            page_url='/page2/'
        )
        events = AnalyticsEvent.objects.all()
        self.assertEqual(events[0].id, event2.id)
        self.assertEqual(events[1].id, event1.id)


class CtaClickTrackingTest(TestCase):
    """Test CTA click tracking endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.track_cta_url = reverse('analytics:track_cta_click')

    def test_track_cta_click_success(self):
        """Test successful CTA click tracking."""
        data = {
            'button_text': 'Start Project',
            'button_url': '/contact/',
            'button_class': 'btn-primary',
            'page_url': '/',
            'user_session_id': 'test-session-123',
        }
        
        response = self.client.post(
            self.track_cta_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        # Verify event was created
        event = AnalyticsEvent.objects.get(event_type='cta_click')
        self.assertEqual(event.page_url, '/')
        self.assertEqual(event.user_session_id, 'test-session-123')
        self.assertEqual(event.event_data['button_text'], 'Start Project')
        self.assertEqual(event.event_data['button_url'], '/contact/')
        self.assertEqual(event.event_data['button_class'], 'btn-primary')

    def test_track_cta_click_with_secondary_button(self):
        """Test CTA click tracking for secondary button."""
        data = {
            'button_text': 'View Work',
            'button_url': '/portfolio/',
            'button_class': 'btn-secondary',
            'page_url': '/',
            'user_session_id': 'test-session-456',
        }
        
        response = self.client.post(
            self.track_cta_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        event = AnalyticsEvent.objects.get(event_type='cta_click')
        self.assertEqual(event.event_data['button_text'], 'View Work')
        self.assertEqual(event.event_data['button_class'], 'btn-secondary')

    def test_track_cta_click_multiple_buttons(self):
        """Test tracking multiple CTA clicks."""
        data1 = {
            'button_text': 'Start Project',
            'button_url': '/contact/',
            'button_class': 'btn-primary',
            'page_url': '/',
            'user_session_id': 'test-session-123',
        }
        
        data2 = {
            'button_text': 'Get in Touch',
            'button_url': '/contact/',
            'button_class': 'btn-primary',
            'page_url': '/services/',
            'user_session_id': 'test-session-123',
        }
        
        self.client.post(
            self.track_cta_url,
            data=json.dumps(data1),
            content_type='application/json'
        )
        
        self.client.post(
            self.track_cta_url,
            data=json.dumps(data2),
            content_type='application/json'
        )
        
        # Verify both events were created
        events = AnalyticsEvent.objects.filter(event_type='cta_click')
        self.assertEqual(events.count(), 2)
        
        # Verify session ID is the same
        session_ids = set(e.user_session_id for e in events)
        self.assertEqual(len(session_ids), 1)

    def test_track_cta_click_with_missing_fields(self):
        """Test CTA click tracking with missing optional fields."""
        data = {
            'button_text': 'Click Me',
            'page_url': '/',
            'user_session_id': 'test-session-789',
        }
        
        response = self.client.post(
            self.track_cta_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        event = AnalyticsEvent.objects.get(event_type='cta_click')
        self.assertEqual(event.event_data['button_text'], 'Click Me')
        self.assertEqual(event.event_data['button_url'], '')
        self.assertEqual(event.event_data['button_class'], '')

    def test_track_cta_click_invalid_json(self):
        """Test CTA click tracking with invalid JSON."""
        response = self.client.post(
            self.track_cta_url,
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')


class AnalyticsMiddlewareTest(TestCase):
    """Test analytics middleware for page view tracking."""

    def test_middleware_creates_session_id(self):
        """Test that middleware creates a session ID for tracking."""
        from django.test import RequestFactory
        from apps.analytics.middleware import AnalyticsMiddleware
        
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {}
        
        middleware = AnalyticsMiddleware(lambda r: None)
        middleware.process_request(request)
        
        # Check that session ID was created
        self.assertIn('analytics_session_id', request.session)
        self.assertIsNotNone(request.analytics_session_id)

    def test_middleware_tracks_page_view_on_success(self):
        """Test that middleware tracks page view on successful response."""
        from django.test import RequestFactory
        from django.http import HttpResponse
        from apps.analytics.middleware import AnalyticsMiddleware
        
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {'analytics_session_id': 'test-session-123'}
        request.META['HTTP_USER_AGENT'] = 'Test Browser'
        
        response = HttpResponse(status=200)
        
        middleware = AnalyticsMiddleware(lambda r: response)
        middleware.process_request(request)
        middleware.process_response(request, response)
        
        # Check that page view was tracked
        page_views = AnalyticsEvent.objects.filter(
            event_type='page_view',
            page_url='/'
        )
        self.assertEqual(page_views.count(), 1)

    def test_middleware_skips_admin_pages(self):
        """Test that middleware skips tracking for admin pages."""
        from django.test import RequestFactory
        from django.http import HttpResponse
        from apps.analytics.middleware import AnalyticsMiddleware
        
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        factory = RequestFactory()
        request = factory.get('/admin/')
        request.session = {'analytics_session_id': 'test-session-123'}
        
        response = HttpResponse(status=200)
        
        middleware = AnalyticsMiddleware(lambda r: response)
        middleware.process_request(request)
        middleware.process_response(request, response)
        
        # Check that no page view was tracked for admin
        admin_views = AnalyticsEvent.objects.filter(page_url__startswith='/admin/')
        self.assertEqual(admin_views.count(), 0)

    def test_middleware_skips_static_files(self):
        """Test that middleware skips tracking for static files."""
        from django.test import RequestFactory
        from django.http import HttpResponse
        from apps.analytics.middleware import AnalyticsMiddleware
        
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        factory = RequestFactory()
        request = factory.get('/static/css/main.css')
        request.session = {'analytics_session_id': 'test-session-123'}
        
        response = HttpResponse(status=200)
        
        middleware = AnalyticsMiddleware(lambda r: response)
        middleware.process_request(request)
        middleware.process_response(request, response)
        
        # Check that no page view was tracked for static files
        static_views = AnalyticsEvent.objects.filter(page_url__startswith='/static/')
        self.assertEqual(static_views.count(), 0)

    def test_middleware_skips_non_200_responses(self):
        """Test that middleware skips tracking for non-200 responses."""
        from django.test import RequestFactory
        from django.http import HttpResponse
        from apps.analytics.middleware import AnalyticsMiddleware
        
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        factory = RequestFactory()
        request = factory.get('/nonexistent/')
        request.session = {'analytics_session_id': 'test-session-123'}
        
        response = HttpResponse(status=404)
        
        middleware = AnalyticsMiddleware(lambda r: response)
        middleware.process_request(request)
        middleware.process_response(request, response)
        
        # Check that no page view was tracked for 404
        page_views = AnalyticsEvent.objects.filter(page_url='/nonexistent/')
        self.assertEqual(page_views.count(), 0)



class AnalyticsDashboardViewTest(TestCase):
    """Test analytics dashboard view."""

    def setUp(self):
        """Set up test client and create test data."""
        self.client = Client()
        self.dashboard_url = reverse('analytics:dashboard')
        
        # Create test events
        AnalyticsEvent.objects.create(
            event_type='page_view',
            page_url='/',
            user_session_id='session-1'
        )
        AnalyticsEvent.objects.create(
            event_type='page_view',
            page_url='/portfolio/',
            user_session_id='session-2'
        )
        AnalyticsEvent.objects.create(
            event_type='cta_click',
            page_url='/',
            user_session_id='session-1',
            event_data={'button_text': 'Start Project'}
        )

    def test_dashboard_requires_staff_login(self):
        """Test that dashboard requires staff member login."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_dashboard_view_context_data(self):
        """Test that dashboard view provides correct context data."""
        from django.contrib.auth.models import User
        from apps.analytics.views import AnalyticsDashboardView
        from django.test import RequestFactory
        
        # Create a staff user
        staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )
        
        # Create a request
        factory = RequestFactory()
        request = factory.get('/analytics/dashboard/')
        request.user = staff_user
        
        # Create view and get context
        view = AnalyticsDashboardView()
        view.request = request
        context = view.get_context_data()
        
        # Verify context data
        self.assertEqual(context['total_events'], 3)
        self.assertEqual(context['unique_sessions'], 2)
        self.assertEqual(context['events_last_7_days'], 3)
        self.assertIn('event_breakdown', context)
        self.assertIn('recent_events', context)
        self.assertIn('top_pages', context)
        self.assertIn('event_types', context)
        
        # Verify event breakdown
        event_breakdown = context['event_breakdown']
        self.assertEqual(len(event_breakdown), 2)
        
        # Verify top pages
        top_pages = context['top_pages']
        self.assertGreater(len(top_pages), 0)
        
        # Verify event types
        event_types = context['event_types']
        self.assertIn('page_view', event_types)
        self.assertIn('cta_click', event_types)
