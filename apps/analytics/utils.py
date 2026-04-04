from .models import AnalyticsEvent


def track_event(event_type, page_url=None, user_session_id=None, event_data=None):
    """Track an analytics event."""
    AnalyticsEvent.objects.create(
        event_type=event_type,
        page_url=page_url,
        user_session_id=user_session_id,
        event_data=event_data or {}
    )
