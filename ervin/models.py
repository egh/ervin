# -*- coding: utf-8 -*-
#Copyright (C) 2007 Erik Hetzner

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

from string import lower
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.conf import settings
from noid import LocalMinter
from noid import NoidField
from django.contrib import admin
import re, os, md5

class FreeformDateField(models.CharField):
    def get_internal_type(self):
        return models.CharField.__name__
    
    def pre_save(self, model_instance, add):
        value = super(FreeformDateField, self).pre_save(model_instance, add)
        model_instance.__dict__[self.attname + "_sort"] = self.__canonicalize_date__(value)
        return value
    
    def __canonicalize_date__(self, value):
        stripped = value.replace("[","").replace("]","").replace("?","")
        return stripped

class MyFileField(models.FileField):
    def get_internal_type(self):
        return "FileField"    

    def contribute_to_class(self, cls, name):
        def _make_filename(filename, data):
            (basename, ext) = os.path.splitext(filename)
            m = md5.new()
            for d in data['content']:
                m.update(d)
            return "%s%s"%(m.hexdigest(), ext)

        super(MyFileField, self).contribute_to_class(cls, name)
        setattr(cls, 'save_%s_file' % self.name, lambda instance, filename, raw_contents, save=True: instance._save_FIELD_file(self, _make_filename(filename, raw_contents), raw_contents, save))

class SubjectMixin(object):
    def get_subject(self):
        s = None
        try: s = Subject.objects.get (object_id=self.noid)
        except Subject.DoesNotExist: s = create_subject (self)
        return s

    def delete_hook(self):
        which_type = ContentType.objects.get(model=lower(type(self).__name__),
                                             app_label='ervin')
        try:
            s = Subject.objects.get(content_type=which_type,
                                    object_id=self.pk)
            s.delete()
        except:
            pass

    def create_subject(self):
        t = ContentType.objects.get(model=lower(type(self).__name__),
                                    app_label='ervin')
        s = Subject(content_type=t,object_id=self.pk)
        s.save()
        return s

    def save_hook(self):
        try:
            Subject.objects.get(object_id=self.pk)
        except Subject.DoesNotExist:
            create_subject(item)

class Subject(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=6,primary_key=True)
    content_object = generic.GenericForeignKey()
    def get_absolute_url(self): return "/%s"%(self.object_id)
    def __unicode__(self): return unicode(self.content_object)
    def __cmp__(self, other):
      return cmp(unicode(self).lower(), unicode(other).lower())

class Person(models.Model, SubjectMixin):
    surname = models.CharField(max_length=200)
    forename = models.CharField(max_length=200)
    dates = models.CharField(max_length=20,blank=True)
    noid = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)
    def get_absolute_url(self): return "/%s"%(self.noid)
    def save(self):
        super(Person, self).save()
        save_hook(self)
    def __hash__(self): return hash(self.pk)
    def __unicode__(self):
        if self.dates:
            return "%s, %s (%s)"%(self.surname, self.forename, self.dates)
        else: 
            return "%s, %s"%(self.surname, self.forename)
    class Meta:
        ordering=['surname','forename']
    class Admin: pass

admin.site.register(Person)
    
class Section(models.Model):
    name = models.CharField(max_length=100)
    def __unicode__(self): return self.name
    class Admin: pass

class Concept(models.Model, SubjectMixin):
    name = models.CharField(max_length=200)
    noid = NoidField(settings.NOID_DIR, max_length=6,primary_key=True)
    def get_absolute_url(self): return "/%s"%(self.noid)
    def save(self):
        super(Concept, self).save()
        save_hook(self)
    def delete(self):
        delete_hook(self)
        super(Concept, self).delete()
    def __unicode__(self): return self.name
    class Admin: pass   

admin.site.register(Concept)
    
