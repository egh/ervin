#Copyright (C) 2007-2009, Erik Hetzner

#This file is part of Ervin.  Ervin is free software: you can
#redistribute it and/or modify it under the terms of the GNU General
#Public License as published by the Free Software Foundation, either
#version 3 of the License, or (at your option) any later version.

#Ervin is distributed in the hope that it will be useful, but WITHOUT
#ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#for more details.

#You should have received a copy of the GNU General Public License
#along with Ervin.  If not, see <http://www.gnu.org/licenses/>.

from urllib2 import urlopen
from os import popen
from django.db import models
from django.conf import settings
import re, ervin.conf

class Minter(object):
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
        cmd = "cd %s && %s mint %d" % (self.location, ervin.conf.NOID_BIN, self.at_once)
        
        return popen(cmd).read()

class NoidField(models.CharField):
    def formfield(self, **kwargs): return None

    def get_internal_type(self):
        return "CharField"
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 6)
        kwargs['noid_dir'] = kwargs.get('noid_dir', ervin.conf.NOID_DIR)
        self.minter = LocalMinter(kwargs['noid_dir'])
        del(kwargs['noid_dir'])
        models.CharField.__init__(self, *args, **kwargs)

    def pre_save(self, model_instance, add):
        value = super(NoidField, self).pre_save(model_instance, add)
        if (not value):
            value = self.minter.mint()
            setattr(model_instance, self.attname, value)
        return value
