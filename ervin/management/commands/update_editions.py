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

from ervin.management.commands import Base 
from ervin.models import PhysicalEdition
from rdflib import URIRef
from rdflib.Graph import Graph
import ervin.isbn

class Command(Base):
    help = "Update editions (and works) from upstream sources."

    def handle_noargs(self, **options):
        for ed in PhysicalEdition.objects.all():
            work = ed.work
            # Behavior is undefined for multiple sameas URIs
            for same_as in ed.same_as_uri_set.all():
                ref = URIRef(same_as.uri)
                g = Graph()
                g.parse(ref)
                if same_as.uri.startswith("http://openlibrary.org/books/"):
                    self.maybe_set(work, 'work_title',
                                   g.value(ref, self.dct_ns['title'], None))
                    self.maybe_set(ed, 'date',
                                   g.value(ref, self.dct_ns['issued'], None))
                    isbn10 = g.value(ref, self.bibo_ns['isbn10'], None)
                    isbn13 = g.value(ref, self.bibo_ns['isbn13'], None)
                    if isbn13:
                        ed.isbn13 = isbn13
                    elif isbn10:
                        ed.isbn13 = ervin.isbn.toI13(isbn10)
                    work.save()
                    ed.save()
                    
