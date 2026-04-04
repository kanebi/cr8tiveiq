"""URL configuration for analytics app."""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('track-cta-click/', views.track_cta_click, name='track_cta_click'),
]
