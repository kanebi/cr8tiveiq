"""Tests for portfolio app."""

import json
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse
from .models import PortfolioGalleryImage, PortfolioProject, PortfolioVideo, video_embed_src
from apps.analytics.models import AnalyticsEvent


class PortfolioViewTrackingTest(TestCase):
    """Test portfolio view tracking."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.project = PortfolioProject.objects.create(
            title='Test Project',
            slug='test-project',
            client_name='Test Client',
            category='graphics',
            description='Test description',
            featured_image='test.jpg',
        )

    def test_portfolio_click_tracking_api(self):
        """Test portfolio click tracking API endpoint."""
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        # Send tracking request
        response = self.client.post(
            reverse('portfolio:track_click'),
            data=json.dumps({
                'portfolio_id': self.project.id,
                'portfolio_title': self.project.title,
                'portfolio_category': 'Graphics',
            }),
            content_type='application/json'
        )
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
        # Check that portfolio view event was tracked
        events = AnalyticsEvent.objects.filter(event_type='portfolio_view')
        self.assertEqual(events.count(), 1)
        
        # Verify event data
        event = events.first()
        self.assertEqual(event.event_data['portfolio_id'], self.project.id)
        self.assertEqual(event.event_data['portfolio_title'], self.project.title)
        self.assertEqual(event.event_data['portfolio_category'], 'Graphics')

    def test_portfolio_click_tracking_api_invalid_json(self):
        """Test portfolio click tracking API with invalid JSON."""
        # Send invalid JSON
        response = self.client.post(
            reverse('portfolio:track_click'),
            data='invalid json',
            content_type='application/json'
        )
        
        # Check response is error
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')

    def test_portfolio_view_tracking_includes_session_id(self):
        """Test that portfolio view tracking includes session ID."""
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        # Send tracking request
        self.client.post(
            reverse('portfolio:track_click'),
            data=json.dumps({
                'portfolio_id': self.project.id,
                'portfolio_title': self.project.title,
                'portfolio_category': 'Graphics',
            }),
            content_type='application/json'
        )
        
        # Check that portfolio view event was tracked with session ID
        events = AnalyticsEvent.objects.filter(event_type='portfolio_view')
        self.assertEqual(events.count(), 1)
        
        event = events.first()
        # Session ID should be set (either from session or IP address)
        self.assertIsNotNone(event.user_session_id)
        self.assertTrue(len(event.user_session_id) > 0)

    def test_multiple_portfolio_views_tracked(self):
        """Test that multiple portfolio views are tracked separately."""
        # Create another project
        project2 = PortfolioProject.objects.create(
            title='Test Project 2',
            slug='test-project-2',
            client_name='Test Client 2',
            category='video',
            description='Test description 2',
            featured_image='test2.jpg',
        )
        
        # Clear existing events
        AnalyticsEvent.objects.all().delete()
        
        # Send tracking request for first project
        self.client.post(
            reverse('portfolio:track_click'),
            data=json.dumps({
                'portfolio_id': self.project.id,
                'portfolio_title': self.project.title,
                'portfolio_category': 'Graphics',
            }),
            content_type='application/json'
        )
        
        # Send tracking request for second project
        self.client.post(
            reverse('portfolio:track_click'),
            data=json.dumps({
                'portfolio_id': project2.id,
                'portfolio_title': project2.title,
                'portfolio_category': 'Video',
            }),
            content_type='application/json'
        )
        
        # Check that both portfolio views were tracked
        events = AnalyticsEvent.objects.filter(event_type='portfolio_view')
        self.assertEqual(events.count(), 2)
        
        # Verify each event has correct data
        event_ids = [e.event_data['portfolio_id'] for e in events]
        self.assertIn(self.project.id, event_ids)
        self.assertIn(project2.id, event_ids)


class VideoEmbedSrcTests(SimpleTestCase):
    def test_youtube_watch_url(self):
        self.assertEqual(
            video_embed_src('https://www.youtube.com/watch?v=dQw4w9wgGcQ'),
            'https://www.youtube.com/embed/dQw4w9wgGcQ',
        )

    def test_youtube_short_url(self):
        self.assertEqual(
            video_embed_src('https://youtu.be/dQw4w9wgGcQ'),
            'https://www.youtube.com/embed/dQw4w9wgGcQ',
        )

    def test_vimeo_url(self):
        self.assertEqual(
            video_embed_src('https://vimeo.com/123456789'),
            'https://player.vimeo.com/video/123456789',
        )

    def test_empty_url(self):
        self.assertEqual(video_embed_src(''), '')


class PortfolioGalleryRenderTests(TestCase):
    def setUp(self):
        self.project = PortfolioProject.objects.create(
            title='Gallery Project',
            slug='gallery-project',
            client_name='Studio',
            category='video',
            description='Work samples.',
            featured_image='portfolio/hero.jpg',
        )

    def test_detail_renders_gallery_images_and_uploaded_video(self):
        image = PortfolioGalleryImage(project=self.project, caption='Still one', order=0)
        image.image.name = 'portfolio/gallery/still.jpg'
        image.save()
        video = PortfolioVideo(project=self.project, title='Cutdown', order=0)
        video.video.name = 'portfolio/videos/cutdown.mp4'
        video.save()

        response = self.client.get(reverse('portfolio:detail', args=[self.project.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Still one')
        self.assertContains(response, 'portfolio/gallery/still.jpg')
        self.assertContains(response, 'portfolio/videos/cutdown.mp4')
        self.assertContains(response, '<video')

    def test_detail_embeds_youtube_url(self):
        PortfolioVideo.objects.create(
            project=self.project,
            embed_url='https://www.youtube.com/watch?v=dQw4w9wgGcQ',
            title='Launch film',
            order=0,
        )
        response = self.client.get(reverse('portfolio:detail', args=[self.project.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://www.youtube.com/embed/dQw4w9wgGcQ')
        self.assertContains(response, '<iframe')
