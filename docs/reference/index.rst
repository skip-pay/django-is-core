.. _reference:

API Reference
=============

This section contains the complete API reference for Django IS Core, automatically generated from the source code docstrings.

For conceptual guides and usage examples, see the main documentation sections.

.. toctree::
   :maxdepth: 2

   cores
   views
   resources

Core Classes
------------

The Core classes are the central controllers that connect models with UI views and REST resources.

See :doc:`cores` for the complete Core API reference.

Key classes:

- :class:`is_core.main.DjangoUiRestCore` - Combined UI and REST Core
- :class:`is_core.main.DjangoUiCore` - UI-only Core
- :class:`is_core.main.DjangoRestCore` - REST-only Core

View Classes
------------

View classes handle the UI presentation layer, rendering forms, tables, and detail pages.

See :doc:`views` for the complete View API reference.

Key classes:

- :class:`is_core.generic_views.table_views.DjangoTableView` - List view with filtering
- :class:`is_core.generic_views.add_views.DjangoAddFormView` - Add new object form
- :class:`is_core.generic_views.detail_views.DjangoDetailFormView` - Edit object form

Resource Classes
----------------

Resource classes provide the REST API layer, handling JSON serialization and CRUD operations.

See :doc:`resources` for the complete Resource API reference.

Key classes:

- :class:`is_core.rest.resource.DjangoCoreResource` - Standard CRUD resource
- :class:`is_core.rest.resource.BaseResource` - Custom endpoint resource
- :class:`is_core.contrib.background_export.resource.CeleryDjangoCoreResource` - Async operations
