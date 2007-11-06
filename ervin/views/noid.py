from django.template import Context, loader
from ervin.models import *
from django.http import HttpResponse,HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
import ervin.views.generic
import ervin.views.person
import ervin.views.work
import ervin.views.expression

def by_noid(request,*args,**kwargs):
    n = kwargs['noid']
    def try_view(klass, view_func):
        try:
            o = klass.objects.get(noid=n)
            if o != None:
                return view_func(o,request,*args,**kwargs)
            else:
                return None
        except ObjectDoesNotExist:
            return None
    for pair in ((Person, ervin.views.person.detail),
                 (Work, ervin.views.work.detail),
                 (Expression, ervin.views.expression.detail)):
        retval = try_view(pair[0], pair[1])
        if retval != None:
            return retval
    return HttpResponseNotFound('Not found')
