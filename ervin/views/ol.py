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
from django.http import HttpResponse,HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from ervin.openlibrary import ThingAuthor, ThingEdition

def author(request,*args,**kwargs):
    author = ThingAuthor(kwargs['olkey'])
    t = loader.get_template('ervin/ol_author.html')
    c = Context({ "author" : author })
    return HttpResponse(t.render(c))

def edition(request,*args,**kwargs):
    edition = ThingEdition(kwargs['olkey'])
    t = loader.get_template('ervin/ol_edition.html')
    c = Context({ "edition" : edition })
    return HttpResponse(t.render(c))
