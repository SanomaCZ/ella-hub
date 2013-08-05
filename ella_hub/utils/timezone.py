import datetime

try:
    from django.utils import timezone
except ImportError:
    now = datetime.datetime.now
else:
    tz_localtime = getattr(timezone, 'template_localtime', timezone.localtime)

    def now():
        """
        Used instead of now function from tastypie.utils.timezone
        becouse this raise Exception if you have USE_TZ to False
        in project settings
        """
        return tz_localtime(timezone.now())
