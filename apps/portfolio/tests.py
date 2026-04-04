"""Tests for portfolio app."""

import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import PortfolioProject
from apps.analytics.models import AnalyticsEvent


class PortfolioViewTrackingTest(TestCase):
    """Test portfolio view tracking."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.project = PortfolioProject.objects.create(
            title='Test Project',
            slug='test-project',
            client_name='Test Client',
            category='graphics',
            description='Test description',
            featured_image='test.jpg',
        )

    def test_portfolio_click_tracking_api(self):
        """Test portfolio click tracking API endpoint."""
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        # Send tracking request
        response = self.client.post(
            reverse('portfolio:track_click'),
            data=json.dumps({
                'portfolio_id': self.project.id,
                'portfolio_title': self.project.title,
                'portfolio_category': 'Graphics',
            }),
            content_type='application/json'
        )
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
        # Check that portfolio view event was tracked
        events = AnalyticsEvent.objects.filter(event_type='portfolio_view')
        self.assertEqual(events.count(), 1)
        
        # Verify event data
        event = events.first()
        self.assertEqual(event.event_data['portfolio_id'], self.project.id)
        self.assertEqual(event.event_data['portfolio_title'], self.project.title)
        self.assertEqual(event.event_data['portfolio_category'], 'Graphics')

    def test_portfolio_click_tracking_api_invalid_json(self):
        """Test portfolio click tracking API with invalid JSON."""
        # Send invalid JSON
        response = self.client.post(
            reverse('portfolio:track_click'),
            data='invalid json',
            content_type='application/json'
        )
        
        # Check response is error
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')

    def test_portfolio_view_tracking_includes_session_id(self):
        """Test that portfolio view tracking includes session ID."""
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        # Send tracking request
        self.client.post(
            reverse('portfolio:track_click'),
            data=json.dumps({
                'portfolio_id': self.project.id,
                'portfolio_title': self.project.title,
                'portfolio_category': 'Graphics',
            }),
            content_type='application/json'
        )
        
        # Check that portfolio view event was tracked with session ID
        events = AnalyticsEvent.objects.filter(event_type='portfolio_view')
        self.assertEqual(events.count(), 1)
        
        event = events.first()
        # Session ID should be set (either from session or IP address)
        self.assertIsNotNone(event.user_session_id)
        self.assertTrue(len(event.user_session_id) > 0)

    def test_multiple_portfolio_views_tracked(self):
        """Test that multiple portfolio views are tracked separately."""
        # Create another project
        project2 = PortfolioProject.objects.create(
            title='Test Project 2',
            slug='test-project-2',
            client_name='Test Client 2',
            category='video',
            description='Test description 2',
            featured_image='test2.jpg',
        )
        
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        # Send tracking request for first project
        self.client.post(
            reverse('portfolio:track_click'),
            data=json.dumps({
                'portfolio_id': self.project.id,
                'portfolio_title': self.project.title,
                'portfolio_category': 'Graphics',
            }),
            content_type='application/json'
        )
        
        # Send tracking request for second project
        self.client.post(
            reverse('portfolio:track_click'),
            data=json.dumps({
                'portfolio_id': project2.id,
                'portfolio_title': project2.title,
                'portfolio_category': 'Video',
            }),
            content_type='application/json'
        )
        
        # Check that both portfolio views were tracked
        events = AnalyticsEvent.objects.filter(event_type='portfolio_view')
        self.assertEqual(events.count(), 2)
        
        # Verify each event has correct data
        event_ids = [e.event_data['portfolio_id'] for e in events]
        self.assertIn(self.project.id, event_ids)
        self.assertIn(project2.id, event_ids)
