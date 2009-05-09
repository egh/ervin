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

from django.template import Context, loader, TemplateDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.conf import settings
from django.contrib.sites.models import Site

from ervin.models import *
from ervin.views.generic import *

def list_formats(request,iden):
        t = loader.get_template('ervin/unapi/format_list.xml')
        c = Context({'id': iden})
        return HttpResponse(t.render(c), status=300,
                            mimetype='application/xml')

CLASSES = [OnlineEdition, Expression, PhysicalEdition, Work]

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
                o = find_one(CLASSES, pk=request.GET['id'])
                if o == None: return HttpResponse(status=404)
                class_name = o.__class__.__name__.lower()
		t = loader.get_template('ervin/unapi/%s.%s.xml' % (class_name, format))
                c = Context({ class_name : o,
                              'base_url' : "http://%s"%(Site.objects.get_current().domain) })
                return HttpResponse(t.render(c),
                                    mimetype='application/xml')
            except TemplateDoesNotExist:
                return HttpResponse(status=406)
            except ObjectDoesNotExist:
                return HttpResponse(status=404)
