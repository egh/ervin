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
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.conf import settings
from noid import LocalMinter
from noid import NoidField
import re

def delete_hook(item):
    which_type = ContentType.objects.get(model=lower(type(item).__name__),
                                         app_label='ervin')
    try:
        s = Subject.objects.get(content_type=which_type,
                                object_id=item.id)
        s.delete()
    except:
        pass

class Subject(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    slug = models.CharField(max_length=100,editable=False)
    noid = models.CharField(max_length=6,editable=False)
    def get_absolute_url(self):
	return '/' + self.content_type.name + '/' + self.slug
    def save(self):
        self.slug = self.content_object.slug
        super(Subject, self).save() 
    class Admin:
        pass
    def __str__(self):
        return str(self.content_object)

class Person(models.Model):
    surname = models.CharField(max_length=200)
    slug = models.CharField(max_length=100,editable=False)
    forename = models.CharField(max_length=200)
    dates = models.CharField(max_length=20,blank=True)
    noid = NoidField(settings.NOID_DIR, max_length=6,primary_key=True)
    def get_absolute_url(self):
	return '/' + self.noid
    def save(self):
        self.slug = slugify(self.surname + '-' + self.forename)
        super(Person, self).save()
        person_type = ContentType.objects.get(model='person', 
                                              app_label='ervin')
        try:
            s = Subject.objects.get(content_type=person_type,object_id=self.id)
        except Subject.DoesNotExist:
            s = Subject(content_type=person_type,object_id=self.id)
        s.save()
    def __hash__(self):
        return hash(self.id)
    def __str__(self):
        if self.dates:
            return self.surname + ", " + self.forename + " (" + self.dates + ")"
        else:
            return self.surname + ", " + self.forename
    class Meta:
        ordering=['surname','forename']
    class Admin:
        pass
    
class Section(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100,editable=False)
    def __str__(self):
        return self.name
    def save(self):
        self.slug = slugify(self.name)
        super(Section, self).save() 
    class Admin:
        pass

class Concept(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200,editable=False)
    noid = NoidField(settings.NOID_DIR, max_length=6)
    def get_absolute_url(self):
	return '/concept/' + self.slug
    def save(self):
        self.slug = slugify(self.name)
        super(Concept, self).save()
        concept_type = ContentType.objects.get(model='concept',
                                               app_label='ervin')
        try:
            s = Subject.objects.get(content_type=concept_type,object_id=self.id)
        except Subject.DoesNotExist:
            s = Subject(content_type=concept_type,object_id=self.id)
        s.save()
    def delete(self):
        delete_hook(self)
        super(Concept, self).delete()
    def __str__(self):
        return self.name
    name_en = "Concept"
    class Admin:
        pass   
    
class Work(models.Model):
    title = models.CharField(max_length=200,blank=True)
    def get_title(self):
        return self.title
    slug = models.CharField(max_length=200,blank=True,editable=False)
    authors = models.ManyToManyField(Person,verbose_name="Authors",
                                     related_name="authored",
                                     blank=True,
                                     filter_interface=models.HORIZONTAL)
    translators = models.ManyToManyField(Person,verbose_name="Translators",
                                         related_name="translated",
                                         filter_interface=models.HORIZONTAL,blank=True)
    subjects = models.ManyToManyField(Subject,filter_interface=models.HORIZONTAL,blank=True)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)
    partof = models.ForeignKey("self",blank=True,null=True,related_name="parts")
    sections = models.ManyToManyField(Section,filter_interface=models.HORIZONTAL,blank=True)
    noid = NoidField(settings.NOID_DIR, max_length=6,primary_key=True)
    class Meta:
        ordering=['title']
    class Admin: 
        fields = (
            ("Main", {'fields': ('title', 'partof','description',
                                 'note')}),
            ("People", {'classes': 'collapse',
                        'fields': ('authors', 'translators')}),
            ("Classification",  {'classes':'collapse',
                        'fields': ('subjects', 'sections')}),
            #("Editions", {'classes':'collapse',
            #'fields': ("catalogeditions", "onlineedition_set")}),
            )
        js = ['js/tiny_mce/tiny_mce.js', 'js/textareas.js']
    def get_absolute_url(self):
        return '/' + self.noid
    def save(self):
        self.slug = slugify(self.title)
        super(Work, self).save() 
        try:
            expression = Expression.objects.get(work=self)
        except Expression.DoesNotExist:
            e = Expression(work=self)
            e.save()

    def __str__(self):
        if self.partof == None:
            return self.title
        else:
            return self.title + " (in " + self.partof.title + ")"

