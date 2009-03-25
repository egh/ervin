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

import solango
from ervin.models import *
from solango.solr import utils

class MultiValuedField(object):
    def __unicode__(self):
        print "*"
        if isinstance(self.value, list):
            return "".join(['<field name="%s"><![CDATA[%s]]></field>\n'%(self.get_name(), utils._from_python(v)) for v in self.value])
        else:
            return '<field name="%s"><![CDATA[%s]]></field>\n'%(self.get_name(), utils._from_python(self.value))

class MultiValuedTextField(MultiValuedField, solango.fields.TextField):
    dynamic_suffix = "t"
    type="text"    

class MultiValuedCharField(MultiValuedField, solango.fields.CharField):
    dynamic_suffix = "s"
    type="string"

class OnlineEditionDocument(solango.SearchDocument):
    title = solango.fields.CharField(copy=True)
    author = MultiValuedTextField(multi_valued=True,copy=True)
    author_facet = MultiValuedCharField(multi_valued=True,stored=False)
    content = solango.fields.TextField(copy=True)

    def transform_title(self,instance):
        return instance.title

    def transform_author(self, instance):
        return [ unicode(a) for a in instance.authors.all() ]

    def transform_author_facet(self, instance):
        return [ unicode(a) for a in instance.authors.all() ]

    def transform_content(self, instance):
        if instance.html.data:
            retval = re.sub(r"<[^>]*?>", "", instance.html.data)
            return retval
        else:
            return None

solango.register(OnlineEdition, OnlineEditionDocument)
