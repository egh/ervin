from django.conf import settings

FEED_AUTHOR = getattr(settings, "ERVIN_FEED_AUTHOR", "John Doe")
FEED_EMAIL = getattr(settings, "ERVIN_FEED_EMAIL", "john.doe@example.org")
RECENT_DOCUMENTS_FEED_TITLE = getattr(settings, "ERVIN_RECENT_DOCUMENTS_FEED_TITLE", "Recent Documents")
RECENT_DOCUMENTS_FEED_ID = getattr(settings, "ERVIN_RECENT_DOCUMENTS_FEED_ID", "BROKEN FEED ID")
