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

from django.template import Context, loader, TemplateDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.conf import settings

from ervin.models import *
from ervin.views.generic import *

def list_formats(request,iden):
        t = loader.get_template('unapi/format_list.xml')
        c = Context({'id': iden})
        return HttpResponse(t.render(c), status=300,
                            mimetype='application/xml')
    
def unapi(request):
    if not(request.GET.has_key('id')):
        return list_formats(request, None)
    else:
        iden = request.GET['id']
        if not(request.GET.has_key('format')):
            return list_formats(request, iden)
        else:
            try:
                format = request.GET['format']
                work = Work.objects.get(slug=iden)
                edition = work.onlineedition_set.all()[0]
		t = loader.get_template('unapi/%s.xml' % format)
                c = Context({
                    'edition':edition,
                    'author_list':edition.work.authors.all(),
                    'subject_list':edition.work.subjects.all(),
		    'base_url':settings.BASE_URL
                    })
                return HttpResponse(t.render(c),
                                    mimetype='application/xml')
            except TemplateDoesNotExist:
                return HttpResponse(status=406)
            except ObjectDoesNotExist:
                return HttpResponse(status=404)
