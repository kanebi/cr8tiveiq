from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class BaseModel(models.Model):
    """Base model with common fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Testimonial(models.Model):
    """Client testimonial with rating."""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    client_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    testimonial_text = models.TextField()
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f"{self.client_name} - {self.rating} stars"


# USER MODEL DECISION:
# The default Django User model is sufficient for CR8TIVEIQ.
# 
# Rationale:
# - CR8TIVEIQ is a public-facing digital agency portfolio website
# - Visitor interactions are captured through ContactInquiry and NewsletterSubscriber models
# - Admin/staff user management is handled by Django's built-in User model
# - No visitor authentication or user profiles are required
# - No custom user roles beyond admin/staff are needed
# - Contact preferences and newsletter subscriptions are managed separately
#
# The following models handle user-related data:
# - ContactInquiry: Stores client project inquiries
# - NewsletterSubscriber: Manages newsletter subscriptions
# - Django's built-in User model: Manages admin/staff users
#
# If future requirements include visitor authentication, user profiles, or
# custom user roles, a UserProfile model can be created at that time.