class Work(models.Model, SubjectMixin):
    title = models.TextField(max_length=200,blank=True)
    def get_title(self):
        return self.title
    filter_horizontal = ('authors', 'subjects')
    authors = models.ManyToManyField(Person,verbose_name="Authors",
                                     related_name="authored",
                                     blank=True)
    subjects = models.ManyToManyField(Subject,blank=True)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)
    partof = models.ForeignKey("self",blank=True,null=True,related_name="parts",db_column='partof_noid',to_field='noid')
    sections = models.ManyToManyField(Section,blank=True)
    noid = NoidField(settings.NOID_DIR, max_length=6,primary_key=True)
    date = FreeformDateField(max_length=128,blank=True,null=True)
    date_sort = models.CharField(max_length=128,blank=True,null=True)
    sort = models.CharField(max_length=128,editable=False)
    class Meta:
        ordering=['sort']
    class Admin: 
        fields = (
            ("Main", {'fields': ('title', 'partof','description',
                                 'note', 'authors')}),
            ("Classification",  {'classes':'collapse',
                        'fields': ('subjects', 'sections')}),
            #("Editions", {'classes':'collapse',
            #'fields': ("catalogeditions", "onlineedition_set")}),
            )
        js = ['js/tiny_mce/tiny_mce.js', 'js/textareas.js']
    def get_absolute_url(self): return "/%s"%(self.noid)
    def save(self):
        key = None
        title_key = ervin.templatetags.catalog.sort_friendly(self.title)
        if len(self.authors.all()) > 0:
            first_author_key = ervin.templatetags.catalog.sort_friendly(ervin.templatetags.catalog.inverted_name(self.authors.order_by('surname','forename').all()[0]))
            key = "%s%s"%(first_author_key,title_key)
        else: key = title_key
        self.sort = key[:128].lower()

        super(Work, self).save() 
        try:
            expression = Expression.objects.get(work=self)
        except Expression.DoesNotExist:
            e = Expression(work=self)
            e.save()
        
    def __unicode__(self):
        if self.partof == None:
            return self.title
        else:
            return "%s (in %s)"%(self.title, self.partof.title)

admin.site.register(Work)

class Expression(models.Model, SubjectMixin):
    work = models.ForeignKey(Work,
                             to_field='noid',
                             db_column='work_noid',
                             edit_inline=models.STACKED)
    title = models.TextField(max_length=200, blank=True)
    filter_horizontal = ('translators')
    translators = models.ManyToManyField(Person,verbose_name="Translators",
                                         related_name="translated",
                                         blank=True)
    noid = NoidField(settings.NOID_DIR,
                     max_length=6,
                     primary_key=True,
                     core=True)
    def get_manifestations(self):
        return list(self.onlineedition_set.all()) + list(self.physicaledition_set.all())    
    def get_authors(self):
        return self.work.authors
    authors = property(get_authors)
    def get_subjects(self):
        return self.work.subjects
    subjects = property(get_subjects)
    def get_title(self):
        if self.title != None and self.title != '':
            return self.title
        else:
            return self.work.get_title()
    def get_absolute_url(self): return "/%s"%(self.noid)
    def __unicode__(self): return unicode(self.work)

class OnlineEdition(models.Model, SubjectMixin):
    date = FreeformDateField(max_length=128,blank=True,null=True)
    date_sort = models.CharField(max_length=128,blank=True,null=True)
    expression = models.ForeignKey(Expression,
                                   db_column='expression_noid',
                                   to_field='noid')
    title = models.TextField("Title (leave blank if same as expression)", max_length=200, blank=True)
    noid = NoidField(settings.NOID_DIR,max_length=6, primary_key=True)
    def get_work(self):
        return self.expression.work
    work = property(get_work)
    def get_title(self):
        if self.title != None and self.title != '':
            return self.title
        else:
            return self.expression.get_title()
    def get_authors(self):
        return self.expression.authors
    authors = property(get_authors)
    def get_subjects(self):
        return self.expression.subjects
    subjects = property(get_subjects)
    def get_parts(self):
        return self.work.parts
    parts = property(get_parts)
    def get_items(self):
        return list(self.remoteitem_set.all())
    items = property(get_items)
    def __unicode__(self): return unicode(self.work)
    def get_absolute_url(self): return "/%s"%(self.noid)
    class Admin:
        js = ['js/tiny_mce/tiny_mce.js', 'js/textareas.js']



admin.site.register(OnlineEdition)
    
class PhysicalEdition(models.Model, SubjectMixin):
    date = FreeformDateField(max_length=128,blank=True, null=True)
    date_sort = models.CharField(max_length=128,blank=True,null=True)
    publisher = models.CharField(max_length=100,core=True)
    #in_series = models.ForeignKey(Work,edit_inline=False,related_name="in_series",null=True,blank=True,limit_choices_to={'type': "series"})
    series_count = models.IntegerField(blank=True)
    isbn10 = models.CharField("ISBN-10",max_length=13,blank=True)
    isbn13 = models.CharField("ISBN-13",max_length=16,blank=True)
    description = models.CharField("Physical description",max_length=100,blank=True,null=True)
    price_dollars = models.DecimalField('Price ($)',
                                        max_digits=5,
                                        decimal_places=2,
                                        blank=True,
                                        null=True)
    price_pounds = models.DecimalField('Price (£)',
                                       max_digits=5,
                                       decimal_places=2,
                                       blank=True,
                                       null=True)
    available = models.BooleanField()
    def get_work(self): return self.expression.work
    work = property(get_work)
    expression = models.ForeignKey(Expression,
                                   to_field='noid',
                                   db_column='expression_noid')
    noid = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)
    def get_title(self): return self.work.title
    def get_authors(self): return self.expression.authors
    authors = property(get_authors)
    def get_subjects(self): return self.work.subjects
    subjects = property(get_subjects)
    def get_parts(self): return self.work.parts
    parts = property(get_parts)
    def __unicode__(self):
        return "%s(%s)"%(self.work.title, unicode(self.date))
    class Admin:
        js = ['js/tiny_mce/tiny_mce.js', 'js/textareas.js']   
    def get_absolute_url(self): return "/%s"%(self.noid)
    def get_items(self): return None
    
