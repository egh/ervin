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
from ervin.views.generic import *
from django.http import HttpResponse

def home(request, *args, **kwargs):
    t = loader.get_template('ervin/home.html')
    recent_online_editions = OnlineEdition.objects.order_by('-date_sort').all()[0:5]
    c = Context({'recent_online_editions': recent_online_editions})
    return HttpResponse(t.render(c))
