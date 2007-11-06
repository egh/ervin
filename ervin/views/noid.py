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
import ervin.views.generic
import ervin.views.person
import ervin.views.work
import ervin.views.expression

def by_noid(request,*args,**kwargs):
    n = kwargs['noid']
    def try_view(klass, view_func):
        try:
            o = klass.objects.get(noid=n)
            if o != None:
                return view_func(o,request,*args,**kwargs)
            else:
                return None
        except ObjectDoesNotExist:
            return None
    for pair in ((Person, ervin.views.person.detail),
                 (Work, ervin.views.work.detail),
                 (Expression, ervin.views.expression.detail)):
        retval = try_view(pair[0], pair[1])
        if retval != None:
            return retval
    return HttpResponseNotFound('Not found')
