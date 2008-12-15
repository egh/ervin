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

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from noid import LocalMinter, NoidField
import re, os, md5, ervin.templatetags.ervin, isbn

class FreeformDateField(models.CharField):
    def get_internal_type(self):
        return models.CharField.__name__
    
    def pre_save(self, model_instance, add):
        value = super(FreeformDateField, self).pre_save(model_instance, add)
        model_instance.__dict__[self.attname + "_sort"] = self.__canonicalize_date__(value)
        return value
    
    def __canonicalize_date__(self, value):
        if value != None:
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
        try: s = Subject.objects.get (object_id=self.pk)
        except Subject.DoesNotExist: s = self.create_subject()
        return s

    def _subject_delete_hook(self):
        s = Subject.objects.get(object_id=self.pk)
        s.delete()

    def create_subject(self):
        t = ContentType.objects.get(model=type(self).__name__.lower(),
                                    app_label='ervin')
        s = Subject(content_type=t,object_id=self.pk)
        s.save()
        return s

    def _subject_save_hook(self):
        try: Subject.objects.get(object_id=self.pk)
        except Subject.DoesNotExist: self.create_subject()

class BibSortMixin(object):
    def _sort_save_hook(self):
        key = None
        title_key = ervin.templatetags.ervin.sort_friendly(self.title)
        author = self.first_author
        if author != None:
            author_key = ervin.templatetags.ervin.sort_friendly(ervin.templatetags.ervin.inverted_name(author))
            key = "%s%s"%(author_key,title_key)
        else: key = title_key
        self.sort = re.sub("[\":,.'\[\]\(\)\?\&-]" ,'', key[:128].lower())

class Subject(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=6,primary_key=True)
    content_object = generic.GenericForeignKey()
    sort = models.CharField(max_length=128)

    def get_absolute_url(self): return "/%s"%(self.object_id)

    def __unicode__(self): return unicode(self.content_object)

    def __cmp__(self, other):
      return cmp(unicode(self).lower(), unicode(other).lower())

    def save(self):
        self.sort = ervin.templatetags.ervin.sort_friendly(unicode(self))[:128]
        super(Subject, self).save()

    class Meta:
        ordering = ['sort']

class Person(models.Model, SubjectMixin):
    surname = models.CharField(max_length=200)
    forename = models.CharField(max_length=200)
    dates = models.CharField(max_length=20,blank=True)
    id = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)

    def get_absolute_url(self): return "/%s"%(self.pk)

    def save(self):
        super(Person, self).save()
        self._subject_save_hook()

    def delete(self):
        self._subject_delete_hook()
        super(Person, self).delete()

    def __hash__(self): return hash(self.pk)

    def __unicode__(self):
        if self.dates:
            return "%s, %s (%s)"%(self.surname, self.forename, self.dates)
        else: 
            return "%s, %s"%(self.surname, self.forename)

    class Meta:
        ordering=['surname','forename']
    
class Concept(models.Model, SubjectMixin):
    name = models.CharField(max_length=200)
    id = NoidField(settings.NOID_DIR, max_length=6,primary_key=True)

    def get_absolute_url(self): return "/%s"%(self.pk)

    def save(self):
        super(Concept, self).save()
        self._subject_save_hook()

    def delete(self):
        self._subject_delete_hook()
        super(Concept, self).delete()

    def __unicode__(self): return self.name

    class Meta:
        ordering=['name']

WORK_FORMS = (('series', 'Serial'),
              ('article', 'Article'),
              ('monograph', 'Monograph'))

