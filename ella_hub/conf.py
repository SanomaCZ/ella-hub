from django.conf import settings

API_KEY_EXPIRATION_IN_DAYS = getattr(settings, 'ELLA_HUB_API_KEY_EXPIRATION_IN_DAYS', 14)
STATES_CACHE_TIMEOUT = getattr(settings, 'ELLA_HUB_STATES_CACHE_TIMEOUT', 5 * 60)
THUMBNAIL_FORMAT = getattr(settings, 'ELLA_HUB_THUMBNAIL_FORMAT', None)
ALLOW_THUMBNAIL_FALLBACK = getattr(settings, 'ELLA_HUB_ALLOW_THUMBNAIL_FALLBACK', True)
MEDIA_DRAFTS_DIR = getattr(settings, 'ELLA_HUB_MEDIA_DRAFTS_DIR', 'ella_hub_drafts')
