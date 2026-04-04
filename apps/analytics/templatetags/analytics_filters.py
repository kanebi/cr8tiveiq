"""Custom template filters for analytics app."""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, key)
    return key


@register.filter
def percentage(value, total):
    """Calculate percentage of value relative to total."""
    if total == 0:
        return 0
    return int((value / total) * 100)
