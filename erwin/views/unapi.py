from django.template import Context, loader, TemplateDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.conf import settings

from erwin.models import *
from erwin.views.generic import *

def list_formats(request,iden):
        t = loader.get_template('unapi/format_list.xml')
        c = Context({'id': iden})
        return HttpResponse(t.render(c), status=300,
                            mimetype='application/xml')
    
def unapi(request):
    if not(request.GET.has_key('id')):
        return list_formats(request, None)
    else:
        iden = request.GET['id']
        if not(request.GET.has_key('format')):
            return list_formats(request, iden)
        else:
            try:
                format = request.GET['format']
                work = Work.objects.get(slug=iden)
                edition = work.onlineedition_set.all()[0]
		t = loader.get_template('unapi/%s.xml' % format)
                c = Context({
                    'edition':edition,
                    'author_list':edition.work.authors.all(),
                    'subject_list':edition.work.subjects.all(),
		    'base_url':settings.BASE_URL
                    })
                return HttpResponse(t.render(c),
                                    mimetype='application/xml')
            except TemplateDoesNotExist:
                return HttpResponse(status=406)
            except ObjectDoesNotExist:
                return HttpResponse(status=404)
