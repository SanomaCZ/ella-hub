try:
    # try import offset-aware datetime from Django >= 1.4
    from django.utils.timezone import now
except ImportError:
    # backward compatibility with Django < 1.4 (offset-naive datetimes)
    from datetime import datetime
    now = datetime.now
