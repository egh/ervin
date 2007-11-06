from django.template import Context, loader
from erwin.models import *
from erwin.views.generic import *
from django.http import HttpResponse

def by_slug(request, *args, **kwargs):
   person = Person.objects.get(slug=kwargs['slug'])
   return detail(person, request, *args, **kwargs)

def by_noid(request, *args, **kwargs):
   person = Person.objects.get(noid=kwargs['noid'])
   return detail(person, request, *args, **kwargs)

def detail(person, request,*args,**kwargs):
   s = Subject.objects.get(slug=person.slug)
   docs_about = list(Work.objects.filter(subjects=s))
   docs_about.sort(title_sort)
   docs_by = list(Work.objects.filter(authors=person))
   docs_by.sort(title_sort)
   # collaborator_set = dict()
#    for d in docs_by:
#       for p in list(d.authors.all()):
#          collaborator_set[p] = p
#       for p in list(d.translators.all()):
#          collaborator_set[p] = p
#    if collaborator_set.has_key(person):
#       collaborator_set.pop(person)
#    collaborators = collaborator_set.values()      
#    collaborators.sort()

   subjects_set = dict()
   for w in docs_by:
      for s in w.subjects.all():
         subjects_set[s] = s
   for w in docs_about:
      for s in w.subjects.all():
         subjects_set[s] = s
   subjects = subjects_set.values()
   subjects.sort()
   
   t = loader.get_template('person/detail.html')
   c = Context({
	'sections': get_sections(),
        #'collaborators': collaborators,
        'subjects': subjects,
        'person': person,
        'docs_by': docs_by,
        'docs_about': docs_about})
   return HttpResponse(t.render(c))

def index(request):
    persons = list(Person.objects.all())
    persons.sort(lambda a,b: cmp(a.slug,b.slug))
    t = loader.get_template('person/index.html')
    c = Context({
        'persons': persons,
        'sections': get_sections(),
        })
    return HttpResponse(t.render(c))
