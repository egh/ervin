# -*- coding: utf-8 -*-
#Copyright (C) 2007-2020, Erik Hetzner

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

from django.contrib import admin
from django import forms
from django.db.models import get_model
from ervin.models import *
from ervin.forms import DbContentAdminModelForm, PageAdminModelForm
from django.contrib import admin
from django.contrib.contenttypes import generic

class RemoteContentInlineAdmin(admin.StackedInline):
    model=RemoteContent
    extra = 0

class DbContentInlineAdmin(admin.StackedInline):
    model=DbContent
    extra = 0
    form = DbContentAdminModelForm

class FileContentInlineAdmin(admin.StackedInline):
    model=FileContent
    extra = 0

class RemoteContentInlineAdmin(admin.StackedInline):
    model=RemoteContent
    extra = 0

class CreatorshipInlineAdmin(admin.TabularInline):
    model = Creatorship
    extra = 0

class AliasInlineAdmin(admin.TabularInline):
    model = Person
    extra = 0
    fields = ('forename', 'surname')
    verbose_name = "Alias"
    verbose_name_plural = "Aliases"

class ExpressionInlineAdmin(admin.StackedInline):
    model = Expression
    filter_horizontal=['translators']
    extra = 0

class WorkModelForm(forms.ModelForm):
    work_title = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 100, 'rows': 1}))
    class Meta:
        model = Work

class WorkSameAsUriInline(admin.TabularInline):
    model = WorkSameAsUri
    extra = 0

class WorkAdmin(admin.ModelAdmin):
    form = WorkModelForm
    search_fields = ['sort']
    fieldsets = [
        [None, {
            'fields': ['work_title','date','part_of'],
        }],
        ['Subjects', {
            'classes': ['collapse'],
            'fields': ['subjects'],
        }],
    ]
    filter_horizontal=['subjects']
    inlines = [CreatorshipInlineAdmin, ExpressionInlineAdmin, WorkSameAsUriInline]
    raw_id_fields = ['part_of']

class OnlineEditionAdmin(admin.ModelAdmin):
    model = OnlineEdition
    search_fields = ['sort']
    raw_id_fields = ['expression']
    inlines=[DbContentInlineAdmin, FileContentInlineAdmin,RemoteContentInlineAdmin]
    list_display = ('__unicode__','date')

class PhysicalEditionSameAsUriInline(admin.TabularInline):
    model = PhysicalEditionSameAsUri

class PhysicalEditionAdmin(admin.ModelAdmin):
    model = PhysicalEdition
    search_fields = ['sort']
    raw_id_fields = ['expression']    
    inlines=[PhysicalEditionSameAsUriInline]

class PageAdmin(admin.ModelAdmin):
    model = Page
    form = PageAdminModelForm
    prepopulated_fields = {"id": ("title",)}

class ExpressionAdmin(admin.ModelAdmin):
    model = Expression
    search_fields = ['sort']

class PersonSameAsUriInline(admin.TabularInline):
    model = PersonSameAsUri
    extra = 0

class PersonAdmin(admin.ModelAdmin):
    model = Person
    search_fields = ['surname', 'forename']
    inlines=[AliasInlineAdmin, PersonSameAsUriInline]
    fields = ('forename', 'surname', 'dates')

class PlaceSameAsUriInline(admin.TabularInline):
    model = PlaceSameAsUri
    extra = 0

class PlaceAdmin(admin.ModelAdmin):
    inlines=[PlaceSameAsUriInline]

class OrganizationSameAsUriInline(admin.TabularInline):
    model = OrganizationSameAsUri

class OrganizationAdmin(admin.ModelAdmin):
    inlines=[OrganizationSameAsUriInline]

class ConceptSameAsUriInline(admin.TabularInline):
    model = ConceptSameAsUri
    extra = 0

class ConceptAdmin(admin.ModelAdmin):
    inlines=[ConceptSameAsUriInline]

class FrbrObjectSameAsUriInline(admin.TabularInline):
    model = FrbrObjectSameAsUri
    extra = 0

class FrbrObjectAdmin(admin.ModelAdmin):
    inlines=[FrbrObjectSameAsUriInline]

class EventSameAsUriInline(admin.TabularInline):
    model = EventSameAsUri
    extra = 0

class EventAdmin(admin.ModelAdmin):
    inlines=[EventSameAsUriInline]

admin.site.register(Concept, ConceptAdmin)
admin.site.register(Expression, ExpressionAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(FileContent)
admin.site.register(FrbrObject, FrbrObjectAdmin)
admin.site.register(OnlineEdition, OnlineEditionAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(PhysicalEdition, PhysicalEditionAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Work, WorkAdmin)
