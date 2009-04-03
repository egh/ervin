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

from django.conf.urls.defaults import *
import ervin.models, ervin.feeds, django.contrib.syndication.views

urlpatterns = patterns('ervin.views',
    (r'^concepts$', 'generic.list_view', {'class' : ervin.models.Concept,
                                          'columns' : 4 }),
    (r'^events$', 'generic.list_view', {'class' : ervin.models.Event,
                                        'columns' : 4 }),
    (r'^places$', 'generic.list_view', {'class' : ervin.models.Place,
                                         'columns' : 4 }),
    (r'^objects$', 'generic.list_view', {'class' : ervin.models.FrbrObject }),
    (r'^persons$', 'generic.list_view', {'class' : ervin.models.Person,
                                         'columns' : 4 }),
    (r'^people$', 'generic.list_view', {'class' : ervin.models.Person,
                                         'columns' : 4 }),
    (r'^organizations$', 'generic.list_view', {'class' : ervin.models.Organization,
                                               'columns' : 4 }),
    (r'^works$', 'generic.list_view', {'class' : ervin.models.Work }),
    (r'^documents$', 'work.online_works'),
    (r'^physicaleditions$', 'generic.list_view', {'class' : ervin.models.PhysicalEdition }),
    (r'^unapi$', 'unapi.unapi'),
    (r'^doc/(?P<id>.*)$', 'page.by_id'),
    (r'^(?P<noid>[a-z0-9-]{6})$', 'generic.by_noid'),
    (r'^(?P<olkey>a/[A-Za-z0-9-]+)$', 'ol.author'),
    (r'^(?P<olkey>b/[A-Za-z0-9-]+)$', 'ol.edition'),
    (r"^feeds/(.*)$", django.contrib.syndication.views.feed, {
      "feed_dict": {
        "recent": ervin.feeds.RecentFeed,
      }
    }),
    (r'^search/', include('solango.urls')),
    (r'^$', 'main.home'),
)
