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

class Columnator(object):
    def __init__(self, data, column_count=5):
        self.column_count = column_count
        self._data = data
        if type(self._data) == list:
            l = len(data)
        else:
            l = data.count()
        self._remainder = l % self.column_count
        self._base = l / self.column_count

    def __len__(self):
        return self.column_count
    
    def __getitem__(self,i):
        if type(i) != int or i < 0 or i >= len(self):
            raise IndexError
        start = i * self._base + min(i, self._remainder)
        if (i >= self._remainder):
            add_one = 0
        else:
            add_one = 1
        end = start + self._base + add_one
        return self._data[start:end]

    def __iter__(self):
        return Columnator.Iter(self)

    class Iter(object):
        def __init__(self, columnator):
            self._columnator = columnator
            self._index = 0

        def __iter__(self):
            return self

        def next(self):
            if self._index == len(self._columnator):
                raise StopIteration()
            retval = self._columnator[self._index]
            self._index = self._index+1
            return retval

