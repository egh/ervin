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
from django.http import HttpResponse
from ervin.views import make_columns
from ervin.ol import ThingAuthor

def by_noid(request, *args, **kwargs):
   person = Person.objects.get(id=kwargs['noid'])
   return detail(person, request, *args, **kwargs)

def detail(person, request, *args,**kwargs):
   if person.alias_for:
      return HttpResponseRedirect(person.alias_for.get_absolute_url())
   else:
      work_list = Work.objects.filter(Q(authors=person) | Q(subjects=person.subject))
      subject_list = Subject.objects.filter(work__in=work_list).distinct()
      image_list = work_list.filter(form='image').distinct()
      text_list = person.authored.exclude(form='image').distinct()

      if person.olkey:
         ol_edition_list = ThingAuthor(person.olkey).fulltext_editions()
      else: ol_edition_list = None
      
      t = loader.get_template('person.html')
      c = Context({
            'subject_list' : subject_list,
            'person'       : person,
            'image_list'   : image_list,
            'text_list'    : text_list,
            'ol_list'      : ol_edition_list,
            })
      return HttpResponse(t.render(c))
