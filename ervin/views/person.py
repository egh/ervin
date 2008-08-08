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
from ervin.views.generic import *
from django.http import HttpResponse

def by_slug(request, *args, **kwargs):
   person = Person.objects.get(slug=kwargs['slug'])
   return detail(person, request, *args, **kwargs)

def by_noid(request, *args, **kwargs):
   person = Person.objects.get(noid=kwargs['noid'])
   return detail(person, request, *args, **kwargs)

def detail(person, request, *args,**kwargs):
   s = person.get_subject ()
   docs_about = list (Work.objects.filter (subjects=s))
   docs_by = list (Work.objects.filter (authors=person))

   subjects_set = dict()
   for w in docs_by:
      for s in w.subjects.all():
         subjects_set[s] = s
   for w in docs_about:
      for s in w.subjects.all():
         subjects_set[s] = s
   subjects = subjects_set.values()
   subjects.sort()
   
   t = loader.get_template('person.html')
   c = Context({
         'subjects' : subjects,
         'person': person,
         'docs_by': docs_by,
         'docs_about': docs_about
         })
   return HttpResponse(t.render(c))
