from django.conf import settings

API_KEY_EXPIRATION_IN_DAYS = getattr(settings, 'ELLA_HUB_API_KEY_EXPIRATION_IN_DAYS', 14)
STATES_CACHE_TIMEOUT = getattr(settings, 'ELLA_HUB_STATES_CACHE_TIMEOUT', 5 * 60)
THUMBNAIL_FORMAT = getattr(settings, 'ELLA_HUB_THUMBNAIL_FORMAT', None)
