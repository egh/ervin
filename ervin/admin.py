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
from ervin.models import *

class WorkAdmin(admin.ModelAdmin):
    filter_horizontal=('subjects','authors')

admin.site.register(Work, WorkAdmin)
admin.site.register(Person)
admin.site.register(Concept)
admin.site.register(OnlineEdition)
admin.site.register(PhysicalEdition)
