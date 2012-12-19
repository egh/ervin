Ervin
=====

Installing
----------

Requirements
~~~~~~~~~~~~

Noid. http://search.cpan.org/dist/Noid/

Steps
~~~~~
::

  ERVIN_VENV=$HOME/ervin-demo

  virtualenv --distribute --no-site-packages $ERVIN_VENV

  cd $ERVIN_VENV

  source bin/activate

  pip install Django==1.3.1

  pip install MySQL-python==1.2.3

  pip install distribute==0.6.15

  pip install httplib2==0.6.0

  pip install python-memcached==1.47

  pip install simplejson==2.1.5

  pip install smartypants==1.6.0.3

  pip install sorl-thumbnail==11.05.1

  pip install wsgiref==0.1.2

  pip install ftp://xmlsoft.org/libxml2/python/libxml2-python-2.6.9.tar.gz

  cd /tmp && svn checkout http://django-solr-search.googlecode.com/svn/trunk/ \
    django-solr-search-read-only && cd django-solr-search-read-only && \
    python setup.py install

  cd $ERVIN_VENV/lib/python*/site-packages/ && \
    svn co http://django-atompub.googlecode.com/svn/trunk/atompub/ 

  cd /tmp && bzr clone lp:ervin && cd ervin && python setup.py install

Install Noid::

 $ sudo perl -MCPAN -e "install Noid" # change sudo for your platform as necessary

Start project
=============

::

  cd $ERVIN_VENV

  django-admin.py startproject ervintest

  cd ervintest

Use your editor to configure the database in ``settings.py``. Add
``ervin`` and ``django.contrib.admin`` to ``INSTALLED_APPS``, e.g.::

 INSTALLED_APPS = (
     'django.contrib.auth',
     'django.contrib.admin',
     'django.contrib.contenttypes',
     'django.contrib.sessions',
     'django.contrib.sites',
     'ervin'
 )

Edit ``urls.py`` appropriately. For instance::

  from django.conf.urls.defaults import *

  from django.contrib import admin
  admin.autodiscover()

  urlpatterns = patterns('',
      (r'^admin/', include(admin.site.urls)),
      (r'', include('ervin.urls')),
  )

Setup the database & run the server::

  python $ERVIN_VENV/ervintest/manage.py syncdb

  python $ERVIN_VENV/ervintest/manage.py runserver

Setup Noid
==========

::

  cd $ERVIN_VENV/ervintest/ && noid dbcreate .reeeeek

Visit http://localhost:8000/admin and begin adding data!

