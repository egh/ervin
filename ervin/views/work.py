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
from django.db.models import Q

def by_noid(request, *args, **kwargs):
    work = Work.objects.get(id=kwargs['noid'])
    return detail(work, request, *args, **kwargs)

def detail(work, request, *args, **kwargs):
    if len(work.expression_set.all()) == 1:
        return HttpResponseRedirect(work.expression_set.all()[0].get_absolute_url())
    else:
	t = loader.get_template('work.html')
	c = Context({
                'work': work
                })
    	return HttpResponse(t.render(c))

def online_works(request, *args, **kwargs):
    works = Work.objects.exclude(Q(expression__onlineedition=None) & Q(parts=None)).distinct().all()
    works = [ work for work in works if work.is_online ]
    t = loader.get_template('onlineedition_list.html')
    c = Context({ "edition_list" : works })
    return HttpResponse(t.render(c))
