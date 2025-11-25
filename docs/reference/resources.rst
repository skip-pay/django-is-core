.. _reference-resources:

Resource Classes Reference
==========================

This is the API reference for REST Resource classes in Django IS Core. For conceptual information and usage examples, see :ref:`rests`.

Base Resources
--------------

.. autoclass:: is_core.rest.resource.BaseResource
   :members:
   :show-inheritance:

Django Core Resources
---------------------

.. autoclass:: is_core.rest.resource.DjangoCoreResource
   :members:
   :show-inheritance:

.. autoclass:: is_core.rest.resource.DjangoResource
   :members:
   :show-inheritance:

Specialized Resources
---------------------

.. note::
   CeleryDjangoCoreResource requires the ``security`` library to be installed.

.. .. autoclass:: is_core.contrib.background_export.resource.CeleryDjangoCoreResource
..    :members:
..    :show-inheritance:

Serializers
-----------

.. note::
   Django IS Core uses Pyston's serialization framework. See the `Pyston documentation <https://github.com/druids/django-pyston>`_ for details on serializers.

Paginators
----------

.. autoclass:: is_core.rest.paginators.DjangoOffsetBasedPaginator
   :members:
   :show-inheritance:
