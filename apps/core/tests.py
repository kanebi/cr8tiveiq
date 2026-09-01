import json
from unittest.mock import patch

from django.template import Context, Template
from django.test import SimpleTestCase, TestCase, override_settings

from apps.core.models import Testimonial
from apps.core.storage import (
    PublicGCSMediaStorage,
    _gcs_client,
    absolute_media_url,
    object_name,
    parse_gcs_credentials_json,
    parse_gcs_media_url,
)
from apps.portfolio.models import PortfolioProject


GCS_MEDIA = 'https://storage.googleapis.com/cr8tiveiq-media/media/'


class ParseGcsMediaUrlTests(SimpleTestCase):
    def test_parses_bucket_and_media_prefix(self):
        parsed = parse_gcs_media_url(GCS_MEDIA)
        self.assertEqual(parsed['bucket'], 'cr8tiveiq-media')
        self.assertEqual(parsed['location'], 'media')
        self.assertEqual(parsed['base_url'], GCS_MEDIA)

    def test_parses_bucket_root(self):
        parsed = parse_gcs_media_url('https://storage.googleapis.com/cr8tiveiq-media')
        self.assertEqual(parsed['bucket'], 'cr8tiveiq-media')
        self.assertEqual(parsed['location'], '')
        self.assertTrue(parsed['base_url'].endswith('/'))

    def test_parses_console_browser_url(self):
        parsed = parse_gcs_media_url('https://console.cloud.google.com/storage/browser/cr8tive-iq')
        self.assertEqual(parsed['bucket'], 'cr8tive-iq')
        self.assertEqual(parsed['location'], '')
        self.assertEqual(parsed['base_url'], 'https://storage.googleapis.com/cr8tive-iq/')

    def test_parses_quoted_console_url(self):
        parsed = parse_gcs_media_url('"https://console.cloud.google.com/storage/browser/cr8tive-iq"')
        self.assertEqual(parsed['bucket'], 'cr8tive-iq')
        self.assertEqual(parsed['base_url'], 'https://storage.googleapis.com/cr8tive-iq/')

    def test_parses_bare_bucket_name(self):
        parsed = parse_gcs_media_url('cr8tive-iq')
        self.assertEqual(parsed['bucket'], 'cr8tive-iq')
        self.assertEqual(parsed['base_url'], 'https://storage.googleapis.com/cr8tive-iq/')


class AbsoluteMediaUrlTests(SimpleTestCase):
    @override_settings(MEDIA_URL=GCS_MEDIA, GS_MEDIA_URL=GCS_MEDIA, USE_GCS=True)
    def test_relative_name_becomes_full_gcs_url(self):
        self.assertEqual(
            absolute_media_url('testimonials/jane.jpg'),
            f'{GCS_MEDIA}testimonials/jane.jpg',
        )

    @override_settings(MEDIA_URL=GCS_MEDIA, GS_MEDIA_URL=GCS_MEDIA, USE_GCS=True)
    def test_does_not_double_prefix_absolute_url(self):
        full = f'{GCS_MEDIA}blog/cover.png'
        self.assertEqual(absolute_media_url(full), full)

    @override_settings(MEDIA_URL=GCS_MEDIA, GS_MEDIA_URL=GCS_MEDIA, USE_GCS=True)
    def test_strips_local_media_prefix(self):
        self.assertEqual(
            absolute_media_url('/media/portfolio/work.jpg'),
            f'{GCS_MEDIA}portfolio/work.jpg',
        )

    @override_settings(MEDIA_URL='/media/')
    def test_local_urls_stay_relative(self):
        self.assertEqual(absolute_media_url('blog/cover.png'), '/media/blog/cover.png')


class PublicGCSMediaStorageTests(SimpleTestCase):
    @override_settings(MEDIA_URL=GCS_MEDIA, GS_MEDIA_URL=GCS_MEDIA, USE_GCS=True)
    def test_storage_url_is_absolute(self):
        storage = PublicGCSMediaStorage()
        self.assertEqual(
            storage.url('testimonials/jane.jpg'),
            f'{GCS_MEDIA}testimonials/jane.jpg',
        )

    @override_settings(MEDIA_URL=GCS_MEDIA, GS_MEDIA_URL=GCS_MEDIA, USE_GCS=True)
    def test_object_name_includes_media_prefix(self):
        self.assertEqual(object_name('blog/cover.png'), 'media/blog/cover.png')

    @override_settings(GCS_CREDENTIALS_JSON='', GCS_CREDENTIALS_INFO=None)
    def test_public_bucket_uses_anonymous_client(self):
        with patch('google.cloud.storage.Client') as client_cls:
            _gcs_client()
            client_cls.create_anonymous_client.assert_called_once()
            client_cls.assert_not_called()


class ParseCredentialsJsonTests(SimpleTestCase):
    SAMPLE = {
        'type': 'service_account',
        'project_id': 'demo-project',
        'private_key_id': 'abc',
        'private_key': '-----BEGIN PRIVATE KEY-----\nDEMO\n-----END PRIVATE KEY-----\n',
        'client_email': 'media@demo-project.iam.gserviceaccount.com',
        'token_uri': 'https://oauth2.googleapis.com/token',
    }

    def test_parses_one_line_json(self):
        info = parse_gcs_credentials_json(json.dumps(self.SAMPLE))
        self.assertEqual(info['project_id'], 'demo-project')
        self.assertIn('\n', info['private_key'])

    def test_parses_double_encoded_json(self):
        info = parse_gcs_credentials_json(json.dumps(json.dumps(self.SAMPLE)))
        self.assertEqual(info['client_email'], 'media@demo-project.iam.gserviceaccount.com')

    def test_empty_returns_none(self):
        self.assertIsNone(parse_gcs_credentials_json(''))
        self.assertIsNone(parse_gcs_credentials_json(None))

    def test_rejects_file_path(self):
        from django.core.exceptions import ImproperlyConfigured
        with self.assertRaises(ImproperlyConfigured):
            parse_gcs_credentials_json('gcs-credentials.json')


class MediaUrlFilterTests(SimpleTestCase):
    @override_settings(MEDIA_URL=GCS_MEDIA, GS_MEDIA_URL=GCS_MEDIA, USE_GCS=True)
    def test_template_filter_renders_full_url(self):
        template = Template('{% load media_tags %}{{ photo|media_url }}')
        html = template.render(Context({'photo': 'testimonials/jane.jpg'}))
        self.assertEqual(html, f'{GCS_MEDIA}testimonials/jane.jpg')


@override_settings(
    USE_GCS=True,
    GS_MEDIA_URL=GCS_MEDIA,
    MEDIA_URL=GCS_MEDIA,
    STORAGES={
        'default': {'BACKEND': 'apps.core.storage.PublicGCSMediaStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class FrontendGcsUrlTests(TestCase):
    def test_home_testimonial_uses_full_gcs_url(self):
        Testimonial.objects.create(
            client_name='Jane Doe',
            testimonial_text='Great work.',
            photo='testimonials/jane.jpg',
            rating=5,
            is_active=True,
        )
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'{GCS_MEDIA}testimonials/jane.jpg')
        self.assertNotContains(response, 'src="/media/testimonials/jane.jpg"')

    def test_portfolio_list_uses_full_gcs_url(self):
        PortfolioProject.objects.create(
            title='Brand Refresh',
            slug='brand-refresh',
            client_name='Acme',
            category='graphics',
            description='A new look.',
            featured_image='portfolio/brand.jpg',
        )
        response = self.client.get('/portfolio/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'{GCS_MEDIA}portfolio/brand.jpg')
