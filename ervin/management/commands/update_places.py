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

from django.core.management.base import NoArgsCommand
import rdflib, sys
from rdflib.Graph import Graph
from ervin.models import *
from django.conf import settings

class Command(NoArgsCommand):
    help = "Update places from upstream sources."

    def_lang        = getattr(settings, "LANGUAGE_CODE")[0:2]
    prefLabel_ref   = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
    concept_ref     = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#Concept")
    type_ref        = rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    geoname_feature = rdflib.URIRef("http://www.geonames.org/ontology#Feature")
    geoname_name    = rdflib.URIRef("http://www.geonames.org/ontology#name")
    geoname_re      = re.compile(r'^http://www.geonames.org/[0-9]+/$')

    def handle_noargs(self, **options):
        for place in Place.objects.all():
            # Behavior is undefined for multiple sameas URIs
            for same_as in place.same_as_uri_set.all():
                u = same_as.uri
                ref = rdflib.URIRef(u)
                g = Graph()
                g.parse(ref)
                if self.concept_ref in g.objects(ref, self.type_ref):
                    for o in g.objects(ref, self.prefLabel_ref):
                        if o.language == self.def_lang:
                            place.name = o
                            place.save()
                if self.geoname_feature in g.objects(ref, self.type_ref):
                    for o in g.objects(ref, self.geoname_name):
                        place.name = o
                        place.save()
