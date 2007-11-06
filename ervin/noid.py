from urllib2 import urlopen
from os import popen
from django.db import models
import re

class Minter():
    def __init__(self, location, at_once=1):
        self.location = location
        self.at_once = at_once
        self.cache = []
    def mint(self):
        if (len(self.cache) == 0):
            self.fill_cache()
        return self.cache.pop()
    def fill_cache(self):
        my_re = re.compile("id:\\s+([^\\s]+)")
        data = self.read_ids()
        def f(l):
            return my_re.match(l) != None
        lines = filter(f, data.split("\n"))
        self.cache = self.cache + [my_re.match(l).group(1) for l in lines]

class RemoteMinter(Minter):
    def read_ids(self):
        return urlopen(self.location + "?mint+" + str(self.at_once)).read()

class LocalMinter(Minter):
    def read_ids(self):
        cmd = "cd %s && noid mint %s" % (self.location, self.at_once)
        return popen(cmd).read()
    

class NoidField(models.CharField):
    def get_internal_type(self):
        return models.CharField.__name__
    
    def __init__(self, location, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 20)
        self.minter = LocalMinter(location)
        super(NoidField, self).__init__(self, *args,**kwargs)
        self.editable = False
    
    def pre_save(self, model_instance, add):
        value = super(NoidField, self).pre_save(model_instance, add)
        if (not value):
            value = self.minter.mint()
            setattr(model_instance, self.attname, value)
        return value
        
