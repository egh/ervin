from django.template import Context, loader
from ervin.models import *
from django.http import HttpResponse,HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist

def by_id(*args, **kwargs):
    pages = Page.objects.filter(id=kwargs['id']).all()
    if len(pages) == 0:    
        return HttpResponseNotFound('Not found')
    else:
        t = loader.get_template('page.html')
        c = Context({ 'page' : pages[0] })
        return HttpResponse(t.render(c))
    

