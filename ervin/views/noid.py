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

from django.template import Context, loader
from ervin.models import *
from django.http import HttpResponse,HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from ervin.views.generic import find_one
import ervin.views.generic
import ervin.views.person
import ervin.views.work
import ervin.views.expression

views = { Person : ervin.views.person.detail,	
          Work : ervin.views.work.detail,
          Expression : ervin.views.expression.detail }

def by_noid(request,*args,**kwargs):
    n = kwargs['noid']
    o = find_one(Person, Work, Expression, noid=n)
    if views.has_key(o.__class__):
        return views[o.__class__] (o, request, *args, **kwargs)
    else:
        return HttpResponseNotFound('Not found')
