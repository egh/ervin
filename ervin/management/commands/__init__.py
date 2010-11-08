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
from rdflib import Namespace

class Base(NoArgsCommand):
    rdf_ns  = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    skos_ns = Namespace("http://www.w3.org/2004/02/skos/core#")
    dct_ns  = Namespace("http://purl.org/dc/terms/")
    bibo_ns = Namespace("http://purl.org/ontology/bibo/")

    def maybe_set(self, o, prop, value):
        if value != None:
            setattr(o, prop, value)
            
    def set_attributes(self, graph, what, ref, pairs):
        for (attr, pred,) in pairs:
            self.maybe_set(what, attr,
                           graph.value(ref, pred, None))
