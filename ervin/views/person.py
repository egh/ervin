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
from django.db.models import Q
from ervin.views.generic import *
from django.http import HttpResponse

def by_slug(request, *args, **kwargs):
   person = Person.objects.get(slug=kwargs['slug'])
   return detail(person, request, *args, **kwargs)

def by_noid(request, *args, **kwargs):
   person = Person.objects.get(id=kwargs['noid'])
   return detail(person, request, *args, **kwargs)

def detail(person, request, *args,**kwargs):
   work_list = Work.objects.filter(Q(authors=person) | Q(subjects=person.subject))
   subject_list = Subject.objects.filter(work__in=work_list).distinct()
   image_list = work_list.filter(form='image').distinct()
   text_list = person.authored.exclude(form='image').distinct()

   t = loader.get_template('person.html')
   c = Context({
         'subject_list' : subject_list,
         'person'       : person,
         'image_list'   : image_list,
         'text_list'    : text_list,
         })
   return HttpResponse(t.render(c))
