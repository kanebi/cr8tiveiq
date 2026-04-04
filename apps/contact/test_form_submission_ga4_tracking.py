"""
Tests for GA4 form submission tracking functionality.
Validates that form submissions are tracked with proper GA4 parameters.
"""

from django.test import TestCase, Client
from django.urls import reverse
from apps.analytics.models import AnalyticsEvent
from .models import ContactInquiry


class FormSubmissionGA4TrackingTestCase(TestCase):
    """Test cases for GA4 form submission tracking."""

    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.contact_url = reverse('contact:form')

    def test_form_submission_tracks_form_name(self):
        """Test that form submission event includes form_name parameter."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        event = AnalyticsEvent.objects.filter(event_type='form_submit').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_data.get('form_name'), 'contact_form')

    def test_form_submission_tracks_form_id(self):
        """Test that form submission event includes form_id parameter."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        event = AnalyticsEvent.objects.filter(event_type='form_submit').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_data.get('form_id'), 'contact-form')

    def test_form_submission_tracks_field_count(self):
        """Test that form submission event includes field_count parameter."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        event = AnalyticsEvent.objects.filter(event_type='form_submit').first()
        self.assertIsNotNone(event)
        field_count = event.event_data.get('field_count')
        self.assertIsNotNone(field_count)
        # Contact form has 6 fields: name, email, phone, company, service_type, project_description
        self.assertEqual(field_count, 6)

    def test_form_submission_ga4_parameters_complete(self):
        """Test that form submission event has all GA4 parameters."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        event = AnalyticsEvent.objects.filter(event_type='form_submit').first()
        self.assertIsNotNone(event)
        
        # Verify all GA4 parameters are present
        ga4_params = ['form_name', 'form_id', 'field_count']
        for param in ga4_params:
            self.assertIn(param, event.event_data)
            self.assertIsNotNone(event.event_data.get(param))

    def test_form_submission_event_type_is_form_submit(self):
        """Test that form submission creates event with type 'form_submit'."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        event = AnalyticsEvent.objects.filter(event_type='form_submit').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, 'form_submit')

    def test_form_submission_stores_in_database(self):
        """Test that form submission is stored in analytics database."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        # Verify event is stored in database
        events = AnalyticsEvent.objects.filter(event_type='form_submit')
        self.assertEqual(events.count(), 1)
        
        event = events.first()
        self.assertIsNotNone(event.created_at)
        self.assertIsNotNone(event.page_url)

    def test_form_submission_with_all_fields_filled(self):
        """Test form submission tracking with all fields filled."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '+1 (555) 123-4567',
            'company': 'Acme Corp',
            'project_description': 'We need a complete website redesign with e-commerce functionality',
            'service_type': 'Website Development',
        })
        
        event = AnalyticsEvent.objects.filter(event_type='form_submit').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_data.get('form_name'), 'contact_form')
        self.assertEqual(event.event_data.get('form_id'), 'contact-form')
        self.assertEqual(event.event_data.get('field_count'), 6)

    def test_form_submission_with_minimal_fields(self):
        """Test form submission tracking with only required fields."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '',  # Optional
            'company': '',  # Optional
            'project_description': 'Test project',
            'service_type': '',  # Optional
        })
        
        event = AnalyticsEvent.objects.filter(event_type='form_submit').first()
        self.assertIsNotNone(event)
        # Field count should still be 6 (all form fields)
        self.assertEqual(event.event_data.get('field_count'), 6)

    def test_form_submission_creates_contact_inquiry_and_event(self):
        """Test that form submission creates both inquiry and analytics event."""
        AnalyticsEvent.objects.all().delete()
        ContactInquiry.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        # Verify both inquiry and event are created
        inquiry = ContactInquiry.objects.first()
        event = AnalyticsEvent.objects.filter(event_type='form_submit').first()
        
        self.assertIsNotNone(inquiry)
        self.assertIsNotNone(event)
        
        # Verify event references the inquiry
        self.assertEqual(event.event_data.get('inquiry_id'), inquiry.id)

    def test_form_submission_event_has_page_url(self):
        """Test that form submission event includes page URL."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        event = AnalyticsEvent.objects.filter(event_type='form_submit').first()
        self.assertIsNotNone(event.page_url)
        self.assertIn('/contact/', event.page_url)

    def test_form_submission_event_has_session_id(self):
        """Test that form submission event includes session ID."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        event = AnalyticsEvent.objects.filter(event_type='form_submit').first()
        self.assertIsNotNone(event.user_session_id)
