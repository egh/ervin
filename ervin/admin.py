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

class WorkAdmin(admin.ModelAdmin):
    search_fields = ['work_title']
    filter_horizontal=('subjects',)
    inlines = [AuthorshipInlineAdmin]

class OnlineEditionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    model=OnlineEdition
    search_fields = ['sort']
    inlines=[DbContentInlineAdmin, FileContentInlineAdmin]

class PhysicalEditionAdmin(admin.ModelAdmin):
    search_fields = ['sort']
    model=PhysicalEdition

admin.site.register(Work, WorkAdmin)
admin.site.register(Person)
admin.site.register(Concept)
admin.site.register(OnlineEdition,OnlineEditionAdmin)
admin.site.register(PhysicalEdition,PhysicalEditionAdmin)
admin.site.register(Page)
admin.site.register(Place)
admin.site.register(Organization)
