#Copyright (C) 2007-2010, Erik Hetzner

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
import rdflib, re, sys
from rdflib.Graph import Graph
from ervin.models import *
from django.conf import settings

class Command(NoArgsCommand):
    help = "Update concepts from upstream sources."

    def_lang = getattr(settings, 'LANGUAGE_CODE')[0:2]
    
    skos_ns = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
    rdf_ns = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    en_name_re = re.compile(r'^([^,]+), (.*)$')

    def handle_noargs(self, **options):
        for concept in Concept.objects.all():
            # Behavior is undefined for multiple sameas URIs
            for same_as in concept.same_as_uri_set.all():
                ref = rdflib.URIRef(same_as.uri)
                g = Graph()
                g.parse(ref)
                for o in g.objects(ref, self.skos_ns["prefLabel"]):
                    if o.language == self.def_lang:
                        concept.name = o
                        concept.save()
