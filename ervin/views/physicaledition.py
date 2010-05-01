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

from django.template import Context, loader
from ervin.models import *
from django.http import HttpResponse

def detail(ed, request, *args,**kwargs):
    if kwargs.has_key('ext') and type.has_key(kwargs['ext']):
        type = type_map[kwargs['ext']]
    t = loader.get_template('ervin/physicaledition.html')
    c = Context({ 'entity' : ed})
    return HttpResponse(t.render(c))
    
def available(*args,**kwargs):
    physicaledition_list = PhysicalEdition.objects.exclude(available_uk=False).exclude(available_us=False).all()
    t = loader.get_template('ervin/physicaledition_list.html')
    c = Context({ 'physicaledition_list' : physicaledition_list})
    return HttpResponse(t.render(c))
