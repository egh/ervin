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

    def_lang = getattr(settings, "LANGUAGE_CODE")[0:2]
    rdf_ns = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    dbprop_ns = rdflib.Namespace("http://dbpedia.org/property/")
    foaf_ns = rdflib.Namespace("http://xmlns.com/foaf/0.1/")
    bio_ns = rdflib.Namespace("http://purl.org/vocab/bio/0.1/")
    dcterms_ns = rdflib.Namespace("http://purl.org/dc/terms/")
    en_name_inverted_re = re.compile(r'^([^,]+), (.*)$')
    en_name_re = re.compile(r'^(.*) ([^ ]+)$')
    year_re = re.compile(r'^([0-9]{4})-.*$')
    ol_year_re = re.compile(r'^.*([0-9]{4})$')

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
                    for o in g.objects(ref, self.dbprop_ns['name']):
                        if o.language == self.def_lang:
                            md = self.en_name_inverted_re.match(o)
                            if md:
                                person.surname = md.group(1)
                                person.forename = md.group(2)
                                person.save()
                    for o in g.objects(ref, self.dbprop_ns['dateOfBirth']):
                        birth_date = self.year_re.match(o).group(1)
                    for o in g.objects(ref, self.dbprop_ns['dateOfDeath']):
                        death_date = self.year_re.match(o).group(1)
                    if birth_date and death_date:
                        person.dates = "%s-%s"%(birth_date, death_date)
                        person.save()
                elif self.foaf_ns['Person'] in g.objects(ref, self.rdf_ns['type']) or \
                        self.foaf_ns['person'] in g.objects(ref, self.rdf_ns['type']):
                    for o in g.objects(ref, self.foaf_ns['name']):
                        md = self.en_name_re.match(o)
                        if md:
                            person.surname = md.group(2)
                            person.forename = md.group(1)
                            person.save()
                    birth_date = None
                    death_date = None
                    for o in g.objects(ref, self.bio_ns['event']):
                        if self.bio_ns['Birth'] in g.objects(o, self.rdf_ns['type']):
                            for date in g.objects(o, self.dcterms_ns['date']):
                                birth_date = self.ol_year_re.match(date).group(1)
                        elif self.bio_ns['Death'] in g.objects(o, self.rdf_ns['type']):
                            for date in g.objects(o, self.dcterms_ns['date']):
                                death_date = self.ol_year_re.match(date).group(1)
                    if birth_date and death_date:
                        person.dates = "%s-%s"%(birth_date, death_date)
                        person.save()
