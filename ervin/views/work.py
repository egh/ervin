from django.template import Context, loader
from ervin.models import *
from ervin.views.generic import *
from django.http import HttpResponse, HttpResponseRedirect

def by_noid(request, *args, **kwargs):
    work = Work.objects.get(noid=kwargs['noid'])
    return detail(work, request, *args, **kwargs)

def detail(work, request, *args, **kwargs):
    if len(work.expression_set.all()) == 1:
        return HttpResponseRedirect(work.expression_set.all()[0].get_absolute_url())
    

