import urllib, httplib2, simplejson

class FakeCache():
    def get(self, key):
        return None
    def set(self, *args):
        return None

try:
    from django.core.cache import cache
    CACHE = cache
except:
    CACHE = FakeCache()

HTTP = httplib2.Http("/tmp/httpcache")

CACHE_TIME=600

def ol_query(q):
    resp, content = HTTP.request("http://openlibrary.org/api/things?query=%s"%(urllib.quote(q)))
    return simplejson.loads(content)

class LazyThing(dict):
    def __init__(self, key):
        if not(key.startswith('/')): 
            self._key = "/%s"%(key)
        else:
            self._key = key
        self._populated = False

    def _populate(self):
        cached = CACHE.get("ol_%s"%(self._key))
        if cached != None:
            self._populate_from_value(cached)
        else:
            self._populate_from_ol()

    def _populate_from_value(self, cached):
        for k in cached.keys():
            self[k] = cached[k]
        self._populated = True
        self._populate_hook()

    def _populate_from_ol(self):
        resp, content = HTTP.request("http://openlibrary.org/api/get?key=%s" %(self._key), "GET")
        r = simplejson.loads(content)
        if r['status'] == 'ok':
            CACHE.set("ol_%s"%(self._key), r['result'], CACHE_TIME)
            self._populate_from_value(r['result'])

    def _populate_hook(self):
        pass

    def __getitem__(self, key):
        if not(self._populated):
            self._populate()
        return super(LazyThing,self).__getitem__(key)

    def keys(self):
        if not(self._populated):
            self._populate()
        return super(LazyThing,self).keys()

class ThingEdition(LazyThing):
    def _populate_hook(self):
        if self.has_key('authors'):
            self['_authors'] = self['authors']
            self['authors'] = [ ThingAuthor(a['key']) for a in self['_authors'] ]
        if self.has_key('languages'):
            self['_languages'] = self['languages']
            self['languages'] = [ ThingLanguage(l['key']) for l in self['_languages'] ]

    def __init__(self, key):
        return super(ThingEdition,self).__init__(key)

class ThingLanguage(LazyThing):
    def __unicode__(self):
        return self['name']
    def __init__(self, key):
        return super(ThingLanguage,self).__init__(key)

class ThingAuthor(LazyThing):
    def editions(self):
        r = ol_query("{\"type\":\"\\/type\\/edition\", \"authors\":\"%s\"}"%(str(self._key)))
        if r['status'] == 'ok':
            return [ ThingEdition(key) for key in r['result']]
        else: return None

    def fulltext_editions(self):
        r = ol_query("{\"type\":\"\\/type\\/edition\", \"authors\":\"%s\", \"ocaid~\":\"*\"}"%(str(self._key)))
        if r['status'] == 'ok':
            print r['result']
            return [ ThingEdition(key) for key in r['result']]
        else: return None

    def __init__(self, key):
        return super(ThingAuthor,self).__init__(key)

    def __unicode__(self):
        return self['name']

def search(keyword):
    url = "http://openlibrary.org/api/search?q={\"query\":\"%s\"}"%(urllib.quote(keyword))
    resp, content = HTTP.request(url)
    results = simplejson.loads(content)
    return [ ThingEdition(key) for key in results['result'] ]

# {"name": "William Shakespeare", "entity_type": "person", "death_date": "1616", "wikipedia": "http://en.wikipedia.org/wiki/William_Shakespeare", "last_modified": {"type": "/type/datetime", "value": "2009-01-09T14:21:25.840373"}, "key": "/a/OL9388A", "birth_date": "1564", "personal_name": "William Shakespeare", "type": {"key": "/type/author"}, "id": 23567, "revision": 2}}

