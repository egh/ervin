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

from django import template
from django.template.defaultfilters import stringfilter
from django.template import Library, Node
from django.db.models.query import QuerySet
from ervin.columnator import Columnator
import re, django, datetime
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.

register = template.Library()

def listfilter(func):
    def _dec(*args, **kwargs):
        if type(args[0]) != list and type(args[0]) != QuerySet:
            args = [[args[0]]] + args[1:]
        return func(*args, **kwargs)
    _dec._decorated_function = getattr(func, '_decorated_function', func)
    return wraps(func)(_dec)

def testemptylist(func):
    def _dec(*args, **kwargs):
        if len(args[0]) == 0: return ""
        else: return func(*args, **kwargs)
    _dec._decorated_function = getattr(func, '_decorated_function', func)
    return wraps(func)(_dec)

def join_with_final(join_string, final_join_string, join_list):
    n = 0
    s = ""
    for a in join_list:
        s = s + a
        n = n + 1
        if len(join_list) > n + 1:
            s = s + join_string
        elif len(join_list) == n + 1:
            s = s + final_join_string
    return s

@register.filter
def inverted_name (person):
    return "%s, %s"%(person.surname, person.forename)

@register.filter
def inverted_name_linked (person):
    return "<a href=\"%s\">%s, %s</a>"%(person.get_absolute_url(), person.surname, person.forename)

@register.filter
@listfilter
@testemptylist
def inverted_name_first_list_linked (persons, arg=""):
    """
    Prints name list with first name inverted (linked names).
    """
    ignore = None
    if (re.compile("[a-z0-9]+").match(arg)):
        ignore = arg
    names = []
    for (i, person) in enumerate(persons):
        if (i == 0):
            if (person.pk == ignore): names.append (inverted_name (person))
            else: names.append (inverted_name_linked (person))
        else:
            if (person.pk == ignore): names.append (name (person))
            else: names.append (name_linked (person))
    return join_with_final(", ", " and ", names)

@register.filter
@listfilter
@testemptylist
def inverted_name_first_etal_list_linked (persons, arg=""):
    """
    Prints name list with first name inverted (linked names), using et al. if authors > 3.
    """
    ignore = None
    if (re.compile("[a-z0-9]+").match(arg)):
        ignore = arg
    if len(persons) > 3:
        person = persons[0]
        if (person.pk == ignore): return "%s et al."%(inverted_name (person))
        else: return "%s et al."%(inverted_name_linked (person))
    else:
        return inverted_name_first_list_linked (persons, arg)

@register.filter
@listfilter
@testemptylist
def inverted_name_first_list (persons):
    """
    Prints name list with first name inverted
    """
    names = []
    for (i, person) in enumerate(persons):
        if (i == 0): names.append(inverted_name(person))
        else: names.append(name_linked(person))
    return join_with_final(", ", " and ", names)

@register.filter
@listfilter
@testemptylist
def inverted_name_first_etal_list (persons):
    """
    Prints name list with first name inverted, using et al. if authors > 3.
    """
    if len(persons) > 3:
        return "%s et al."%(inverted_name (persons[0]))
    else:
        return inverted_name_first_list (persons)

@register.filter
def name_linked(person):
    return "<a href=\"%s\">%s %s</a>"%(person.get_absolute_url(), person.forename, person.surname)

@register.filter
def name(person):
    return "%s %s"%(person.forename, person.surname)

@register.filter
@listfilter
@testemptylist
def name_list(people):
    return join_with_final(", ", " and ",
                           [name (p) for p in people])

@register.filter
@listfilter
@testemptylist
def name_list_linked(persons,arg=""):
    ignore = None
    if (re.compile("[a-z0-9]+").match(arg)):
        ignore = arg
    names = []
    for person in persons:
        if (arg != None) and (arg == person.pk): names.append(name (person))
        else: names.append(name_linked (person))
    return django.utils.safestring.mark_safe(join_with_final(", ", " and ", names))

FINAL_PERIOD_RE = re.compile(".*\\.(</a>)?$")

@register.filter
@stringfilter
def with_final_period(value):
    if (value != "" and not(FINAL_PERIOD_RE.match(value))):
        return django.utils.safestring.mark_safe("%s."%(value))
    else:
        return value

TERMINAL_RE = re.compile("(</a>)$")

@register.filter
@stringfilter
def with_terminal(value, arg):
    if (value != "" and not(TERMINAL_RE.sub("",value).endswith(arg))):
        return django.utils.safestring.mark_safe("%s%s"%(value,arg))
    else:
        return value
    
@register.filter
def fix_isbn(value):
    import re
    return (re.compile("-")).sub("",value)

@register.filter
def smartypants(value):
    try:
        import smartypants
        return smartypants.smartyPants(value)
    except:
        return value

SORT_STOP_RE = re.compile("^(the|a|an|de) ")
INT_RE = re.compile("^[0-9]+$")
ALL_INT_RE = re.compile("[0-9]+")

@register.filter
def sort_friendly(value):
    def pad_ints(s):
        if (ALL_INT_RE.match(s)):
           return "%09i"%(int(s))
        else: return s
    padded_value = "".join([ pad_ints(c) for c in re.split("([0-9]+)", value) ])
    return re.sub(SORT_STOP_RE, "", padded_value.lower())

@register.filter
def freeformdate(value):
    from django.utils.dateformat import format
    if (type(value) == str or type(value) == unicode):
        return value
    elif type(value) == datetime.datetime:
        return format(value, "j F Y")
    else: return ""

class ColumnatorNode(Node):
    def __init__(self, var, column_count, column_var):
        self._column_var = column_var
        self._var = template.Variable(var)
        self._column_count = column_count

    def render(self, context):
        try:
            context[self._column_var] = Columnator(self._var.resolve(context), self._column_count)
        except template.VariableDoesNotExist:
            pass
        return ''
        
#{% build_columns var [columns] as column_var %}
def make_columns(parser, token):
    bits = token.split_contents()
    if len(bits) != 4 and len(bits) != 5:
        raise template.TemplateSyntaxError, "make_columns tag takes three or four arguments"
    if len(bits) == 4:
        if bits[2] != 'as':
            raise template.TemplateSyntaxError, "second argument to the make_columns tag must be 'as' if column count is not present"
        column_count = 5
        column_var = bits[3]
    if len(bits) == 5:
        if bits[3] != 'as':
            raise template.TemplateSyntaxError, "third argument to the make_columns tag must be 'as' if column count is present"
        column_count = int(bits[2])
        column_var = bits[4]
    return ColumnatorNode(bits[1], column_count, column_var)
    
make_columns = register.tag(make_columns)

