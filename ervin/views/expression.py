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
import ervin.views.generic
from django.http import HttpResponse, HttpResponseRedirect

def by_noid(request, *args, **kwargs):
    expression = Expression.objects.get(noid=kwargs['noid'])
    return detail(expression, request, *args, **kwargs)

def detail(expression, request, *args, **kwargs):
    manifestations = expression.get_manifestations()
    if len(manifestations) == 1:
        return HttpResponseRedirect(manifestations[0].get_absolute_url())
    else:
	t = loader.get_template('expression.html')
	c = Context({
          'expression': expression
        })
    	return HttpResponse(t.render(c))
