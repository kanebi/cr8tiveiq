from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings
from .models import ContactInquiry, NewsletterSubscriber
from .forms import ContactForm, NewsletterForm
from apps.analytics.utils import track_event
import logging

logger = logging.getLogger(__name__)

# Check if Celery should be used
USE_CELERY = getattr(settings, 'USE_REDIS', False) and not getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False)

if USE_CELERY:
    try:
        from .tasks import send_contact_admin_notification, send_contact_user_confirmation, send_newsletter_confirmation
        logger.info("Celery tasks loaded successfully")
    except Exception as e:
        USE_CELERY = False
        logger.warning(f"Celery not available: {str(e)}, using synchronous email sending")
else:
    logger.info("Using synchronous email sending (Celery disabled)")


def send_contact_emails_sync(inquiry_id):
    """Send contact emails synchronously when Celery is not available."""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    
    try:
        inquiry = ContactInquiry.objects.get(id=inquiry_id)
        
        # Send admin notification
        admin_context = {
            'inquiry': inquiry,
            'admin_url': f"{settings.SITE_URL}/admin/contact/contactinquiry/{inquiry.id}/change/",
        }
        admin_html = render_to_string('contact/emails/contact_submission_admin.html', admin_context)
        send_mail(
            subject=f"New Contact Inquiry from {inquiry.name}",
            message=strip_tags(admin_html),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=admin_html,
            fail_silently=True,
        )
        
        # Send user confirmation
        user_context = {'inquiry': inquiry}
        user_html = render_to_string('contact/emails/contact_submission_user.html', user_context)
        send_mail(
            subject="We Received Your Inquiry - CR8TIVEIQ",
            message=strip_tags(user_html),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inquiry.email],
            html_message=user_html,
            fail_silently=True,
        )
        logger.info(f"Contact emails sent synchronously for inquiry {inquiry_id}")
    except Exception as e:
        logger.error(f"Error sending contact emails: {str(e)}")


def send_newsletter_email_sync(subscriber_id):
    """Send newsletter confirmation email synchronously when Celery is not available."""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    
    try:
        subscriber = NewsletterSubscriber.objects.get(id=subscriber_id)
        context = {
            'email': subscriber.email,
            'subscription_date': subscriber.created_at,
        }
        html_message = render_to_string('contact/emails/newsletter_confirmation.html', context)
        send_mail(
            subject="Confirm Your Newsletter Subscription - CR8TIVEIQ",
            message=strip_tags(html_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            html_message=html_message,
            fail_silently=True,
        )
        logger.info(f"Newsletter email sent synchronously to {subscriber.email}")
    except Exception as e:
        logger.error(f"Error sending newsletter email: {str(e)}")


class ContactView(FormView):
    """Contact form view."""
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:success')

    def form_valid(self, form):
        inquiry = form.save()
        
        # Track form submission in analytics
        try:
            track_event(
                event_type='form_submit',
                page_url=self.request.path,
                user_session_id=self.request.session.session_key or 'anonymous',
                event_data={
                    'form_name': 'contact_form',
                    'form_id': 'contact-form',
                    'field_count': len(form.fields),
                    'inquiry_id': inquiry.id,
                    'service_type': inquiry.service_type,
                }
            )
        except Exception as e:
            logger.warning(f"Error tracking form submission: {str(e)}")
        
        # Send emails via Celery or synchronously
        try:
            if USE_CELERY:
                send_contact_admin_notification.delay(inquiry.id)
                send_contact_user_confirmation.delay(inquiry.id)
                logger.info(f"Contact emails queued via Celery for inquiry {inquiry.id}")
            else:
                send_contact_emails_sync(inquiry.id)
        except Exception as e:
            logger.error(f"Error sending contact emails: {str(e)}")
            # Still show success to user even if email fails
        
        messages.success(self.request, 'Your inquiry has been submitted successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ContactSuccessView(TemplateView):
    """Contact success view."""
    template_name = 'contact/contact_success.html'


class NewsletterSubscribeView(FormView):
    """Newsletter subscription view."""
    form_class = NewsletterForm
    
    def form_valid(self, form):
        try:
            subscriber = form.save()
            
            # Send newsletter confirmation email
            try:
                if USE_CELERY:
                    send_newsletter_confirmation.delay(subscriber.id)
                    logger.info(f"Newsletter email queued via Celery for {subscriber.email}")
                else:
                    send_newsletter_email_sync(subscriber.id)
            except Exception as e:
                logger.error(f"Error sending newsletter email: {str(e)}")
            
            messages.success(self.request, 'Thank you for subscribing! Please check your email to confirm.')
            return redirect(self.request.META.get('HTTP_REFERER', '/'))
        except Exception as e:
            logger.error(f"Error subscribing to newsletter: {str(e)}")
            messages.error(self.request, 'An error occurred. Please try again.')
            return redirect(self.request.META.get('HTTP_REFERER', '/'))
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please enter a valid email address.')
        return redirect(self.request.META.get('HTTP_REFERER', '/'))
