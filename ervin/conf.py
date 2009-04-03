from django.conf import settings

FEED_AUTHOR = getattr(settings, "ERVIN_FEED_AUTHOR", "John Doe")
FEED_EMAIL = getattr(settings, "ERVIN_FEED_EMAIL", "john.doe@example.org")
RECENT_DOCUMENTS_FEED_TITLE = getattr(settings, "ERVIN_RECENT_DOCUMENTS_FEED_TITLE", "Recent documents")
RECENT_DOCUMENTS_FEED_ID = getattr(settings, "ERVIN_RECENT_DOCUMENTS_FEED_ID", "BROKEN FEED ID")
RECENT_PUBLICATIONS_FEED_TITLE = getattr(settings, "ERVIN_RECENT_PUBLICATIONS_FEED_TITLE", "Recent publications")
RECENT_PUBLICATIONS_FEED_ID = getattr(settings, "ERVIN_RECENT_PUBLICATIONS_FEED_ID", "BROKEN FEED ID")
NOID_DIR = getattr(settings, 'ERVIN_NOID_DIR', 'noid/')
