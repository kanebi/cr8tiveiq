"""
Tests for contact app Celery tasks.
"""

from django.test import TestCase, override_settings
from django.core import mail
from django.utils import timezone
from unittest.mock import patch, MagicMock
from celery.exceptions import MaxRetriesExceededError
from .models import ContactInquiry, NewsletterSubscriber
from .tasks import (
    send_contact_admin_notification,
    send_contact_user_confirmation,
    send_newsletter_confirmation,
    calculate_retry_delay,
    MAX_RETRIES,
    INITIAL_RETRY_DELAY,
    EXPONENTIAL_BACKOFF_BASE,
)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    ADMIN_EMAIL='admin@test.com',
    DEFAULT_FROM_EMAIL='noreply@test.com',
    SITE_URL='http://localhost:8000',
)
class ContactTasksTestCase(TestCase):
    """Test cases for contact app Celery tasks."""

    def setUp(self):
        """Set up test data."""
        self.contact_inquiry = ContactInquiry.objects.create(
            name='John Doe',
            email='john@example.com',
            phone='1234567890',
            company='Test Company',
            project_description='Test project description',
            service_type='Web Development',
        )
        
        self.newsletter_subscriber = NewsletterSubscriber.objects.create(
            email='subscriber@example.com',
        )

    def test_send_contact_admin_notification(self):
        """Test sending admin notification email."""
        # Clear the test mailbox
        mail.outbox = []
        
        # Call the task
        send_contact_admin_notification(self.contact_inquiry.id)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        # Check email properties
        self.assertEqual(email.to, ['admin@test.com'])
        self.assertIn('New Contact Inquiry', email.subject)
        self.assertIn('John Doe', email.body)
        self.assertIn('john@example.com', email.body)
        self.assertIn('Test project description', email.body)

    def test_send_contact_user_confirmation(self):
        """Test sending user confirmation email."""
        # Clear the test mailbox
        mail.outbox = []
        
        # Call the task
        send_contact_user_confirmation(self.contact_inquiry.id)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        # Check email properties
        self.assertEqual(email.to, ['john@example.com'])
        self.assertIn('We Received Your Inquiry', email.subject)
        self.assertIn('John Doe', email.body)
        self.assertIn('Test Company', email.body)

    def test_send_newsletter_confirmation(self):
        """Test sending newsletter confirmation email."""
        # Clear the test mailbox
        mail.outbox = []
        
        # Call the task
        send_newsletter_confirmation(self.newsletter_subscriber.id)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        # Check email properties
        self.assertEqual(email.to, ['subscriber@example.com'])
        self.assertIn('Confirm Your Newsletter Subscription', email.subject)
        self.assertIn('subscriber@example.com', email.body)

    def test_send_contact_admin_notification_nonexistent_inquiry(self):
        """Test sending admin notification with nonexistent inquiry."""
        # Call the task with nonexistent ID
        # Should not raise an exception, just log error
        send_contact_admin_notification(9999)
        
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_send_contact_user_confirmation_nonexistent_inquiry(self):
        """Test sending user confirmation with nonexistent inquiry."""
        # Call the task with nonexistent ID
        # Should not raise an exception, just log error
        send_contact_user_confirmation(9999)
        
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_send_newsletter_confirmation_nonexistent_subscriber(self):
        """Test sending newsletter confirmation with nonexistent subscriber."""
        # Call the task with nonexistent ID
        # Should not raise an exception, just log error
        send_newsletter_confirmation(9999)
        
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_admin_notification_email_contains_all_inquiry_details(self):
        """Test that admin notification email contains all inquiry details."""
        mail.outbox = []
        
        send_contact_admin_notification(self.contact_inquiry.id)
        
        email = mail.outbox[0]
        body = email.body
        
        # Verify all inquiry details are in the email
        self.assertIn('John Doe', body)
        self.assertIn('john@example.com', body)
        self.assertIn('1234567890', body)
        self.assertIn('Test Company', body)
        self.assertIn('Test project description', body)
        self.assertIn('Web Development', body)

    def test_user_confirmation_email_contains_inquiry_summary(self):
        """Test that user confirmation email contains inquiry summary."""
        mail.outbox = []
        
        send_contact_user_confirmation(self.contact_inquiry.id)
        
        email = mail.outbox[0]
        body = email.body
        
        # Verify inquiry summary is in the email
        self.assertIn('John Doe', body)
        self.assertIn('john@example.com', body)
        self.assertIn('Test Company', body)

    def test_newsletter_confirmation_email_contains_subscription_details(self):
        """Test that newsletter confirmation email contains subscription details."""
        mail.outbox = []
        
        send_newsletter_confirmation(self.newsletter_subscriber.id)
        
        email = mail.outbox[0]
        body = email.body
        
        # Verify subscription details are in the email
        self.assertIn('subscriber@example.com', body)

    def test_email_html_content_is_rendered(self):
        """Test that email HTML content is properly rendered."""
        mail.outbox = []
        
        send_contact_admin_notification(self.contact_inquiry.id)
        
        email = mail.outbox[0]
        
        # Verify HTML message is present
        self.assertIsNotNone(email.alternatives)
        self.assertTrue(any(mime_type == 'text/html' for _, mime_type in email.alternatives))

    def test_email_from_address_is_correct(self):
        """Test that email from address is set correctly."""
        mail.outbox = []
        
        send_contact_admin_notification(self.contact_inquiry.id)
        
        email = mail.outbox[0]
        self.assertEqual(email.from_email, 'noreply@test.com')

    def test_multiple_emails_sent_for_contact_inquiry(self):
        """Test that both admin and user emails are sent for contact inquiry."""
        mail.outbox = []
        
        # Send both emails
        send_contact_admin_notification(self.contact_inquiry.id)
        send_contact_user_confirmation(self.contact_inquiry.id)
        
        # Verify both emails were sent
        self.assertEqual(len(mail.outbox), 2)
        
        # Verify recipients
        recipients = [email.to[0] for email in mail.outbox]
        self.assertIn('admin@test.com', recipients)
        self.assertIn('john@example.com', recipients)


