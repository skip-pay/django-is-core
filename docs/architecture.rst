.. _architecture:

Architecture
============

Django IS Core is built on a modular architecture that separates UI rendering, REST API resources, and business logic. This section provides an overview of the core concepts and how they work together.

Core Concepts
-------------

The framework is built around several key concepts:

**Core**
  The main organizational unit that groups related views and REST resources together. A Core acts as a "roof" or container for functionality, automatically generating REST endpoints and managing URL patterns.

**Views**
  Server-rendered templates (HTML) or components that bootstrap JavaScript which then fetches data from REST endpoints. Views handle the UI presentation layer.

**Forms**
  Handle validation, sanitization of input, and rendering of fields through widgets. Forms are also used for read-only display states.

**Resources (REST)**
  Classes that define REST endpoints (GET/POST/PUT/DELETE) acting as the backend for UI actions. Resources provide the data and actions that views consume.

Request Flow
------------

An example request flow in Django IS Core:

.. image:: .images/iscore-arch.png
   :alt: IS Core Architecture Diagram
   :align: center
   :width: 200%

The flow in detail:

1. **Initial Request**: Browser hits a URL → View returns HTML template with links to JS/static files
2. **Static Assets**: Browser loads JavaScript, CSS, and images from static files
3. **Data Loading**: JavaScript calls the appropriate Core's REST endpoint for data (e.g., to populate a table)
4. **Interactive Updates**: Further interactions (filtering, row actions) go through REST → JS updates the DOM

Types of Core
-------------

Django IS Core provides several types of Core classes that can be combined based on your needs. For detailed information on working with cores, see :doc:`cores`.

Which Core Type Should I Use?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+---------------------------+---------------------------+---------------------------+
| **Use Case**              | **Core Type**             | **What You Get**          |
+===========================+===========================+===========================+
| Full admin interface      | DjangoUiRestCore          | UI views + REST API       |
+---------------------------+---------------------------+---------------------------+
| REST API only             | DjangoRestCore            | API endpoints only        |
+---------------------------+---------------------------+---------------------------+
| UI with external API      | DjangoUiCore              | UI views (REST elsewhere) |
+---------------------------+---------------------------+---------------------------+
| Custom frontend (React)   | DjangoRestCore            | API for your frontend     |
+---------------------------+---------------------------+---------------------------+
| Static pages only         | UiCore                    | Simple server-side views  |
+---------------------------+---------------------------+---------------------------+

UI Core
^^^^^^^

Handles server-side rendered views without REST queries during interaction. Useful for simple, static pages.

**API Reference**: :class:`is_core.main.UiCore`

REST Core
^^^^^^^^^

Generates REST API over models providing CRUD operations, pagination, filtering, etc. Can be used independently to build custom frontends (e.g., React, Vue).

**API Reference**: :class:`is_core.main.RestCore`

Django UI Core
^^^^^^^^^^^^^^

A UI Core specialized for Django models providing default list/detail/create views automatically.

**API Reference**: :class:`is_core.main.DjangoUiCore`

Django REST Core
^^^^^^^^^^^^^^^^

Default REST API over Django models with automatic CRUD endpoints.

**API Reference**: :class:`is_core.main.DjangoRestCore`

Combined Core (DjangoUiRestCore)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The most common case - combines UI + REST in a single Core. Provides both the admin interface and the REST API that powers it.

**API Reference**: :class:`is_core.main.DjangoUiRestCore`

.. tip::
   **Recommended**: Use ``DjangoUiRestCore`` for most use cases. It gives you both admin UI and REST API with a single class definition.

Example::

    from is_core.main import DjangoUiRestCore

    class ArticleCore(DjangoUiRestCore):
        model = Article
        list_fields = ('title', 'author', 'created_at')
        fields = ('title', 'content', 'author')

Registration and Auto-discovery
--------------------------------

Django IS Core uses automatic registration through metaclasses and singletons:

Architecture Overview
^^^^^^^^^^^^^^^^^^^^^

.. image:: .images/core-registration.png
   :alt: Core Registration Architecture
   :align: center
   :width: 800px

Registration Process
^^^^^^^^^^^^^^^^^^^^

1. **Django Apps Discovery**: ``INSTALLED_APPS`` → IS Core singleton (``ISSite``) discovers all apps
2. **Automatic Import**: In each app listed in ``INSTALLED_APPS``, the ``cores.py`` module is automatically imported (if it exists)
3. **Metaclass Registration**: Core classes use the ``CoreBase`` metaclass which automatically registers them into the ``CoresLoader`` singleton when the class is defined
4. **URL Generation**: In ``urls.py``, importing the IS Core singleton generates complete URLs including admin routes

Example of automatic registration::

    # myapp/cores.py
    from is_core.main import UIRestCore
    from .models import Article

    class ArticleCore(UIRestCore):
        model = Article
        # This Core is automatically registered when the module is imported
        # The CoreBase metaclass calls CoresLoader.register_core(ArticleCore)

Resources and Actions
---------------------

Generic Resource
^^^^^^^^^^^^^^^^

A custom endpoint where you implement get/post/put/delete methods. Resources are registered by returning them from a Core's ``get_rest_patterns()`` method. See :ref:`custom_url_patterns` for details on registering custom resources.

Example::

    from is_core.rest.resource import BaseResource

    class CustomResource(BaseResource):
        def get(self, request):
            return {'status': 'ok', 'data': [...]}

        @classmethod
        def get_rest_patterns(cls):
            return patterns(
                url(r'^custom-endpoint/$', cls.as_view(), name='custom'),
            )

DjangoCoreResource
^^^^^^^^^^^^^^^^^^

An internal "model resource" providing ready-made CRUD over a model. Behavior can be extended or overridden.

List Actions
^^^^^^^^^^^^

The backend returns a list of actions for each row via ``get_list_actions``. For more details, see :ref:`list_actions`.

**UI actions**
  e.g., redirect to detail view (without calling backend)

**API actions**
  e.g., delete action that calls REST; JavaScript executes the call and handles UI consequences (hide row, refresh, etc.)

Example::

    class ArticleCore(UIRestCore):
        model = Article

        def get_list_actions(self, obj, request):
            actions = []
            if request.user.has_perm('articles.change_article'):
                actions.append({
                    'name': 'edit',
                    'url': self.get_edit_url(obj),
                    'type': 'ui'
                })
            if request.user.has_perm('articles.delete_article'):
                actions.append({
                    'name': 'delete',
                    'url': self.get_api_url('delete', obj.pk),
                    'type': 'api'
                })
            return actions