class Expression(models.Model):
    work = models.ForeignKey('Work',
                             to_field='noid',
                             db_column='work_noid')
    title = models.TextField(max_length=200, blank=True)
    noid = NoidField(settings.NOID_DIR,
                     max_length=6,
                     primary_key=True,
                     core=True)
    def get_manifestations(self):
        return list(self.onlineedition_set.all()) + list(self.physicaledition_set.all())    
    def get_authors(self):
        return self.work.authors
    authors = property(get_authors)
    def get_title(self):
        if self.title != None and self.title != '':
            return self.title
        else:
            return self.work.get_title()
    def get_absolute_url(self):
        return '/' + self.noid
    def __str__(self):
    	return str(self.work)

class OnlineEdition(models.Model):
    pub_date = models.DateTimeField(blank=True)
    pdf = models.FileField(upload_to="pamphlet_pdfs",blank=True)
    html = models.TextField(blank=True,core=True)
    expression = models.ForeignKey(Expression,
                                   db_column='expression_noid',
                                   to_field='noid')
    title = models.TextField(max_length=200, blank=True)
    noid = NoidField(settings.NOID_DIR,max_length=6)
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
    def __str__(self):
        return str(self.work)
    def get_absolute_url(self):
        return '/' + self.noid
    class Admin:
        js = ['js/tiny_mce/tiny_mce.js', 'js/textareas.js']
    
class PhysicalEdition(models.Model):
    pub_date = models.DateField(blank=True)
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
    #def get_work(self):
    #    return self.expression.work
    #work = property(get_work)
    work = models.ForeignKey('Work',
                             edit_inline=models.STACKED,
                             related_name="physicalmanifestations")
    expression = models.ForeignKey(Expression,
                                   to_field='noid',
                                   db_column='expression_noid')
    noid = NoidField(settings.NOID_DIR, max_length=6)
    def get_title(self):
        return self.work.title
    def get_authors(self):
        return self.expression.authors
    authors = property(get_authors)
    def get_subjects(self):
        return self.work.subjects
    subjects = property(get_subjects)
    def get_parts(self):
        return self.work.parts
    parts = property(get_parts)
    def __str__(self):
        return self.work.title + " (" + str(self.pub_date) + ")"
    class Admin:
        js = ['js/tiny_mce/tiny_mce.js', 'js/textareas.js']   
    def get_absolute_url(self):
        return '/' + self.noid
    def get_items(self):
        return None

class RemoteItem(models.Model):
    manifestation = models.ForeignKey(OnlineEdition, 
                                      to_field='noid',
                                      db_column='manifestation_noid',
                                      edit_inline=models.STACKED)
    url = models.CharField(max_length=1024,core=True)
    noid = NoidField(settings.NOID_DIR, max_length=6,primary_key=True)
    def get_absolute_url(self):
        return self.url
    
class Place(models.Model):
    name_en = "Place"
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200,editable=False)
    noid = NoidField(settings.NOID_DIR, max_length=6)
    def get_absolute_url(self):
	return '/place/' + self.slug
    def save(self):
        self.slug = slugify(self.name)
        super(Place, self).save()
        place_type = ContentType.objects.get(model='place',
                                             app_label='ervin')
        try:
            s = Subject.objects.get(content_type=place_type,object_id=self.id)
        except Subject.DoesNotExist:
            s = Subject(content_type=place_type,object_id=self.id)
        s.save()
    def delete(self):
        delete_hook(self)
        super(Place, self).delete()
    def __str__(self):
        return self.name
    class Admin:
        pass

class Organization(models.Model):
    name_en = "Organization"
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200,editable=False)
    noid = NoidField(settings.NOID_DIR, max_length=6)
    def get_absolute_url(self):
	return '/organization/' + self.slug
    def save(self):
        self.slug = slugify(self.name)
        super(Organization, self).save()
        which_type = ContentType.objects.get(model='organization',
                                             app_label='ervin')
        try:
            s = Subject.objects.get(content_type=which_type,object_id=self.id)
        except Subject.DoesNotExist:
            s = Subject(content_type=which_type,object_id=self.id)
        s.save()
    def delete(self):
        delete_hook(self)
        super(Organization, self).delete()
    def __str__(self):
        return self.name
    class Admin:
        pass   

class Event(models.Model):
    name_en = "Event"
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200,editable=False)
    noid = NoidField(settings.NOID_DIR, max_length=6)
    def get_absolute_url(self):
	return '/event/' + self.slug
    def save(self):
        self.slug = slugify(self.name)
        super(Event, self).save()
        which_type = ContentType.objects.get(model='event',
                                             app_label='ervin')
        try:
            s = Subject.objects.get(content_type=which_type,object_id=self.id)
        except Subject.DoesNotExist:
            s = Subject(content_type=which_type,object_id=self.id)
        s.save()
    def delete(self):
        delete_hook(self)
        super(Event, self).delete()
    def __str__(self):
        return self.name
    class Admin:
        pass
    
