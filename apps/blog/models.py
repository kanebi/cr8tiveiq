from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from apps.core.models import BaseModel


class BlogArticle(BaseModel):
    """Blog article model."""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    summary = models.TextField(help_text="Brief summary for cards and listings", blank=True)
    excerpt = models.TextField(blank=True, help_text="Short excerpt (deprecated, use summary)")
    content = RichTextField(help_text="Full article content with rich text formatting")
    featured_image = models.ImageField(upload_to='blog/', blank=True)
    category = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Blog Article'
        verbose_name_plural = 'Blog Articles'

    def __str__(self):
        return self.title
    
    def get_summary(self):
        """Return summary or fall back to excerpt."""
        return self.summary or self.excerpt
