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
from ervin.views import make_columns
from ervin.grouping_paginator import GroupingPaginator

def by_noid(request, *args, **kwargs):
    work = Work.objects.get(id=kwargs['noid'])
    return detail(work, request, *args, **kwargs)

def detail(work, request, *args, **kwargs):
    if work.expression_set.all().count() == 1:
        return HttpResponseRedirect(work.expression_set.all()[0].get_absolute_url())
    else:
	t = loader.get_template('work.html')
	c = Context({
                "work": work
                })
    	return HttpResponse(t.render(c))

def online_works(request, *args, **kwargs):
    page_n = int(request.GET.get('page','1'))
    page = GroupingPaginator(Work.with_content.distinct().all(), 50, 'online_works_groups').page(page_n)
    t = loader.get_template('work_list_grouped.html')
    c = Context({ 
            "page" : page
            })
    return HttpResponse(t.render(c))