class Work(models.Model, SubjectMixin, BibSortMixin):
    work_title = models.TextField(max_length=200,blank=True,db_column='title')
    authors = models.ManyToManyField(Person, 
                                     through='Authorship',
                                     related_name='authored',
                                     blank=True)
    subjects = models.ManyToManyField(Subject,blank=True)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)
    part_of = models.ForeignKey("self",blank=True,null=True,related_name="parts")
    id = NoidField(settings.NOID_DIR, max_length=6,primary_key=True)
    date = FreeformDateField(max_length=128,blank=True,null=True)
    date_sort = models.CharField(max_length=128,blank=True,null=True,editable=False)
    sort = models.CharField(max_length=128,editable=False)
    form = models.CharField(max_length=128, choices=WORK_FORMS)
    source = models.TextField(blank=True)
    
    def _all_subjects(self):
        all_works = [self] + list(self.parts.all())
        return Subject.objects.filter(work__in=all_works).distinct()

    def _first_author(self): 
        authors = self.authors.filter(authorship__primary=True).all()
        if (authors.count() > 0): return authors[0]
        else:
            authors = self.authors.order_by('surname','forename').all()
            if (authors.count() > 0): return authors[0]
            else: return None

    def _title(self):
        return self.work_title

    def get_absolute_url(self): return "/%s"%(self.pk)

    def save(self):
        self._sort_save_hook()
        super(Work, self).save() 
        try:
            expression = Expression.objects.get(work=self)            
        except Expression.DoesNotExist:
            e = Expression(work=self)
            e.save()
        # save hook to update sort keys on children
        for e in self.expression_set.all():
            e.save()

    def __unicode__(self):
        if self.part_of == None:
            return self.title
        else:
            return "%s (in %s)"%(self.title, self.part_of.title)

    title = property(_title)
    first_author = property(_first_author)
    all_subjects = property(_all_subjects)
    
    class Meta:
        ordering=['sort']

class Authorship(models.Model):
    person = models.ForeignKey(Person)
    work = models.ForeignKey(Work)
    primary = models.BooleanField(verbose_name="Primary?")

    class Meta:
        db_table = 'ervin_work_authors'
        verbose_name = "Author"

    def save(self):
        super(Authorship, self).save() 
        self.work.save()
        # update sort key in work

class Expression(models.Model, SubjectMixin,BibSortMixin):
    work = models.ForeignKey(Work)
    expression_title = models.TextField(max_length=200, blank=True, db_column='title')
    translators = models.ManyToManyField(Person,
                                         through='ExpressionTranslator',
                                         verbose_name="Translators",
                                         related_name="translated",
                                         blank=True)
    id = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)
    sort = models.CharField(max_length=128,editable=False)
    
    def _first_author(self): 
        return self.work.first_author

    def _editions(self):
        return list(self.onlineedition_set.all()) + list(self.physicaledition_set.all())    

    def _authors(self):
        return self.work.authors

    def _subjects(self):
        return self.work.subjects

    def _title(self):
        if self.expression_title != None and self.expression_title != '':
            return self.expression_title
        else:
            return self.work.title

    def get_absolute_url(self): return "/%s"%(self.pk)

    def __unicode__(self): return unicode(self.work)

    def save(self):
        self._sort_save_hook()
        super(Expression, self).save() 
        # save hook to update sort keys on children
        for e in self.editions:
            e.save()

    authors = property(_authors)
    subjects = property(_subjects)
    title = property(_title)
    editions = property(_editions)
    first_author = property(_first_author)
    
    class Meta:
        ordering=['sort']

class ExpressionTranslator(models.Model):
    person = models.ForeignKey(Person)
    expression = models.ForeignKey(Expression)

    class Meta:
        db_table = 'ervin_expression_translators'
        verbose_name = "Translator"

#    def save(self):
#        super(Authorship, self).save() 
#        self.work.save()

