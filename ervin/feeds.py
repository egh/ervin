from django.contrib.sites.models import Site
from atompub.atom import Feed
from ervin.models import *
from django.db.models import Q
import ervin.conf

class NewsFeed(Feed):
    feed_id = ervin.conf.NEWS_FEED_ID
    feed_title = ervin.conf.NEWS_FEED_TITLE
    feed_authors = [{'name':  ervin.conf.FEED_AUTHOR,
                     'email': ervin.conf.FEED_EMAIL}]

    def items(self):
        return Page.objects.filter(news=True).order_by('-created')[0:10]

    def item_id(self, item):
        return 'http://%s%s' % (Site.objects.get_current().domain, item.get_absolute_url())

    def item_title(self, item):
        return item.title

    def item_updated(self, item):
        return item.updated
    
    def item_published(self, item):
        return item.created

    def item_links(self, item):
        return [{'href': 'http://%s%s' % (Site.objects.get_current().domain, item.get_absolute_url())}]
    
    def item_content(self, item):
        return ({'type':'html'}, item.content)
    
class EditionFeed(Feed):
    def _is_image(self, ed):
        return hasattr(ed, 'image') and hasattr(ed.image, 'mimetype')

    def _is_html(self, ed):
        return hasattr(ed, 'html') and hasattr(ed.html, 'data')

    def item_id(self, ed):
        return 'http://%s%s' % (Site.objects.get_current().domain, ed.get_absolute_url())

    def item_title(self, ed):
        return ed.title

    def item_updated(self, ed):
        return ed.date
    
    def item_published(self, ed):
        return ed.date

    def item_links(self, ed):
        retval = [{'href': 'http://%s%s' % (Site.objects.get_current().domain, ed.get_absolute_url())}]
        if self._is_image(ed):
            retval.append({'rel': 'self', 
                           'href': 'http://%s%s'%(Site.objects.get_current().domain, ed.image.get_absolute_url()),
                           'type': ed.image.mimetype, 
                           'title': ed.title,
                           'length': ed.image.size})
        return retval

    def item_content(self, ed):
        if self._is_html(ed):
            return ({'type':'html'}, ed.html.data)
        elif self._is_image(ed):
            uri = 'http://%s%s?x=400'%(Site.objects.get_current().domain, ed.image.get_absolute_url())
            return ({'type': 'html'}, '<p><img alt="%s" src="%s"></p>'%(ed.title, uri))
        else:
            return None

    def item_source(self, ed):
        if ed.work.source:
            return {'title':ed.work.source}
        else: return None
    
    def item_authors(self, ed):
        return [ {'name': unicode(a)} for a in ed.authors.all() ]
        
        
class RecentDocumentsFeed(EditionFeed):
    feed_id = ervin.conf.RECENT_DOCUMENTS_FEED_ID
    feed_title = ervin.conf.RECENT_DOCUMENTS_FEED_TITLE
    feed_authors = [{'name':  ervin.conf.FEED_AUTHOR,
                     'email': ervin.conf.FEED_EMAIL}]

    def items(self):
        retval = []
        for o in OnlineEdition.objects.order_by('-date')[0:30]:
            if len(o.content) != 0:
                retval.append(o)
            if len(retval) == 20: break
        return retval

class RecentPublicationsFeed(EditionFeed):
    feed_id = ervin.conf.RECENT_PUBLICATIONS_FEED_ID
    feed_title = ervin.conf.RECENT_PUBLICATIONS_FEED_TITLE
    feed_authors = [{'name':  ervin.conf.FEED_AUTHOR,
                     'email': ervin.conf.FEED_EMAIL}]

    def items(self):
        return PhysicalEdition.objects.order_by('-date_sort')[0:10]