class Place(models.Model, SubjectMixin):
    name = models.CharField(max_length=200)
    noid = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)
    def get_absolute_url(self): return "/%s"%(self.noid)
    def save(self):
        super(Place, self).save()
        save_hook(self)
    def delete(self):
        delete_hook(self)
        super(Place, self).delete()
    def __unicode__(self): return self.name
    class Admin: pass

admin.site.register(PhysicalEdition)

class Organization(models.Model, SubjectMixin):
    name = models.CharField(max_length=200)
    noid = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)
    def get_absolute_url(self): return "/%s"%(self.noid)
    def save(self):
        super(Organization, self).save()
        save_hook(self)
    def delete(self):
        delete_hook(self)
        super(Organization, self).delete()
    def __unicode__(self): return self.name
    class Admin: pass   

class Event(models.Model, SubjectMixin):
    name = models.CharField(max_length=200)
    noid = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)
    def get_absolute_url(self): return "/%s"%(self.noid)
    def save(self):
        super(Event, self).save()
        save_hook(self)
    def delete(self):
        delete_hook(self)
        super(Event, self).delete()
    def __unicode__(self): return self.name
    class Admin: pass

class FrbrObject(models.Model, SubjectMixin):
    name = models.CharField(max_length=200)
    noid = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)
    def get_absolute_url(self): return "/%s"%(self.noid)
    def save(self):
        super(FrbrObject, self).save()
        save_hook(self)
    def delete(self):
        delete_hook(self)
        super(FrbrObject, self).delete()
    def __unicode__(self): return self.name
    class Admin: pass
    class Meta:
        verbose_name = "Object"

class RemoteContent(models.Model):
    edition = models.ForeignKey('OnlineEdition', 
                                db_column='edition_noid',
                                to_field='noid',
                                edit_inline=models.STACKED,
                                related_name='content_remote')
    name = models.CharField(max_length=100,
                            core=True)
    noid = NoidField(settings.NOID_DIR, 
                     max_length=6,
                     primary_key=True)
    url = models.CharField(max_length=1024)
    def __unicode__(self): return self.name
    def get_absolute_url(self): return self.url 

class DbContent(models.Model): 
    edition = models.ForeignKey('OnlineEdition', 
                                db_column='edition_noid',
                                to_field='noid',
                                edit_inline=models.STACKED,
                                related_name='content_db')
    name = models.CharField(max_length=100, 
                            core=True)
    data = models.TextField(blank=True,
                            core=True)
    noid = NoidField(settings.NOID_DIR, 
                     primary_key=True,
                     max_length=6)
    def __unicode__(self): return self.name
    def get_absolute_url(self): return "/%s"%(self.noid)

ext2mime_map = { '.pdf' : 'application/pdf' }
mime2ext_map = dict([(d[1],d[0]) for d in ext2mime_map.items()])

class FileContent(models.Model):
    edition = models.ForeignKey('OnlineEdition', db_column='edition_noid',edit_inline=models.STACKED, related_name='content_file')
    name = models.CharField(max_length=100,core=True)
    filename = MyFileField(upload_to="data")
    mimetype = models.CharField(max_length=100,editable=False)
    noid = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)
    def get_ext(self):
        if mime2ext_map.has_key(self.mimetype):
            return mime2ext_map[self.mimetype]
        else: return None
    def get_mimetype_from_ext(self, ext):
        if ext2mime_map.has_key(ext):
            return ext2mime_map[ext]
        else: return None
    def __unicode__(self): return self.name
    def get_absolute_url(self): return "/%s"%(self.noid)
    def save(self):
        (basename, ext) = os.path.splitext(self.filename)
        self.mimetype = self.get_mimetype_from_ext(ext)
        super(FileContent, self).save()
        
    
