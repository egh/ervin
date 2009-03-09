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
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.db.models import Q
from django.core.cache import cache

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

def build_groups(q, max_size):
    startswith = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    groups = [('a'),('b'),('c'),('d'),('e'),('f'),('g'),('h'),('i'),('j'),('k'),('l'),('m'),('n'),('o'),('p'),('q'),('r'),('s'),('t'),('u'),('v'),('w'),('x'),('y'),('z')]
    count = {}
    for l in startswith:
        count[l] = q.filter(sort__startswith=l).count()
    finished = False
    while (not(finished)):
        for i in range(0, len(groups)-1):
            i_size = sum([ count[l] for l in groups[i] ])
            next_size = sum([ count[l] for l in groups[i+1] ])
            if (i_size + next_size) < max_size:
                groups = groups[:i] + [(groups[i] + groups[i+1])] + groups[i+2:]
                break
        else:
            finished = True
    return groups

def group_to_re(group):
    return "^[%s]"%("".join(group))
        
def group_to_string(group):
    if len(group) == 1:
        return group[0]
    else:
        return "%s-%s"%(group[0].upper(),group[-1].upper())

def online_works(request, *args, **kwargs):
    works = Work.objects.exclude(Q(expression__onlineedition=None) & Q(parts=None)).distinct().all()
    groups = cache.get('document_groups')
    if groups == None:
        groups = build_groups(works,50)
        cache.set('document_groups', groups, 600)
    if request.REQUEST.has_key('page'): page = int(request.REQUEST['page'])
    else: page = 1
    works = works.filter(sort__iregex=group_to_re(groups[page-1]))
    t = loader.get_template('work_list.html')
    c = Context({ "work_list" : works,
                  "groups"    : [ group_to_string(g) for g in groups ],
                  'page'      : page })
    return HttpResponse(t.render(c))
