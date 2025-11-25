.. _reference-views:

View Classes Reference
======================

This is the API reference for View classes in Django IS Core. For conceptual information and usage examples, see :ref:`views`.

Form Views
----------

Add Views
^^^^^^^^^

.. autoclass:: is_core.generic_views.add_views.DjangoAddFormView
   :members:
   :show-inheritance:

Detail Views
^^^^^^^^^^^^

.. autoclass:: is_core.generic_views.detail_views.DjangoDetailFormView
   :members:
   :show-inheritance:

.. autoclass:: is_core.generic_views.detail_views.DjangoReadonlyDetailView
   :members:
   :show-inheritance:

Table Views
-----------

.. autoclass:: is_core.generic_views.table_views.DjangoTableView
   :members:
   :show-inheritance:

Inline Views
------------

Inline Form Views
^^^^^^^^^^^^^^^^^

.. autoclass:: is_core.generic_views.inlines.inline_form_views.TabularInlineFormView
   :members:
   :show-inheritance:

.. autoclass:: is_core.generic_views.inlines.inline_form_views.StackedInlineFormView
   :members:
   :show-inheritance:

.. autoclass:: is_core.generic_views.inlines.inline_form_views.ResponsiveInlineFormView
   :members:
   :show-inheritance:

Inline Table Views
^^^^^^^^^^^^^^^^^^

.. autoclass:: is_core.generic_views.inlines.inline_table_views.DjangoInlineTableView
   :members:
   :show-inheritance:

Base View Classes
-----------------

.. autoclass:: is_core.generic_views.base.DefaultCoreViewMixin
   :members:
   :show-inheritance:

.. autoclass:: is_core.generic_views.base.DefaultModelCoreViewMixin
   :members:
   :show-inheritance:
