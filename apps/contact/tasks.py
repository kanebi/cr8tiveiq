"""
Celery tasks for contact app email notifications.
"""

import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from .models import ContactInquiry, NewsletterSubscriber

logger = logging.getLogger(__name__)

# Retry configuration constants
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 60  # 60 seconds
EXPONENTIAL_BACKOFF_BASE = 2  # Multiply delay by 2 for each retry


def calculate_retry_delay(retry_count):
    """
    Calculate exponential backoff delay for retries.
    
    Args:
        retry_count: Current retry attempt number (0-indexed)
        
    Returns:
        Delay in seconds with exponential backoff
    """
    return INITIAL_RETRY_DELAY * (EXPONENTIAL_BACKOFF_BASE ** retry_count)


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_contact_admin_notification(self, inquiry_id):
    """
    Send admin notification email when contact form is submitted.
    
    Implements retry logic with exponential backoff for failed email sends.
    
    Args:
        inquiry_id: ID of the ContactInquiry instance
        
    Requirement: Requirement 26 - Email notifications SHALL be sent within 5 seconds
    """
    try:
        inquiry = ContactInquiry.objects.get(id=inquiry_id)
        
        # Prepare email context
        context = {
            'inquiry': inquiry,
            'admin_url': f"{settings.SITE_URL}/admin/contact/contactinquiry/{inquiry.id}/change/",
        }
        
        # Render email template
        html_message = render_to_string(
            'contact/emails/contact_submission_admin.html',
            context
        )
        plain_message = strip_tags(html_message)
        
        # Send email to admin
        send_mail(
            subject=f"New Contact Inquiry from {inquiry.name}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Admin notification email sent for inquiry {inquiry_id}")
        
    except ContactInquiry.DoesNotExist:
        logger.error(f"ContactInquiry with id {inquiry_id} does not exist - permanent failure")
        # Don't retry for non-existent inquiries
        
    except Exception as exc:
        retry_count = self.request.retries
        retry_delay = calculate_retry_delay(retry_count)
        
        logger.warning(
            f"Error sending admin notification email for inquiry {inquiry_id} "
            f"(attempt {retry_count + 1}/{MAX_RETRIES + 1}): {str(exc)}"
        )
        
        try:
            # Retry with exponential backoff
            raise self.retry(exc=exc, countdown=retry_delay)
        except MaxRetriesExceededError:
            logger.error(
                f"Failed to send admin notification email for inquiry {inquiry_id} "
                f"after {MAX_RETRIES} retries. Permanent failure."
            )


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_contact_user_confirmation(self, inquiry_id):
    """
    Send confirmation email to user when contact form is submitted.
    
    Implements retry logic with exponential backoff for failed email sends.
    
    Args:
        inquiry_id: ID of the ContactInquiry instance
        
    Requirement: Requirement 26 - Email notifications SHALL be sent within 5 seconds
    """
    try:
        inquiry = ContactInquiry.objects.get(id=inquiry_id)
        
        # Prepare email context
        context = {
            'inquiry': inquiry,
        }
        
        # Render email template
        html_message = render_to_string(
            'contact/emails/contact_submission_user.html',
            context
        )
        plain_message = strip_tags(html_message)
        
        # Send email to user
        send_mail(
            subject="We Received Your Inquiry - CR8TIVEIQ",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inquiry.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"User confirmation email sent for inquiry {inquiry_id} to {inquiry.email}")
        
    except ContactInquiry.DoesNotExist:
        logger.error(f"ContactInquiry with id {inquiry_id} does not exist - permanent failure")
        # Don't retry for non-existent inquiries
        
    except Exception as exc:
        retry_count = self.request.retries
        retry_delay = calculate_retry_delay(retry_count)
        
        logger.warning(
            f"Error sending user confirmation email for inquiry {inquiry_id} "
            f"(attempt {retry_count + 1}/{MAX_RETRIES + 1}): {str(exc)}"
        )
        
        try:
            # Retry with exponential backoff
            raise self.retry(exc=exc, countdown=retry_delay)
        except MaxRetriesExceededError:
            logger.error(
                f"Failed to send user confirmation email for inquiry {inquiry_id} "
                f"after {MAX_RETRIES} retries. Permanent failure."
            )


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_newsletter_confirmation(self, subscriber_id):
    """
    Send confirmation email when user subscribes to newsletter.
    
    Implements retry logic with exponential backoff for failed email sends.
    
    Args:
        subscriber_id: ID of the NewsletterSubscriber instance
        
    Requirement: Requirement 27 - Newsletter confirmation email
    """
    try:
        subscriber = NewsletterSubscriber.objects.get(id=subscriber_id)
        
        # Generate confirmation link (placeholder - implement based on your confirmation flow)
        confirmation_link = f"{settings.SITE_URL}/newsletter/confirm/{subscriber.id}/"
        unsubscribe_link = f"{settings.SITE_URL}/newsletter/unsubscribe/{subscriber.id}/"
        
        # Prepare email context
        context = {
            'email': subscriber.email,
            'subscription_date': subscriber.created_at,
            'confirmation_link': confirmation_link,
            'unsubscribe_link': unsubscribe_link,
        }
        
        # Render email template
        html_message = render_to_string(
            'contact/emails/newsletter_confirmation.html',
            context
        )
        plain_message = strip_tags(html_message)
        
        # Send email to subscriber
        send_mail(
            subject="Confirm Your Newsletter Subscription - CR8TIVEIQ",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Newsletter confirmation email sent to {subscriber.email}")
        
    except NewsletterSubscriber.DoesNotExist:
        logger.error(f"NewsletterSubscriber with id {subscriber_id} does not exist - permanent failure")
        # Don't retry for non-existent subscribers
        
    except Exception as exc:
        retry_count = self.request.retries
        retry_delay = calculate_retry_delay(retry_count)
        
        logger.warning(
            f"Error sending newsletter confirmation email for subscriber {subscriber_id} "
            f"(attempt {retry_count + 1}/{MAX_RETRIES + 1}): {str(exc)}"
        )
        
        try:
            # Retry with exponential backoff
            raise self.retry(exc=exc, countdown=retry_delay)
        except MaxRetriesExceededError:
            logger.error(
                f"Failed to send newsletter confirmation email for subscriber {subscriber_id} "
                f"after {MAX_RETRIES} retries. Permanent failure."
            )
