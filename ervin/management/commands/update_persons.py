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
    help = "Update persons from upstream sources."

    def_lang = getattr(settings, 'LANGUAGE_CODE')[0:2]
    type_ref = rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    dbprop_name_ref = rdflib.URIRef("http://dbpedia.org/property/name")
    dbprop_date_of_birth_ref = rdflib.URIRef("http://dbpedia.org/property/dateOfBirth")
    dbprop_date_of_death_ref = rdflib.URIRef("http://dbpedia.org/property/dateOfDeath")
    en_name_re = re.compile(r'^([^,]+), (.*)$')
    year_re = re.compile(r'^([0-9]{4})-.*$')

    def handle_noargs(self, **options):
        for person in Person.objects.all():
            # Behavior is undefined for multiple sameas URIs
            for same_as in person.same_as_uri_set.all():
                ref = rdflib.URIRef(same_as.uri)
                g = Graph()
                g.parse(ref)
                if same_as.uri.startswith("http://dbpedia.org/"):
                    birth_date = None
                    death_date = None
                    for o in g.objects(ref, self.dbprop_name_ref):
                        if o.language == self.def_lang:
                            md = self.en_name_re.match(o)
                            if md:
                                person.surname = md.group(1)
                                person.forename = md.group(2)
                                person.save()
                    for o in g.objects(ref, self.dbprop_date_of_birth_ref):
                        birth_date = self.year_re.match(o).group(1)
                    for o in g.objects(ref, self.dbprop_date_of_death_ref):
                        death_date = self.year_re.match(o).group(1)
                    if birth_date and death_date:
                        person.dates = "%s-%s"%(birth_date, death_date)
                        person.save()