class OnlineEdition(models.Model, SubjectMixin,BibSortMixin):
    date = models.DateTimeField(null=True)
    expression = models.ForeignKey(Expression, verbose_name="Work")
    edition_title = models.TextField(max_length=200, editable=False, blank=True,db_column='title')
    #numbering = models.CharField("Numbering", max_length=128, blank=True)
    id = NoidField(settings.NOID_DIR,max_length=6, primary_key=True)
    sort = models.CharField(max_length=128,editable=False)

    def _first_author(self): 
        return self.work.first_author

    def _html(self): return self._get_by_mimetype("text/html")

    def _get_by_mimetype(self, mimetype):
        for c in self.content:
            if c.mimetype == mimetype: return c
        return None

    def _pdf(self): return self._get_by_mimetype("application/pdf")

    def _content(self):
        return (list(self.content_db.all()) + list(self.content_file.all()))

    def get_multiple_contents(self): 
        return ((self.content_db.count() + self.content_file.count()) > 1)

    def _work(self):
        return self.expression.work

    def _title(self):
        if self.edition_title != None and self.edition_title != '':
            return self.edition_title
        else:
            return self.expression.title

    def _authors(self):
        return self.expression.authors

    def _subjects(self):
        return self.expression.subjects

    def get_parts(self):
        return self.work.parts

    def get_items(self):
        return list(self.remoteitem_set.all())

    def __unicode__(self): return unicode(self.work)

    def get_absolute_url(self): return "/%s"%(self.pk)

    def save(self):
        self._sort_save_hook()
        super(OnlineEdition, self).save() 

    authors = property(_authors)
    items = property(get_items)
    parts = property(get_parts)
    subjects = property(_subjects)
    title = property(_title)
    work = property(_work)
    content = property(_content)
    multiple_contents = property(get_multiple_contents)
    pdf = property(_pdf)
    html = property(_html)
    first_author = property(_first_author)

    class Meta:
        ordering = ['sort']
    
class PhysicalEdition(models.Model, SubjectMixin,BibSortMixin):
    edition_title = models.TextField("Title (leave blank if same as expression)", max_length=200, blank=True,db_column='title')
    date = FreeformDateField(max_length=128,blank=True, null=True)
    date_sort = models.CharField(max_length=128,blank=True,null=True,editable=False)
    publisher = models.CharField(max_length=100)
    #in_series = models.ForeignKey(Work,edit_inline=False,related_name="in_series",null=True,blank=True,limit_choices_to={'type': "series"})
    #isbn10 = models.CharField("ISBN-10",max_length=13,blank=True)
    def _isbn10(self): 
        if isbn.isValid(self.isbn13): return isbn.toI10(self.isbn13)
        else: return None
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
    available_us = models.BooleanField()
    available_uk = models.BooleanField()
    numbering = models.CharField("Numbering", max_length=128, blank=True)
    sort = models.CharField(max_length=128,editable=False)
    expression = models.ForeignKey(Expression)
    id = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)

    def _available(self):
        return (self.available_uk or self.available_us)
    available = property(_available)

    def _first_author(self): 
        return self.work.first_author
    first_author = property(_first_author)
        
    def _work(self): return self.expression.work
    work = property(_work)

    def _title(self):
        if self.edition_title != None and self.edition_title != '':
            return self.edition_title
        else:
            return self.expression.title
    title = property(_title)

    def _authors(self): return self.expression.authors
    authors = property(_authors)

    def _subjects(self): return self.work.subjects
    subjects = property(_subjects)

    def get_parts(self): return self.work.parts
    parts = property(get_parts)

    def __unicode__(self):
        return "%s(%s)"%(self._title(), unicode(self.date))

    def get_absolute_url(self): return "/%s"%(self.pk)

    def get_items(self): return None
    items = property(get_items)

    def save(self):
        self._sort_save_hook()
        super(PhysicalEdition, self).save() 

    isbn10 = property(_isbn10)

    class Meta:
        ordering = ['sort']
    
class Place(models.Model, SubjectMixin):
    name = models.CharField(max_length=200)
    id = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)

    def get_absolute_url(self): return "/%s"%(self.pk)

    def save(self):
        super(Place, self).save()
        self._subject_save_hook()

    def delete(self):
        self._subject_delete_hook()
        super(Place, self).delete()

    def __unicode__(self): return self.name

    class Meta:
        ordering=['name']

