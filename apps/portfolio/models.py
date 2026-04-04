from django.db import models
from apps.core.models import BaseModel
from apps.services.models import Service


class PortfolioProject(BaseModel):
    """Portfolio project model."""
    CATEGORY_CHOICES = [
        ('graphics', 'Graphics'),
        ('social_media', 'Social Media'),
        ('video', 'Video'),
        ('ads', 'Ads'),
        ('websites', 'Websites'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    client_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    featured_image = models.ImageField(upload_to='portfolio/')
    gallery_images = models.JSONField(default=list, blank=True)
    videos = models.JSONField(default=list, blank=True)
    services_used = models.ManyToManyField(Service, blank=True, related_name='portfolio_projects')
    timeline = models.CharField(max_length=100, blank=True)
    results = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['-order', '-created_at']
        verbose_name = 'Portfolio Project'
        verbose_name_plural = 'Portfolio Projects'

    def __str__(self):
        return self.title
