from django import template
from django.db.models.query import QuerySet
import re

register = template.Library()
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

def last_name_first (value):
    """
    Prints name list with first name first.
    """
    if type(value) != list and type(value) != QuerySet:
        return last_name_first([value])
    elif type(value) == list or type(value) == QuerySet:
        if len(value) == 0:
            return ""
        names = ["<a href=\"" + value[0].get_absolute_url() + "\">" +
                 value[0].surname + ", " + value[0].forename + "</a>"]
        if (len(value) > 1):
            names = names + ["<a href=\"" + p.get_absolute_url() + "\">" +
                             p.forename + " " + p.surname + "</a>"
                             for p in value[1:]]
        return join_with_final(", ", " and ", names)
        
register.filter(last_name_first)

def name_list(people,arg):
    if (len(people) > 0):
        return arg + join_with_final(",", " and ",
                                     [p.forename + " " +
                                      p.surname for p in people])
    else:
        return ""
register.filter(name_list)

def with_final_period(value):
    import re
    my_re = re.compile(".*\\.(</a>)?$")
    if (value != None and value != "" and not(my_re.match(value))):
        return value + "."
    else:
        return value
register.filter(with_final_period)

def fix_isbn(value):
    import re
    return (re.compile("-")).sub("",value)
register.filter(fix_isbn)

def publication_info(ed):
  try:	
    publisher = ed.publisher
    ret_val = ""
    if publisher != "":
      ret_val = ret_val + publisher + ", "
    return ret_val + str(ed.pub_date.year) + ". "
  except AttributeError:
    return ""

register.filter(publication_info)

def smartypants(value):
    try:
        import smartypants
        return smartypants.smartyPants(value)
    except:
        return value
register.filter(smartypants)
