from urllib.parse import urljoin, urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


def normalize_media_base(url):
    """Return a media base URL that always ends with a slash."""
    url = (url or '').strip()
    if not url:
        return ''
    return url if url.endswith('/') else f'{url}/'


def parse_gcs_media_url(media_url):
    """
    Read bucket + folder prefix from a public GCS (or CDN) media URL.

    https://storage.googleapis.com/cr8tiveiq-media/media/
        → bucket=cr8tiveiq-media, location=media
    https://storage.googleapis.com/cr8tiveiq-media/
        → bucket=cr8tiveiq-media, location=''
    https://cdn.example.com/media/
        → bucket='', location=media
    """
    base = normalize_media_base(media_url)
    parsed = urlparse(base)
    parts = [part for part in parsed.path.split('/') if part]
    bucket = ''
    location = ''

    if parsed.netloc == 'storage.googleapis.com' and parts:
        bucket = parts[0]
        location = '/'.join(parts[1:])
    elif parts:
        location = '/'.join(parts)

    return {
        'bucket': bucket,
        'location': location,
        'base_url': base,
        'host': parsed.netloc,
    }


def absolute_media_url(name):
    """Build a public URL for a stored file name. Never double-prefix."""
    if not name:
        return ''

    raw = getattr(name, 'name', name)
    raw = str(raw).strip()
    if not raw:
        return ''
    if raw.startswith(('http://', 'https://')):
        return raw

    base = normalize_media_base(getattr(settings, 'MEDIA_URL', '/media/'))
    relative = raw.lstrip('/')
    if relative.startswith('media/'):
        relative = relative[len('media/'):]
    return urljoin(base, relative)


def object_name(name):
    """Object path inside the bucket, including the media prefix."""
    parsed = parse_gcs_media_url(getattr(settings, 'GS_MEDIA_URL', '') or getattr(settings, 'MEDIA_URL', ''))
    relative = str(name).lstrip('/')
    if parsed['location']:
        return f"{parsed['location'].rstrip('/')}/{relative}"
    return relative


def _gcs_client():
    from google.cloud import storage
    from google.oauth2 import service_account

    credentials_json = getattr(settings, 'GCS_CREDENTIALS_JSON', '') or ''
    credentials_json = str(credentials_json).strip()
    credentials_file = getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS', '') or ''
    credentials_file = str(credentials_file).strip()

    if credentials_json:
        import json
        credentials = service_account.Credentials.from_service_account_info(json.loads(credentials_json))
        return storage.Client(credentials=credentials, project=credentials.project_id)
    if credentials_file:
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        return storage.Client(credentials=credentials, project=credentials.project_id)
    return storage.Client()


@deconstructible
class PublicGCSMediaStorage(Storage):
    """
    Public GCS media. URL generation needs only GS_MEDIA_URL.

    Uploads use ADC or optional GCS_CREDENTIALS_JSON. A public bucket still
    cannot accept anonymous writes.
    """

    def url(self, name):
        return absolute_media_url(name)

    def _bucket(self):
        parsed = parse_gcs_media_url(getattr(settings, 'GS_MEDIA_URL', '') or getattr(settings, 'MEDIA_URL', ''))
        if not parsed['bucket']:
            raise ImproperlyConfigured(
                'GS_MEDIA_URL must be a https://storage.googleapis.com/<bucket>/... URL '
                'so uploads know which bucket to use.'
            )
        return _gcs_client().bucket(parsed['bucket'])

    def _blob(self, name):
        return self._bucket().blob(object_name(name))

    def _save(self, name, content):
        blob = self._blob(name)
        content.seek(0)
        blob.cache_control = 'public, max-age=86400'
        blob.upload_from_file(content, rewind=True, content_type=getattr(content, 'content_type', None))
        return name

    def _open(self, name, mode='rb'):
        blob = self._blob(name)
        return ContentFile(blob.download_as_bytes(), name=name)

    def exists(self, name):
        try:
            return self._blob(name).exists()
        except Exception:
            return False

    def delete(self, name):
        try:
            self._blob(name).delete()
        except Exception:
            pass

    def size(self, name):
        blob = self._blob(name)
        blob.reload()
        return blob.size or 0
