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

from django.conf.urls.defaults import patterns
import ervin.models
urlpatterns = patterns(
    'ervin.views',
    (r'^concepts$', 'generic.list_view', {'class' : ervin.models.Concept }),
    (r'^events$', 'generic.list_view', {'class' : ervin.models.Event }),
    (r'^places$', 'generic.list_view', {'class' : ervin.models.Place }),
    (r'^objects$', 'generic.list_view', {'class' : ervin.models.FrbrObject }),
    (r'^persons$', 'person.index'),
    (r'^works$', 'generic.list_view', {'class' : ervin.models.Work }),
    (r'^unapi$', 'unapi.unapi'),
    (r'^(?P<noid>[a-z0-9-]{6})$', 'generic.by_noid'),
    (r'^$', 'main.home')
    )
