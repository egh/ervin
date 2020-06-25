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

from django.template import Context, loader
from ervin.models import *
import ervin.views.generic
from django.http import HttpResponse, HttpResponseRedirect

def by_noid(request, *args, **kwargs):
    expression = Expression.objects.get(id=kwargs['noid'])
    return detail(expression, request, *args, **kwargs)

def detail(expression, request, *args, **kwargs):
    # for expressions which have only one edition & which are not
    # multi-part works, redirect to the edition.
    editions = expression.editions
    if len(editions) == 1 and expression.work.parts.count() == 0:
        return HttpResponseRedirect(editions[0].get_absolute_url())
    else:
	t = loader.get_template('ervin/expression.html')
	c = Context({
          'image_parts' : expression.work.parts.filter(expression__form='image').distinct(),
          'non_image_parts' : expression.work.parts.exclude(expression__form='image').distinct(),
          'entity': expression
        })
    	return HttpResponse(t.render(c))