class Organization(models.Model, SubjectMixin):
    name = models.CharField(max_length=200)
    id = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)

    def get_absolute_url(self): return "/%s"%(self.pk)

    def save(self):
        super(Organization, self).save()
        self._subject_save_hook()

    def delete(self):
        self._subject_delete_hook()
        super(Organization, self).delete()

    def __unicode__(self): return self.name

    class Meta:
        ordering=['name']

class Event(models.Model, SubjectMixin):
    name = models.CharField(max_length=200)
    id = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)

    def get_absolute_url(self): return "/%s"%(self.pk)

    def save(self):
        super(Event, self).save()
        self._subject_save_hook()

    def delete(self):
        self._subject_delete_hook()
        super(Event, self).delete()

    def __unicode__(self): return self.name

    class Meta:
        ordering=['name']

class FrbrObject(models.Model, SubjectMixin):
    name = models.CharField(max_length=200)
    id = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)

    def get_absolute_url(self): return "/%s"%(self.pk)

    def save(self):
        super(FrbrObject, self).save()
        self._subject_save_hook()

    def delete(self):
        self._subject_delete_hook()
        super(FrbrObject, self).delete()

    def __unicode__(self): return self.name

    class Meta:
        verbose_name = "Object"
        ordering=['name']

class RemoteContent(models.Model):
    edition = models.ForeignKey('OnlineEdition', 
                                related_name='content_remote')
    name = models.CharField(max_length=100)
    id = NoidField(settings.NOID_DIR, 
                     max_length=6,
                     primary_key=True)
    url = models.CharField(max_length=1024)

    def __unicode__(self): return self.name

    def get_absolute_url(self): return self.url 

class DbContent(models.Model): 
    edition = models.ForeignKey('OnlineEdition', related_name='content_db')
    name = models.CharField(max_length=100,editable=False,blank=True)
    data = models.TextField(blank=True)
    mimetype = models.CharField(max_length=100, editable=False,default="text/html")
    id = NoidField(settings.NOID_DIR, primary_key=True, max_length=6)

    def __unicode__(self): return "%s (%s)"%(self.edition.title, self.name)

    def get_absolute_url(self): return "/%s"%(self.pk)

ext2mime_map = { '.pdf' : 'application/pdf' }
mime2ext_map = dict([(d[1],d[0]) for d in ext2mime_map.items()])

class FileContent(models.Model):
    edition = models.ForeignKey('OnlineEdition', related_name='content_file')
    name = models.CharField(max_length=100)
    filename = models.FileField(upload_to="data")
    mimetype = models.CharField(max_length=100,editable=False)
    id = NoidField(settings.NOID_DIR, max_length=6, primary_key=True)

    def get_ext(self):
        if mime2ext_map.has_key(self.mimetype):
            return mime2ext_map[self.mimetype]
        else: return None

    def get_mimetype_from_ext(self, ext):
        if ext2mime_map.has_key(ext):
            return ext2mime_map[ext]
        else: return None

    def __unicode__(self): return self.name

    def get_absolute_url(self): return "/%s"%(self.pk)

    def save(self):
        (basename, ext) = os.path.splitext(str(self.filename))
        self.mimetype = self.get_mimetype_from_ext(ext)
        super(FileContent, self).save()

class Page(models.Model):
    title = models.CharField(max_length=100)
    name = models.CharField(max_length=100,unique=True,primary_key=True)
    data = models.TextField(blank=True)
    date = models.DateTimeField(null=True)
    news = models.BooleanField()
    def __unicode__(self): return "%s (/doc/%s)"%(self.title,self.name)

class Section(models.Model):
    name = models.CharField(max_length=100)
    id = models.CharField(max_length=6,primary_key=True)
    def __unicode__(self): return self.name