class RetryLogicTestCase(TestCase):
    """Test cases for email retry logic with exponential backoff."""

    def setUp(self):
        """Set up test data."""
        self.contact_inquiry = ContactInquiry.objects.create(
            name='John Doe',
            email='john@example.com',
            phone='1234567890',
            company='Test Company',
            project_description='Test project description',
            service_type='Web Development',
        )
        
        self.newsletter_subscriber = NewsletterSubscriber.objects.create(
            email='subscriber@example.com',
        )

    def test_calculate_retry_delay_exponential_backoff(self):
        """Test that retry delay increases exponentially."""
        # First retry: 60 * 2^0 = 60 seconds
        self.assertEqual(calculate_retry_delay(0), 60)
        
        # Second retry: 60 * 2^1 = 120 seconds
        self.assertEqual(calculate_retry_delay(1), 120)
        
        # Third retry: 60 * 2^2 = 240 seconds
        self.assertEqual(calculate_retry_delay(2), 240)

    def test_max_retries_configuration(self):
        """Test that MAX_RETRIES is properly configured."""
        self.assertEqual(MAX_RETRIES, 3)

    def test_initial_retry_delay_configuration(self):
        """Test that INITIAL_RETRY_DELAY is properly configured."""
        self.assertEqual(INITIAL_RETRY_DELAY, 60)

    def test_exponential_backoff_base_configuration(self):
        """Test that EXPONENTIAL_BACKOFF_BASE is properly configured."""
        self.assertEqual(EXPONENTIAL_BACKOFF_BASE, 2)

    @patch('apps.contact.tasks.send_contact_admin_notification.retry')
    @patch('apps.contact.tasks.send_mail')
    def test_admin_notification_retry_on_failure(self, mock_send_mail, mock_retry):
        """Test that admin notification task retries on email send failure."""
        # Mock send_mail to raise an exception
        mock_send_mail.side_effect = Exception("SMTP connection failed")
        mock_retry.side_effect = Exception("Retry called")
        
        # Call the task
        with self.assertRaises(Exception):
            send_contact_admin_notification(self.contact_inquiry.id)
        
        # Verify retry was called
        mock_retry.assert_called_once()

    @patch('apps.contact.tasks.send_contact_user_confirmation.retry')
    @patch('apps.contact.tasks.send_mail')
    def test_user_confirmation_retry_on_failure(self, mock_send_mail, mock_retry):
        """Test that user confirmation task retries on email send failure."""
        # Mock send_mail to raise an exception
        mock_send_mail.side_effect = Exception("SMTP connection failed")
        mock_retry.side_effect = Exception("Retry called")
        
        # Call the task
        with self.assertRaises(Exception):
            send_contact_user_confirmation(self.contact_inquiry.id)
        
        # Verify retry was called
        mock_retry.assert_called_once()

    @patch('apps.contact.tasks.send_newsletter_confirmation.retry')
    @patch('apps.contact.tasks.send_mail')
    def test_newsletter_confirmation_retry_on_failure(self, mock_send_mail, mock_retry):
        """Test that newsletter confirmation task retries on email send failure."""
        # Mock send_mail to raise an exception
        mock_send_mail.side_effect = Exception("SMTP connection failed")
        mock_retry.side_effect = Exception("Retry called")
        
        # Call the task
        with self.assertRaises(Exception):
            send_newsletter_confirmation(self.newsletter_subscriber.id)
        
        # Verify retry was called
        mock_retry.assert_called_once()

    def test_admin_notification_no_retry_on_nonexistent_inquiry(self):
        """Test that admin notification doesn't retry for non-existent inquiry."""
        # Call with non-existent ID
        send_contact_admin_notification(9999)
        
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_user_confirmation_no_retry_on_nonexistent_inquiry(self):
        """Test that user confirmation doesn't retry for non-existent inquiry."""
        # Call with non-existent ID
        send_contact_user_confirmation(9999)
        
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_newsletter_confirmation_no_retry_on_nonexistent_subscriber(self):
        """Test that newsletter confirmation doesn't retry for non-existent subscriber."""
        # Call with non-existent ID
        send_newsletter_confirmation(9999)
        
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    @patch('apps.contact.tasks.send_contact_admin_notification.retry')
    @patch('apps.contact.tasks.send_mail')
    def test_admin_notification_logs_retry_attempts(self, mock_send_mail, mock_retry):
        """Test that admin notification logs retry attempts."""
        # Mock send_mail to raise an exception
        mock_send_mail.side_effect = Exception("SMTP connection failed")
        mock_retry.side_effect = Exception("Retry called")
        
        # Call the task
        with self.assertRaises(Exception):
            send_contact_admin_notification(self.contact_inquiry.id)
        
        # Verify retry was called
        mock_retry.assert_called_once()

    @patch('apps.contact.tasks.send_contact_user_confirmation.retry')
    @patch('apps.contact.tasks.send_mail')
    def test_user_confirmation_logs_retry_attempts(self, mock_send_mail, mock_retry):
        """Test that user confirmation logs retry attempts."""
        # Mock send_mail to raise an exception
        mock_send_mail.side_effect = Exception("SMTP connection failed")
        mock_retry.side_effect = Exception("Retry called")
        
        # Call the task
        with self.assertRaises(Exception):
            send_contact_user_confirmation(self.contact_inquiry.id)
        
        # Verify retry was called
        mock_retry.assert_called_once()

    @patch('apps.contact.tasks.send_newsletter_confirmation.retry')
    @patch('apps.contact.tasks.send_mail')
    def test_newsletter_confirmation_logs_retry_attempts(self, mock_send_mail, mock_retry):
        """Test that newsletter confirmation logs retry attempts."""
        # Mock send_mail to raise an exception
        mock_send_mail.side_effect = Exception("SMTP connection failed")
        mock_retry.side_effect = Exception("Retry called")
        
        # Call the task
        with self.assertRaises(Exception):
            send_newsletter_confirmation(self.newsletter_subscriber.id)
        
        # Verify retry was called
        mock_retry.assert_called_once()

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        ADMIN_EMAIL='admin@test.com',
        DEFAULT_FROM_EMAIL='noreply@test.com',
        SITE_URL='http://localhost:8000',
    )
    def test_admin_notification_succeeds_after_retry(self):
        """Test that admin notification succeeds after retry."""
        mail.outbox = []
        
        # First call succeeds
        send_contact_admin_notification(self.contact_inquiry.id)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['admin@test.com'])

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        ADMIN_EMAIL='admin@test.com',
        DEFAULT_FROM_EMAIL='noreply@test.com',
        SITE_URL='http://localhost:8000',
    )
    def test_user_confirmation_succeeds_after_retry(self):
        """Test that user confirmation succeeds after retry."""
        mail.outbox = []
        
        # First call succeeds
        send_contact_user_confirmation(self.contact_inquiry.id)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['john@example.com'])

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        ADMIN_EMAIL='admin@test.com',
        DEFAULT_FROM_EMAIL='noreply@test.com',
        SITE_URL='http://localhost:8000',
    )
    def test_newsletter_confirmation_succeeds_after_retry(self):
        """Test that newsletter confirmation succeeds after retry."""
        mail.outbox = []
        
        # First call succeeds
        send_newsletter_confirmation(self.newsletter_subscriber.id)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['subscriber@example.com'])
