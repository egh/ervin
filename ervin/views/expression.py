from django.template import Context, loader
from ervin.models import *
import ervin.views.generic
from django.http import HttpResponse, HttpResponseRedirect

def by_noid(request, *args, **kwargs):
    expression = Expression.objects.get(noid=kwargs['noid'])
    return detail(expression, request, *args, **kwargs)

def detail(expression, request, *args, **kwargs):
    manifestations = expression.get_manifestations()
    if len(manifestations) == 1:
        return HttpResponseRedirect(manifestations[0].get_absolute_url())
    
    
