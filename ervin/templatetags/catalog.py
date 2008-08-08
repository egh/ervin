#Copyright (C) 2007 Erik Hetzner

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
from django.db.models.query import QuerySet
import re, django
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.

register = template.Library()

def listfilter(func):
    def _dec(*args, **kwargs):
        if type(args[0]) != list and type(args[0]) != QuerySet:
            args[0] = [args[0]]
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
            if (person.noid == ignore): names.append (inverted_name (person))
            else: names.append (inverted_name_linked (person))
        else:
            if (person.noid == ignore): names.append (name (person))
            else: names.append (name_linked (person))
    return join_with_final(", ", " and ", names)

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
        else: names.append(name_linked(p))
    return join_with_final(", ", " and ", names)

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
    return join_with_final(",", " and ",
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
        if (arg != None) and (arg == person.noid): names.append(name (person))
        else: names.append(name_linked (person))
    return django.utils.safestring.mark_safe(join_with_final(",", " and ", names))

FINAL_PERIOD_RE = re.compile(".*\\.(</a>)?$")

@register.filter
@stringfilter
def with_final_period(value):
    if (value != "" and not(FINAL_PERIOD_RE.match(value))):
        return django.utils.safestring.mark_safe("%s."%(value))
    else:
        return value

@register.filter
def fix_isbn(value):
    import re
    return (re.compile("-")).sub("",value)

@register.filter
def publication_info(ed):
  try:	
    publisher = ed.publisher
    ret_val = ""
    if publisher != "":
      ret_val = "%s%s, "%(ret_val, publisher)
    return "%s%s. "%(ret_val, str(ed.pub_date.year))
  except AttributeError:
    return ""

@register.filter
def smartypants(value):
    try:
        import smartypants
        return smartypants.smartyPants(value)
    except:
        return value

SORT_STOP_RE = re.compile("^(the|a|an) ")
@register.filter
def sort_friendly(value):
    return re.sub(SORT_STOP_RE, "", value.lower())
