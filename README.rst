ella-hub
========

.. _virtualenv: http://docs.python-guide.org/en/latest/starting/install/linux/#virtualenv
.. _`ella-hope`: https://github.com/SanomaCZ/ella-hope


API (not only) for Ella-Hope, brand new Ella/Django admin



Setting up
----------
1. install ella-hub

::

    # if you work with virtualenv
    source env_project/bin/activate

    git clone git://github.com/SanomaCZ/ella-hub.git
    cd ella-hub
    [sudo] pip install -r requirements.txt
    [sudo] python setup.py install


2. include ella-hub to *settings.py* in your ella project

::

    MIDDLEWARE_CLASSES = (
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        ...
        # neccessary for ella-hope with different origin
        'ella_hub.utils.middleware.CrossDomainAccessMiddleware',
    )

    INSTALLED_APPS = (
        ...
        'tastypie',
        ...
        'ella.core',
        'ella.articles',
        'ella.photos',
        ...
        'ella_hub',
        ...
    )

    # API resources
    RESOURCE_MODULES = (
        'ella_hub.ella_resources',
        # only when you are using ella-galleries application
        'ella_hub.extern_resources.ella_galleries_resources',
        # only when you are using ella-wikipages application
        'ella_hub.extern_resources.ella_wikipages_resources',
        # only when you are using django-taggit application
        'ella_hub.extern_resources.taggit_resources',
        # only when you are using daz-taggit application
        'ella_hub.extern_resources.daz_taggit_resources',
    )

    # Needed by object_permissions app (django-object-permissions)
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
    )


3. route resource URLs in *urls.py*

::

    # admin API setup
    from ella_hub.api import EllaHubApi
    from ella_hub.utils.workflow import init_ella_workflow
    admin_api = EllaHubApi('admin-api')
    resources = admin_api.collect_resources()
    admin_api.register_resources(resources)
    init_ella_workflow(resources)


    urlpatterns = patterns('',
        ...
        # /admin-api/[<resource_name>/[<id>/]]
        url(r'^', include(admin_api.urls)),
    )


4. update database of your project

::

    python manage.py syncdb



Build status
************

:Master branch:

  .. image:: https://secure.travis-ci.org/SanomaCZ/ella-hub.png?branch=master
     :alt: Travis CI - Distributed build platform for the open source community
     :target: http://travis-ci.org/#!/SanomaCZ/ella-hub
