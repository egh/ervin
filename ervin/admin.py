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

from django.contrib import admin
from django import forms
from django.db.models import get_model
from ervin.models import *

class ExpressionInlineAdmin(admin.StackedInline):
    model=Expression
    filter_horizontal = ('translators')

class RemoteContentInlineAdmin(admin.StackedInline):
    model=RemoteContent
    extra = 1

class DbContentInlineAdmin(admin.StackedInline):
    model=DbContent
    extra = 1

class FileContentInlineAdmin(admin.StackedInline):
    model=FileContent
    extra = 1

class AuthorshipInlineAdmin(admin.TabularInline):
    model = Authorship
    extra = 1

class ExpressionTranslatorInlineAdmin(admin.TabularInline):
    model = ExpressionTranslator
    extra = 1

class WorkAdmin(admin.ModelAdmin):
    search_fields = ['work_title']
    fieldsets = [
        [None, {
            'fields': ['work_title','date','form','part_of'],
        }],
        ['Subjects', {
            'classes': ['collapse'],
            'fields': ['subjects'],
        }],
        ['More', {
            'classes': ['collapse'],
            'fields': ['description','note','source'],
        }],
    ]
    filter_horizontal=['subjects']
    inlines = [AuthorshipInlineAdmin]
    raw_id_fields = ['part_of']

class OnlineEditionAdmin(admin.ModelAdmin):
    model = OnlineEdition
    search_fields = ['sort']
    list_display = ['id', 'title']
    raw_id_fields = ['expression']
    inlines=[DbContentInlineAdmin, FileContentInlineAdmin]

class PhysicalEditionAdmin(admin.ModelAdmin):
    model = PhysicalEdition
    search_fields = ['sort']
    raw_id_fields = ['expression']

class ExpressionAdmin(admin.ModelAdmin):
    search_fields = ['sort']
    inlines = [ExpressionTranslatorInlineAdmin]

admin.site.register(Concept)
admin.site.register(Expression, ExpressionAdmin)
admin.site.register(OnlineEdition,OnlineEditionAdmin)
admin.site.register(Organization)
admin.site.register(Page)
admin.site.register(Person)
admin.site.register(PhysicalEdition,PhysicalEditionAdmin)
admin.site.register(Place)
admin.site.register(Work, WorkAdmin)
