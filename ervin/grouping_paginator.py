from django.core.cache import cache
import django.core.paginator
import re

class GroupingPaginator(django.core.paginator.Paginator):
    _GROUP_START = [['0'],['1'],['2'],['3'],['4'],['5'],['6'],['7'],['8'],['9'],['a'],['b'],['c'],['d'],['e'],['f'],['g'],['h'],['i'],['j'],['k'],['l'],['m'],['n'],['o'],['p'],['q'],['r'],['s'],['t'],['u'],['v'],['w'],['x'],['y'],['z']]

    def __init__(self, object_list, per_page, key=None, allow_empty_first_page=True):
        self.object_list = object_list
        self.per_page = per_page
        self.allow_empty_first_page = allow_empty_first_page
        if key != None: self._groups = cache.get(key)
        if self._groups == None:
            self._groups = self._build_groups(self.object_list, self.per_page)
            if key != None: cache.set(key, self._groups, 600)

    def group_names(self):
        return [ self._group_to_string(g) for g in self._groups ]

    def has_other_pages(self):
        return len(self._groups) > 1

    def _group_to_string(self, group):
        if len(group) == 1:
            return self._readable_char(group[0])
        else:
            return "%s-%s"%(self._readable_char(group[0]),self._readable_char(group[-1]))

    def _readable_char(self, c):
        if (re.match('^[0-9]$', c)):
            return '(Numerals)'
        else:
            return c.upper()
        
    def _group_to_re(self, group):
        return "^[%s]"%("".join(group))

    def _build_groups(self, q, max_size):
        #clone _GROUP_START
        groups = []
        groups[:] = self._GROUP_START[:]
        letter_count = {}
        for group in groups:
            letter = group[0]
            letter_count[letter] = q.filter(sort__startswith=letter).count()
        # remove all groups where the count is 0 to begin with
        groups = filter(lambda group: (letter_count[group[0]] > 0), groups)
        finished = False
        while (not(finished)):
            if (len(groups)) == 1:
                finished = True
            else:
                # start with a count of the size of each of the groups so far
                group_count = [ sum([ letter_count[letter] for letter in groups[i] ])
                                for i in range(0,len(groups)) ]
                # we want to sort so that the smallest groups are grouped first
                def my_cmp(a,b):
                    return int((group_count[a]+group_count[a+1])-(group_count[b]+group_count[b+1]))
                # find the index of the first (smallest) group
                tmp = sorted(range(0, len(groups)-1), my_cmp)
                if len(tmp) == 0:
                    finished = True
                else:
                    i = tmp[0]
                    # if the smallest group combined with its neighbor to the right will be less than max_size, group it
                    if (group_count[i] + group_count[i+1]) < max_size:
                        groups = groups[:i] + [(groups[i] + groups[i+1])] + groups[i+2:]
                    else:
                        finished = True
        return groups

    def _get_count(self):
        return len(self._groups)
    count = property(_get_count)

    def validate_number(self, number):
        "Validates the given 1-based page number."
        try:
            number = int(number)
        except ValueError:
            raise django.core.paginator.PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise django.core.paginator.EmptyPage('That page number is less than 1')
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise django.core.paginator.EmptyPage('That page contains no results')
        return number

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        if len(self._groups) == 0:
            return Page([], number, self)
        else:
            page_object_list = self.object_list.filter(sort__iregex=self._group_to_re(self._groups[number-1]))
            return Page(page_object_list, number, self)

    def _get_num_pages(self):
        "Returns the total number of pages."
        return len(self._groups)
    num_pages = property(_get_num_pages)

    def _get_page_range(self):
        """
        Returns a 1-based range of pages for iterating through within
        a template for loop.
        """
        return range(1, self.num_pages + 1)
    page_range = property(_get_page_range)

class Page(django.core.paginator.Page):
    def __init__(self, object_list, number, paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator

    def start_index(self):
        raise Exception("Not allowed.")

    def end_index(self):
        raise Exception("Not allowed.")

    def _get_count(self):
        return self.object_list.count()
    count = property(_get_count)

    def group_name(self):
        return self.paginator.group_names()[self.number-1]
    
