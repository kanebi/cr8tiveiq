from django.db import models
from ckeditor.fields import RichTextField
from apps.core.models import BaseModel


class Service(BaseModel):
    """Service model."""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    short_description = models.TextField(help_text="Brief summary for cards and listings")
    description = RichTextField(help_text="Full content with rich text formatting")
    icon = models.CharField(max_length=255, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.title
