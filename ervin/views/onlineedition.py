#Copyright (C) 2007-2020, Erik Hetzner

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
from django.core.paginator import Paginator

def detail(ed, request, *args,**kwargs):
    t = None
    if ed.expression.form == 'StillImage':
        print ed.expression.form
        t = loader.get_template('ervin/onlineedition_image.html')
    else:
        t = loader.get_template('ervin/onlineedition.html')
    c = Context({ 'entity' : ed})
    if len(ed.content_remote.all()) == 0 and len(ed.content_db.all()) == 1 and len(ed.content_file.all()) == 0:
        c['data'] = ed.content_db.all()[0].data
    else:
        contents = {}
        for sec in list(ed.content_db.all()) + list(ed.content_file.all()) + list(ed.content_remote.all()):
            if not(contents.has_key(sec.name)):
                contents[sec.name] = []
            contents[sec.name].append(sec)
        c['contents'] = contents
    return HttpResponse(t.render(c))
    
def recently_online(request, *args, **kwargs):
    page_n = int(request.GET.get('page','1'))
    edition_paginator = Paginator(OnlineEdition.with_content.order_by('-date'), 20,'recently_online').page(page_n)
    t = loader.get_template('ervin/work_list.html')
    c = Context({ 
            "page" : page
            })
    return HttpResponse(t.render(c))
