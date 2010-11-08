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
from django.conf import settings
from django.http import HttpResponse,HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from ervin.views import make_columns
import re, ervin.views.person, ervin.views.work, ervin.views.expression, ervin.views.onlineedition, ervin.views.physicaledition
from ervin.grouping_paginator import GroupingPaginator

stop_words_re = re.compile("(^the |^an |^a )")
show_empty_subjects = getattr(settings, 'ERVIN_SHOW_EMPTY_SUBJECTS', True)

def get_sort_title(title):
    return stop_words_re.sub("",title.lower())

def title_sort(a,b):
    return cmp(get_sort_title(a.title),get_sort_title(b.title))

def creator_sort(a,b):
    a_creators = a.creators.all()
    b_creators = b.creators.all()
    if len(a_creators) > 0:
        a2 = a_creators[0].surname.lower()
    else:
        a2 = get_sort_title(a.title)
    if len(b_creators) > 0:
        b2 = b_creators[0].surname.lower()
    else:
        b2 = get_sort_title(b.title)
    return cmp(a2,b2)

def find_one(*args, **kwargs):
    if type(args[0]) == tuple:
       args = args[0]
    if type(args[0]) == list:
        args = args[0]
    for klass in args:
        try: 
            return klass.objects.get(**kwargs)
        except Exception, ex:
            print ex 
            pass
    return None

def find_all(klass, q=None):
    if q == None:
        q = klass.objects.all()
    if not(show_empty_subjects) and ((klass == FrbrObject) or (klass == Concept) or (klass == Event) or (klass == Place)):
        # for "group 3" only return where we have a positive subject count
        ids = [ x.pk for x in q if x.subject.work_set.count() == 0]
        return q.exclude(id__in=ids)
    else:
        return q
    
def showfile(f, request, *args, **kwargs):
    from sorl.thumbnail.main import DjangoThumbnail
    response = HttpResponse(mimetype=str(f.mimetype))
    disposition = "inline; filename=%s%s"%(f.pk,f.get_ext())
    size = f.size
    fullpath = f.filename.path
    if (request.REQUEST.has_key('x')) and f.mimetype.startswith('image/'):
        x = request.REQUEST['x']
        if request.REQUEST.has_key('y'):
            y = request.REQUEST['y']
        else:
            y = x
        t = DjangoThumbnail(f.filename.path, (x,y))
        disposition = "inline"
        size = t.filesize
        fullpath = t.dest
    response['Content-Disposition'] = disposition
    response['Content-Length'] = size
    response.write(open(fullpath,'rb').read())
    return response

views = {
    #group 1
    Work : ervin.views.work.detail,
    Expression : ervin.views.expression.detail,
    OnlineEdition : ervin.views.onlineedition.detail,
    PhysicalEdition : ervin.views.physicaledition.detail,

    # group 2
    Person : ervin.views.person.detail,
    Organization : 'ervin/organization.html',
    
    # group 3
    FrbrObject : 'ervin/object.html',
    Concept : 'ervin/concept.html',
    Event : 'ervin/event.html',
    Place : 'ervin/place.html',
    
    #content
    FileContent : showfile }
          
list_views = { Work : 'ervin/work_list.html',
               OnlineEdition : 'ervin/onlineedition_list.html',
               PhysicalEdition : 'ervin/physicaledition_list.html',
               
               Person : 'ervin/person_list.html',
               Organization : 'ervin/organization_list.html',
               
               Concept : 'ervin/concept_list.html',
               Event : 'ervin/event_list.html',
               FrbrObject : 'ervin/object_list.html',
               Place : 'ervin/place_list.html' }

variable_names = { OnlineEdition : 'edition',
                   PhysicalEdition : 'edition',
            
                   Person : 'subject',
                   Organization : 'subject',
                   Concept : 'subject',
                   Event : 'subject',
                   FrbrObject : 'subject',
                   Place : 'subject' }

def by_noid(request,*args,**kwargs):
    o = find_one(tuple(views.keys()), id=kwargs['noid'])
    klass = o.__class__
    if views.has_key(klass):
        if type(views[klass]) == str:
            subject = Subject.objects.get (object_id=o.pk)
            works = Work.objects.filter(subjects=subject).order_by('sort')
            t = loader.get_template(views[klass])
            if (variable_names.has_key(klass)):
                variable_name = variable_names[klass]
            else:
                variable_name = klass.__name__.lower()
            c = Context({ variable_name : o,
                          'work_list' : works })
            return HttpResponse(t.render(c))
        else:
            return views[klass] (o, request, *args, **kwargs)
    else:
        return HttpResponseNotFound('Not found')

def list_view(request, *args, **kwargs):
    if kwargs.has_key('columns'): column_count = kwargs['columns']
    else: column_count = 4
    klass = kwargs['class']
    if list_views.has_key(klass):
        page_n = int(request.GET.get('page','1'))
        page = GroupingPaginator(find_all(klass), 60, "%s_groups"%klass.__name__.lower()).page(page_n)
        t = loader.get_template(list_views[klass])
        if (variable_names.has_key(klass)):
            variable_name = variable_names[klass]
        else: 
            variable_name = klass.__name__.lower()
        c = Context({ "page" : page,
                      "subject_type" : klass.__name__.lower() })
        return HttpResponse(t.render(c))

