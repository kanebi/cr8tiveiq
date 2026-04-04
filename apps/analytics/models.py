from django.db import models
from apps.core.models import BaseModel


class AnalyticsEvent(BaseModel):
    """Analytics event model."""
    EVENT_TYPE_CHOICES = [
        ('page_view', 'Page View'),
        ('cta_click', 'CTA Click'),
        ('form_submit', 'Form Submit'),
        ('portfolio_view', 'Portfolio View'),
        ('service_view', 'Service View'),
    ]

    event_type = models.CharField(max_length=100, choices=EVENT_TYPE_CHOICES)
    page_url = models.CharField(max_length=500, blank=True)
    user_session_id = models.CharField(max_length=255, blank=True, null=True)
    event_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Analytics Event'
        verbose_name_plural = 'Analytics Events'
        indexes = [
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['user_session_id', '-created_at']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"
