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

def build_groups(q, max_size):
    startswith = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    groups = [('0'),('1'),('2'),('3'),('4'),('5'),('6'),('7'),('8'),('9'),('a'),('b'),('c'),('d'),('e'),('f'),('g'),('h'),('i'),('j'),('k'),('l'),('m'),('n'),('o'),('p'),('q'),('r'),('s'),('t'),('u'),('v'),('w'),('x'),('y'),('z')]
    count = {}
    for l in startswith:
        count[l] = q.filter(sort__startswith=l).count()
    finished = False
    
    while (not(finished)):
        # start with a count of the size of the total groups so far
        group_count = [ sum([ count[l] for l in groups[i] ])
                        for i in range(0,len(groups)) ]
        # we want to sort so that we first combine the smallest groups
        def cmp(a,b):
            return int((group_count[a]+group_count[a+1])-(group_count[b]+group_count[b+1]))
        i_list = range(0, len(groups)-1)
        i_list.sort(cmp)
        for i in i_list:
            # if the combined size will be less than max_size, group it
            if (group_count[i] + group_count[i+1]) < max_size:
                groups = groups[:i] + [(groups[i] + groups[i+1])] + groups[i+2:]
                break
        else:
            finished = True
    return groups

def group_to_re(group):
    return "^[%s]"%("".join(group))
        
def group_to_string(group):
    if len(group) == 1:
        return group[0].upper()
    else:
        return "%s-%s"%(group[0].upper(),group[-1].upper())
