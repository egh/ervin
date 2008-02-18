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
from django.http import HttpResponse
import re

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
