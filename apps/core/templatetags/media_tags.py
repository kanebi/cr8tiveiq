from django import template

from apps.core.storage import absolute_media_url

register = template.Library()


@register.filter(name='media_url')
def media_url(filefield):
    """Render a media file as an absolute URL when GCS is enabled."""
    if not filefield:
        return ''
    name = getattr(filefield, 'name', filefield)
    if hasattr(filefield, 'url'):
        try:
            return absolute_media_url(filefield.url)
        except ValueError:
            return absolute_media_url(name)
    return absolute_media_url(name)
