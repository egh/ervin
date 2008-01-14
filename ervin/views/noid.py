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
import ervin.views.generic, ervin.views.person, ervin.views.work, ervin.views.expression

views = { Person : ervin.views.person.detail,
          Work : ervin.views.work.detail,
          Expression : ervin.views.expression.detail }

def by_noid(request,*args,**kwargs):
    o = find_one(tuple(views.keys()), noid=kwargs['noid'])
    o_class = o.__class__
    if views.has_key(o.__class__):
        if type(views[o_class]) == str:
            t = loader.get_template(views[o_class])
            c = Context({ o_class.lower(): o })
            return HttpResponse(t.render(c))
        else:
            return views[o.__class__] (o, request, *args, **kwargs)
    else:
        return HttpResponseNotFound('Not found')
