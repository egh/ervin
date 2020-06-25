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

from ervin.management.commands import Base 
from ervin.models import PhysicalEdition, Person, Creatorship
from rdflib import URIRef
from rdflib.Graph import Graph
from rdflib.Collection import Collection
import ervin.isbn, re

class Command(Base):
    help = "Update editions (and works) from upstream sources."

    def handle_noargs(self, **options):
        for ed in PhysicalEdition.objects.all():
            work = ed.work
            # Behavior is undefined for multiple sameas URIs
            for same_as in ed.same_as_uri_set.all():
                g = Graph()
                g.parse(same_as.uri)
                ref = URIRef(re.sub(r"/$", "", str(same_as.uri)))
                if same_as.uri.startswith("http://openlibrary.org/books/"):
                    self.set_attributes(g, ed, ref,
                                        [('date', self.dct_ns['issued']),
                                         ('edition_title', self.dct_ns['title']),
                                         ('publisher', self.dct_ns['publisher'])])
                    isbn10 = g.value(ref, self.bibo_ns['isbn10'], None)
                    isbn13 = g.value(ref, self.bibo_ns['isbn13'], None)
                    if isbn13:
                        ed.isbn13 = isbn13
                    elif isbn10:
                        ed.isbn13 = ervin.isbn.toI13(isbn10)
                    authorList = g.value(ref, self.bibo_ns['authorList'], None)
                    if authorList:
                        c = Collection(g, authorList)
                        for a in c:
                            persons = Person.objects.filter(same_as_uri_set__uri=str(a))
                            if persons.count() == 0:
                                # add person here...
                                pass
                            else:
                                Creatorship(work=work, person=persons[0]).save()
                    ed.save()
                    
