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
import re, ervin.views.person, ervin.views.work, ervin.views.expression, ervin.views.onlineedition

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
    response['Content-Disposition'] = "inline; filename=%s%s"%(f.noid,f.get_ext())
    response['Content-Length'] = os.path.getsize(f.filename)
    response.write(open(f.filename).read())
    return response

views = { Work : ervin.views.work.detail,
          Expression : ervin.views.expression.detail,
          Person : ervin.views.person.detail,
          OnlineEdition : ervin.views.onlineedition.detail,
          # group 3
          FrbrObject : 'object.html',
          Concept : 'concept.html',
          Event : 'event.html',
          Place : 'place.html',
          #content
          FileContent : showfile }
          
list_views = { Person : 'person_list.html',
               Work : 'work_list.html',
               
               Place : 'place_list.html' }
               
def by_noid(request,*args,**kwargs):
    o = find_one(tuple(views.keys()), noid=kwargs['noid'])
    o_class = o.__class__
    if views.has_key(o.__class__):
        if type(views[o_class]) == str:
            t = loader.get_template(views[o_class])
            c = Context({ o_class.__name__.lower(): o })
            return HttpResponse(t.render(c))
        else:
            return views[o.__class__] (o, request, *args, **kwargs)
    else:
        return HttpResponseNotFound('Not found')

def list_view(*args, **kwargs):
    klass = kwargs['class']
    if list_views.has_key(klass):
        l = find_all(klass)
        t = loader.get_template(list_views[klass])
        c = Context({ "%s_list"%(klass.__name__.lower()): l })
        return HttpResponse(t.render(c))
        
