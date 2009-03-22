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
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.db.models import Q
from django.core.cache import cache
from ervin.views import make_columns, build_groups, group_to_re, group_to_string

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
    groups = cache.get('document_groups')
    if groups == None:
        groups = build_groups(works,50)
        cache.set('document_groups', groups, 600)
    page = int(request.GET.get('page','1'))
    works = works.filter(sort__iregex=group_to_re(groups[page-1]))
    t = loader.get_template('work_list.html')
    c = Context({ "work_list" : works,
                  "groups"    : [ group_to_string(g) for g in groups ],
                  'page'      : page })
    return HttpResponse(t.render(c))
