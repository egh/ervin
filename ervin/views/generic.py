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
import re, ervin.views.person, ervin.views.work, ervin.views.expression, ervin.views.onlineedition, ervin.views.physicaledition

def make_columns(data, col_count):
    l = len(data)
    r = l % col_count
    col_size = []
    cols = []
    for i in range(col_count):
        if (i > (r - 1)): col_size.append(l/col_count)
        else: col_size.append(l/col_count + 1)
    start = 0
    for i in range((col_count)):
        if i == col_count - 1: finish = l
        else: finish = (start + col_size[i])
        cols.append(data[start:finish])
        start = finish
    return cols

def get_sections():
    sections = list(Section.objects.all())
    sections.sort(lambda a,b: cmp(a.slug,b.slug))
    return sections

stop_words_re = re.compile("(^the |^an |^a )")

def get_sort_title(title):
    return stop_words_re.sub("",title.lower())

def title_sort(a,b):
    return cmp(get_sort_title(a.title),get_sort_title(b.title))

def author_sort(a,b):
    a_authors = a.authors.all()
    b_authors = b.authors.all()
    if len(a_authors) > 0:
        a2 = a_authors[0].surname.lower()
    else:
        a2 = get_sort_title(a.title)
    if len(b_authors) > 0:
        b2 = b_authors[0].surname.lower()
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

def find_all(klass):
    return klass.objects.all()

def showfile(f,*args,**kwargs):
    response = HttpResponse(mimetype=f.mimetype)
    response['Content-Disposition'] = "inline; filename=%s%s"%(f.pk,f.get_ext())
    response['Content-Length'] = os.path.getsize(str(f.filename.path))
    response.write(open(f.filename.path).read())
    return response

views = {
    #group 1
    Work : ervin.views.work.detail,
    Expression : ervin.views.expression.detail,
    OnlineEdition : ervin.views.onlineedition.detail,
    PhysicalEdition : ervin.views.physicaledition.detail,

    # group 2
    Person : ervin.views.person.detail,
    Organization : 'organization.html',
    
    # group 3
    FrbrObject : 'object.html',
    Concept : 'concept.html',
    Event : 'event.html',
    Place : 'place.html',
    
    #content
    FileContent : showfile }
          
list_views = { Work : 'work_list.html',
               OnlineEdition : 'onlineedition_list.html',
               PhysicalEdition : 'physicaledition_list.html',
               
               Person : 'person_list.html',
               Organization : 'organization_list.html',
               
               Concept : 'concept_list.html',
               Event : 'event_list.html',
               FrbrObject : 'object_list.html',
               Place : 'place_list.html' }

variable_names = { OnlineEdition : 'edition',
                   PhysicalEdition : 'edition' }

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

def list_view(*args, **kwargs):
    if kwargs.has_key('columns'): column_count = kwargs['columns']
    else: column_count = 4
    klass = kwargs['class']
    if list_views.has_key(klass):
        item_list = list(find_all(klass))
        t = loader.get_template(list_views[klass])
        cols = make_columns(item_list, column_count)
        if (variable_names.has_key(klass)):
            list_variable_name = "%s_list"%(variable_names[klass])
        else: 
            list_variable_name = "%s_list"%(klass.__name__.lower())
        c = Context({ "%s_cols"%(klass.__name__.lower()): cols,
                      list_variable_name : item_list } )
        return HttpResponse(t.render(c))
