import json
from urllib.parse import urljoin, urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


def normalize_media_base(url):
    """Return a media base URL that always ends with a slash."""
    url = (url or '').strip().strip('"').strip("'")
    if not url:
        return ''
    return url if url.endswith('/') else f'{url}/'


def _public_base(bucket, location=''):
    base = f'https://storage.googleapis.com/{bucket}/'
    if location:
        base += f'{location.strip("/")}/'
    return base


def parse_gcs_media_url(media_url):
    """
    Read bucket + folder prefix from a GCS URL, console link, or bucket name.

    https://storage.googleapis.com/cr8tive-iq/media/
    https://console.cloud.google.com/storage/browser/cr8tive-iq
    gs://cr8tive-iq/media
    cr8tive-iq
    """
    raw = (media_url or '').strip().strip('"').strip("'")
    if not raw:
        return {'bucket': '', 'location': '', 'base_url': '', 'host': ''}

    if '://' not in raw and '/' not in raw:
        return {
            'bucket': raw,
            'location': '',
            'base_url': _public_base(raw),
            'host': 'storage.googleapis.com',
        }

    parsed = urlparse(raw)
    path = parsed.path.split(';')[0]
    parts = [part for part in path.split('/') if part]
    bucket = ''
    location = ''

    if parsed.scheme == 'gs':
        bucket = parsed.netloc
        location = '/'.join(parts)
    elif parsed.netloc == 'console.cloud.google.com':
        marker = None
        if 'browser' in parts:
            marker = 'browser'
        elif 'buckets' in parts:
            marker = 'buckets'
        if marker:
            rest = parts[parts.index(marker) + 1:]
            bucket = rest[0] if rest else ''
            location = '/'.join(rest[1:])
    elif parsed.netloc in ('storage.googleapis.com', 'storage.cloud.google.com') and parts:
        bucket = parts[0]
        location = '/'.join(parts[1:])
    elif parts:
        location = '/'.join(parts)

    if bucket:
        base_url = _public_base(bucket, location)
        host = 'storage.googleapis.com'
    else:
        base_url = normalize_media_base(raw)
        host = parsed.netloc

    return {
        'bucket': bucket,
        'location': location,
        'base_url': base_url,
        'host': host,
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


def parse_gcs_credentials_json(raw):
    """Parse a service-account JSON string from an env var. Empty returns None."""
    text = str(raw or '').strip()
    if not text:
        return None

    candidates = [text]
    if text.startswith("'") and text.endswith("'"):
        candidates.append(text[1:-1].strip())

    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                continue
        if isinstance(data, dict) and data.get('type') == 'service_account':
            private_key = data.get('private_key', '')
            if isinstance(private_key, str) and '\\n' in private_key:
                data['private_key'] = private_key.replace('\\n', '\n')
            return data

    raise ImproperlyConfigured(
        'GCS_CREDENTIALS_JSON must be the raw service-account JSON object, not a file path.'
    )


def _gcs_client():
    from google.cloud import storage
    from google.oauth2 import service_account

    info = getattr(settings, 'GCS_CREDENTIALS_INFO', None)
    if not info:
        info = parse_gcs_credentials_json(getattr(settings, 'GCS_CREDENTIALS_JSON', ''))
    if info:
        credentials = service_account.Credentials.from_service_account_info(info)
        return storage.Client(credentials=credentials, project=info.get('project_id'))
    return storage.Client.create_anonymous_client()


@deconstructible
class PublicGCSMediaStorage(Storage):
    """
    Public GCS media. URL generation needs only GS_MEDIA_URL.

    Uploads read GCS_CREDENTIALS_JSON (the service-account JSON string, not a
    file path). A public bucket still cannot accept anonymous writes.
    """

    def url(self, name):
        return absolute_media_url(name)

    def _bucket(self):
        parsed = parse_gcs_media_url(getattr(settings, 'GS_MEDIA_URL', '') or getattr(settings, 'MEDIA_URL', ''))
        if not parsed['bucket']:
            raise ImproperlyConfigured(
                'GS_MEDIA_URL must include a bucket name, e.g. '
                'https://storage.googleapis.com/cr8tive-iq/ or '
                'https://console.cloud.google.com/storage/browser/cr8tive-iq'
            )
        return _gcs_client().bucket(parsed['bucket'])

    def _blob(self, name):
        return self._bucket().blob(object_name(name))

    def _save(self, name, content):
        blob = self._blob(name)
        content.seek(0)
        blob.cache_control = 'public, max-age=86400'
        try:
            blob.upload_from_file(content, rewind=True, content_type=getattr(content, 'content_type', None))
        except Exception as exc:
            status = getattr(exc, 'code', None) or getattr(getattr(exc, 'response', None), 'status_code', None)
            if status in (401, 403) or 'Anonymous' in str(exc) or 'credentials' in str(exc).lower():
                raise ImproperlyConfigured(
                    'This public bucket can serve files without a key, but admin uploads '
                    'still need write access. Add a service-account JSON as GCS_CREDENTIALS_JSON, '
                    'or grant allUsers the Storage Object Creator role on the bucket.'
                ) from exc
            raise
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
