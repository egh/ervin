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

import re
from django.core.cache import cache

def make_columns(data, col_count):
    l = len(data)
    r = l % col_count
    col_size = []
    cols = []
    for i in range(col_count):
        if (i > (r - 1)): col_size.append(l/col_count)
        else: col_size.append(l/col_count + 1)
    start = 0
    for i in range((col_count)):
        if i == col_count - 1: finish = l
        else: finish = (start + col_size[i])
        cols.append(data[start:finish])
        start = finish
    return cols
