from django.template import Context, loader
from erwin.models import *
from django.http import HttpResponse,HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
import erwin.views.generic
import erwin.views.person
import erwin.views.work
import erwin.views.expression

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
    for pair in ((Person, erwin.views.person.detail),
                 (Work, erwin.views.work.detail),
                 (Expression, erwin.views.expression.detail)):
        retval = try_view(pair[0], pair[1])
        if retval != None:
            return retval
    return HttpResponseNotFound('Not found')
