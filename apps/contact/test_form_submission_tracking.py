"""
Tests for form submission tracking functionality.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from apps.analytics.models import AnalyticsEvent
from .models import ContactInquiry
from .views import ContactView


class FormSubmissionTrackingTestCase(TestCase):
    """Test cases for form submission tracking."""

    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.factory = RequestFactory()
        self.contact_url = reverse('contact:form')

    def test_form_submission_creates_analytics_event(self):
        """Test that form submission creates an analytics event."""
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        # Submit contact form
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        # Verify analytics event was created
        events = AnalyticsEvent.objects.filter(event_type='form_submit')
        self.assertEqual(events.count(), 1)
        
        event = events.first()
        self.assertEqual(event.event_type, 'form_submit')
        self.assertIsNotNone(event.event_data)

    def test_form_submission_event_contains_form_name(self):
        """Test that form submission event contains form name."""
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
        self.assertEqual(event.event_data.get('form_name'), 'contact_form')

    def test_form_submission_event_contains_form_id(self):
        """Test that form submission event contains form ID."""
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
        self.assertEqual(event.event_data.get('form_id'), 'contact-form')

    def test_form_submission_event_contains_field_count(self):
        """Test that form submission event contains field count."""
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
        field_count = event.event_data.get('field_count')
        self.assertIsNotNone(field_count)
        self.assertGreater(field_count, 0)

    def test_form_submission_event_contains_inquiry_id(self):
        """Test that form submission event contains inquiry ID."""
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
        inquiry_id = event.event_data.get('inquiry_id')
        self.assertIsNotNone(inquiry_id)
        
        # Verify inquiry exists
        inquiry = ContactInquiry.objects.get(id=inquiry_id)
        self.assertEqual(inquiry.name, 'John Doe')

    def test_form_submission_event_contains_service_type(self):
        """Test that form submission event contains service type."""
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
        self.assertEqual(event.event_data.get('service_type'), 'Web Development')

    def test_form_submission_event_contains_page_url(self):
        """Test that form submission event contains page URL."""
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

    def test_form_submission_event_contains_session_id(self):
        """Test that form submission event contains session ID."""
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

    def test_invalid_form_submission_does_not_create_event(self):
        """Test that invalid form submission does not create analytics event."""
        AnalyticsEvent.objects.all().delete()
        
        # Submit form with missing required fields
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            # Missing email (required)
            'phone': '1234567890',
        })
        
        # Verify no analytics event was created
        events = AnalyticsEvent.objects.filter(event_type='form_submit')
        self.assertEqual(events.count(), 0)

    def test_multiple_form_submissions_create_multiple_events(self):
        """Test that multiple form submissions create multiple events."""
        AnalyticsEvent.objects.all().delete()
        
        # Submit form twice
        for i in range(2):
            response = self.client.post(self.contact_url, {
                'name': f'John Doe {i}',
                'email': f'john{i}@example.com',
                'phone': '1234567890',
                'company': 'Test Company',
                'project_description': 'Test project',
                'service_type': 'Web Development',
            })
        
        # Verify two analytics events were created
        events = AnalyticsEvent.objects.filter(event_type='form_submit')
        self.assertEqual(events.count(), 2)

    def test_form_submission_event_data_is_json(self):
        """Test that form submission event data is stored as JSON."""
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
        # Verify event_data is a dict (JSON field)
        self.assertIsInstance(event.event_data, dict)

    def test_form_submission_creates_contact_inquiry(self):
        """Test that form submission creates a contact inquiry."""
        ContactInquiry.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        # Verify contact inquiry was created
        inquiries = ContactInquiry.objects.all()
        self.assertEqual(inquiries.count(), 1)
        
        inquiry = inquiries.first()
        self.assertEqual(inquiry.name, 'John Doe')
        self.assertEqual(inquiry.email, 'john@example.com')

    def test_form_submission_redirects_to_success_page(self):
        """Test that form submission redirects to success page."""
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        }, follow=True)
        
        # Verify redirect to success page
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.request['PATH_INFO'])

    def test_form_submission_with_empty_phone(self):
        """Test form submission with empty phone field."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '',  # Empty phone
            'company': 'Test Company',
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        # Verify analytics event was created (phone is optional)
        events = AnalyticsEvent.objects.filter(event_type='form_submit')
        self.assertEqual(events.count(), 1)

    def test_form_submission_with_empty_company(self):
        """Test form submission with empty company field."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'company': '',  # Empty company
            'project_description': 'Test project',
            'service_type': 'Web Development',
        })
        
        # Verify analytics event was created (company is optional)
        events = AnalyticsEvent.objects.filter(event_type='form_submit')
        self.assertEqual(events.count(), 1)

    def test_form_submission_event_ordering(self):
        """Test that form submission events are ordered by creation date."""
        AnalyticsEvent.objects.all().delete()
        
        # Submit form twice
        for i in range(2):
            response = self.client.post(self.contact_url, {
                'name': f'John Doe {i}',
                'email': f'john{i}@example.com',
                'phone': '1234567890',
                'company': 'Test Company',
                'project_description': 'Test project',
                'service_type': 'Web Development',
            })
        
        # Verify events are ordered by creation date (newest first)
        events = AnalyticsEvent.objects.filter(event_type='form_submit')
        self.assertEqual(events[0].created_at >= events[1].created_at, True)

    def test_form_submission_with_special_characters(self):
        """Test form submission with special characters in fields."""
        AnalyticsEvent.objects.all().delete()
        
        response = self.client.post(self.contact_url, {
            'name': 'John O\'Doe & Co.',
            'email': 'john+test@example.com',
            'phone': '+1 (234) 567-890',
            'company': 'Test & Co. <Ltd>',
            'project_description': 'Test project with "quotes" and \'apostrophes\'',
            'service_type': 'Web Development',
        })
        
        # Verify analytics event was created
        events = AnalyticsEvent.objects.filter(event_type='form_submit')
        self.assertEqual(events.count(), 1)
        
        # Verify inquiry was created with special characters
        inquiry = ContactInquiry.objects.first()
        self.assertEqual(inquiry.name, 'John O\'Doe & Co.')

    def test_form_submission_event_contains_all_required_fields(self):
        """Test that form submission event contains all required fields."""
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
        
        # Verify all required fields are present
        required_fields = ['form_name', 'form_id', 'field_count', 'inquiry_id', 'service_type']
        for field in required_fields:
            self.assertIn(field, event.event_data)
            self.assertIsNotNone(event.event_data.get(field))
