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
from django.template.loader import render_to_string

class MultiValuedField(object):
    def __unicode__(self):
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

class EditionDocument(solango.SearchDocument):
    title = solango.fields.CharField(copy=True)
    author = MultiValuedTextField(multi_valued=True,copy=True)
    author_facet = MultiValuedCharField(multi_valued=True,stored=False)
    translator = MultiValuedTextField(multi_valued=True,copy=True)
    mysort = solango.fields.CharField(copy=False,indexed=True,stored=False)
    subject = MultiValuedTextField(multi_valued=True,copy=True)
    subject_facet = MultiValuedCharField(multi_valued=True,stored=False)

    def transform_title(self,instance):
        return instance.title

    def transform_author(self, instance):
        return [ unicode(a) for a in instance.authors.all() ]

    def transform_translator(self, instance):
        return [ unicode(a) for a in instance.authors.all() ]

    def transform_author_facet(self, instance):
        return [ unicode(a) for a in instance.authors.all() ] + [ unicode(a) for a in instance.translators.all() ]

    def transform_subject(self, instance):
        return [ unicode(a) for a in instance.subjects.all() ]

    def transform_subject_facet(self, instance):
        return [ unicode(a) for a in instance.subjects.all() ]

    def transform_mysort(self, instance):
        return instance.sort

    class Media:
        template = "edition_search.html"
    
class OnlineEditionDocument(EditionDocument):
    content = solango.fields.TextField(copy=True)
    date = solango.fields.DateField(copy=True)

    def transform_content(self, instance):
        if instance.html.data:
            retval = re.sub(r"<[^>]*?>", "", instance.html.data)
            return retval
        else:
            return None

    def transform_date(self, instance):
        if instance.date == '' or instance.date == None:
            return None
        else: return instance.date
    
    def is_indexable(self, instance):
	html = instance.html
	return (html != None) and (html.data != "")   

    def render_html(self):
        edition = OnlineEdition.objects.get(pk=self.pk_field.value)
        return render_to_string(self.template, {'document' : self,
                                                'edition'  : edition })

class PhysicalEditionDocument(EditionDocument):
    def render_html(self):
        edition = PhysicalEdition.objects.get(pk=self.pk_field.value)
        return render_to_string(self.template, {'document' : self,
                                                'edition'  : edition })

solango.register(OnlineEdition, OnlineEditionDocument)
solango.register(PhysicalEdition, PhysicalEditionDocument)
