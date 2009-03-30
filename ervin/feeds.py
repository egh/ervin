from django.contrib.sites.models import Site
from atompub.atom import Feed
from ervin.models import *
import ervin.conf

class EditionFeed(Feed):
    def item_id(self, ed):
        return 'http://%s%s' % (Site.objects.get_current().domain, ed.get_absolute_url())

    def item_title(self, ed):
        return ed.title

    def item_updated(self, ed):
        return ed.date
    
    def item_published(self, ed):
        return ed.date

    def item_links(self, ed):
        return [{'href': 'http://%s%s' % (Site.objects.get_current().domain, ed.get_absolute_url())}]
    
    def item_content(self, ed):
        return ({'type':'html'}, ed.html.data)
    
    def item_source(self, ed):
        if ed.work.source:
            return {'title':ed.work.source}
        else: return None
    
    def item_authors(self, ed):
        return [ {'name': unicode(a)} for a in ed.authors.all() ]

class RecentFeed(EditionFeed):
    feed_id = ervin.conf.RECENT_DOCUMENTS_FEED_ID
    feed_title = ervin.conf.RECENT_DOCUMENTS_FEED_TITLE
    feed_authors = [{'name':  ervin.conf.FEED_AUTHOR,
                     'email': ervin.conf.FEED_EMAIL}]

    def items(self):
        return OnlineEdition.objects.order_by('-date').filter(content_db__gt=0)[0:20]
