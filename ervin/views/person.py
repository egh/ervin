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
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.http import HttpResponse

def by_noid(request, *args, **kwargs):
   person = Person.objects.get(id=kwargs['noid'])
   return detail(person, request, *args, **kwargs)

def detail(person, request, *args,**kwargs):
   if person.alias_for:
      return HttpResponseRedirect(person.alias_for.get_absolute_url())
   else:
      expression_list = Expression.objects.filter(Q(work__creators=person) | Q(work__subjects=person.subject))
      subject_list = Subject.objects.filter(work__in=expression_list).distinct()
      image_list = expression_list.filter(form='image').distinct()
      expressions_by_list = expression_list.filter(work__creators=person).exclude(form='image').distinct()
      expressions_about_list = expression_list.filter(work__subjects=person.subject).exclude(form='image').distinct()

      t = loader.get_template('ervin/person.html')
      c = Context({
            'subject_list'           : subject_list,
            'person'                 : person,
            'image_list'             : image_list,
            'expressions_by_list'    : expressions_by_list,
            'expressions_about_list' : expressions_about_list
            })
      return HttpResponse(t.render(c))
