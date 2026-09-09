from urllib.parse import parse_qs, urlparse

from django.db import models

from apps.core.models import BaseModel
from apps.services.models import Service


def video_embed_src(url):
    """Turn a YouTube/Vimeo watch URL into an embeddable iframe src."""
    text = (url or '').strip()
    if not text:
        return ''

    parsed = urlparse(text)
    host = (parsed.netloc or '').lower()
    path = parsed.path or ''

    if 'youtu.be' in host:
        video_id = path.strip('/').split('/')[0]
        return f'https://www.youtube.com/embed/{video_id}' if video_id else ''

    if 'youtube.com' in host:
        if '/embed/' in path:
            video_id = path.split('/embed/')[1].split('/')[0]
            return f'https://www.youtube.com/embed/{video_id}' if video_id else ''
        if path.startswith('/shorts/'):
            video_id = path.split('/shorts/')[1].split('/')[0]
            return f'https://www.youtube.com/embed/{video_id}' if video_id else ''
        video_id = (parse_qs(parsed.query).get('v') or [''])[0]
        return f'https://www.youtube.com/embed/{video_id}' if video_id else ''

    if 'vimeo.com' in host:
        if 'player.vimeo.com' in host:
            return text
        video_id = next((part for part in path.strip('/').split('/') if part.isdigit()), '')
        return f'https://player.vimeo.com/video/{video_id}' if video_id else ''

    return ''


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


class PortfolioGalleryImage(BaseModel):
    """One uploaded gallery image. Featured image stays on the project."""
    project = models.ForeignKey(
        PortfolioProject,
        on_delete=models.CASCADE,
        related_name='gallery_items',
    )
    image = models.ImageField(upload_to='portfolio/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Gallery image'
        verbose_name_plural = 'Gallery images'

    def __str__(self):
        return self.caption or self.image.name


class PortfolioVideo(BaseModel):
    """One uploaded video file or a YouTube/Vimeo URL."""
    project = models.ForeignKey(
        PortfolioProject,
        on_delete=models.CASCADE,
        related_name='video_items',
    )
    video = models.FileField(upload_to='portfolio/videos/', blank=True)
    embed_url = models.URLField(
        blank=True,
        help_text='YouTube or Vimeo link if you are not uploading a file.',
    )
    title = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Gallery video'
        verbose_name_plural = 'Gallery videos'

    def __str__(self):
        return self.title or self.embed_url or (self.video.name if self.video else 'Video')

    @property
    def embed_src(self):
        return video_embed_src(self.embed_url)
