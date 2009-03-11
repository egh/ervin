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
from ervin.views import make_columns
import re, ervin.views.person, ervin.views.work, ervin.views.expression, ervin.views.onlineedition, ervin.views.physicaledition

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
    if (klass == FrbrObject) or (klass == Concept) or (klass == Event) or (klass == Place):
        # for "group 3" only return where we have a positive subject count
        return [ x for x in klass.objects.all() if x.subject.work_set.count() > 0]
    else:
        return klass.objects.all()
    
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

def list_view(*args, **kwargs):
    if kwargs.has_key('columns'): column_count = kwargs['columns']
    else: column_count = 4
    klass = kwargs['class']
    if list_views.has_key(klass):
        item_list = list(find_all(klass))
        t = loader.get_template(list_views[klass])
        cols = make_columns(item_list, column_count)
        if (variable_names.has_key(klass)):
            variable_name = variable_names[klass]
        else: 
            variable_name = klass.__name__.lower()
        c = Context({ "%s_cols"%(variable_name) : cols,
                      "%s_list"%(variable_name) : item_list } )
        return HttpResponse(t.render(c))
