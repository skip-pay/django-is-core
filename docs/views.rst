.. _views:

Views
=====

Django IS Core provides a comprehensive set of generic views for building admin interfaces. Views handle the UI presentation layer and can work in two modes:

1. **Server-side rendered**: Traditional Django template rendering
2. **AJAX-powered**: HTML structure with data loaded via REST endpoints

View Types Overview
-------------------

When to Use Which View
^^^^^^^^^^^^^^^^^^^^^^

+---------------------------+---------------------------+---------------------------+
| **Need**                  | **View Type**             | **Example Use Case**      |
+===========================+===========================+===========================+
| List objects              | DjangoTableView           | User management list      |
+---------------------------+---------------------------+---------------------------+
| Create new object         | DjangoAddFormView         | New article form          |
+---------------------------+---------------------------+---------------------------+
| Edit object               | DjangoDetailFormView      | Edit user profile         |
+---------------------------+---------------------------+---------------------------+
| View-only details         | DjangoReadonlyDetailView  | Archive viewer            |
+---------------------------+---------------------------+---------------------------+
| Edit with related items   | Inline views              | Order + line items        |
+---------------------------+---------------------------+---------------------------+
| Bulk operations           | BulkChangeFormView        | Change status of many     |
+---------------------------+---------------------------+---------------------------+

Form Views
^^^^^^^^^^

Form views handle user input through Django forms. They provide validation, sanitization, and rendering of form fields.

**Key characteristics:**

- Server-side rendering with ``form_class``
- Implement GET (render form) and POST (validation, save)
- Support for read-only fields
- Automatic widget rendering with custom IS Core widgets

Table Views
^^^^^^^^^^^

Table views display lists of model instances with interactive features like filtering, sorting, and pagination.

**Key characteristics:**

- Data loaded via REST endpoints
- HTML contains only structure/headers
- Require ``get_list_filter`` method to define queryset
- Support for exports (XLSX, PDF, CSV)
- Configurable columns via ``list_display``

Object Views
^^^^^^^^^^^^

Read-only server-side rendered views for displaying object details without editing capabilities.

**Key characteristics:**

- Server-side rendering
- Static HTML (no AJAX)
- Useful for simple overview pages

Add Views
---------

Views for creating new model instances.

DjangoAddFormView
^^^^^^^^^^^^^^^^^

Generic view in ``is_core.generic_views.add_views`` for generating add UI from Django model classes.

**Configuration:**

- Always related to a Core
- Configuration (fields, permissions) can be defined in the view or Core
- Inherits from ``DjangoFormView``

Example::

    from is_core.generic_views.add_views import DjangoAddFormView
    from .models import Article
    from .forms import ArticleForm

    class ArticleAddView(DjangoAddFormView):
        model = Article
        form_class = ArticleForm
        fields = ('title', 'content', 'author', 'published_at')

Detail Views
------------

Views for displaying and editing existing model instances.

DjangoDetailFormView
^^^^^^^^^^^^^^^^^^^^

Editable detail view that combines display and edit functionality.

**Features:**

- Displays object details with edit form
- Submit triggers REST API call
- Supports inline editing of related objects
- Automatic foreign key link generation

Example::

    from is_core.generic_views.detail_views import DjangoDetailFormView

    class ArticleDetailView(DjangoDetailFormView):
        model = Article
        form_class = ArticleForm
        fieldsets = (
            (_('Basic Information'), {'fields': ('title', 'author')}),
            (_('Content'), {'fields': ('content', 'excerpt')}),
        )

DjangoReadonlyDetailView
^^^^^^^^^^^^^^^^^^^^^^^^^

Read-only detail view for displaying object information without edit capability.

**Use cases:**

- Viewing archived objects
- Display-only permissions
- Audit/history views

DjangoRelatedCoreTableView
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Displays a table of related objects within a detail view.

**Example:** Show all comments for an article in the article detail page.

List/Table Views
----------------

DjangoTableView
^^^^^^^^^^^^^^^

Main table view for displaying lists of model instances.

**Configuration:**

``list_display``
  Tuple of field names or callables to display as columns

``list_filter``
  Filter classes for queryset filtering

``list_actions``
  Actions available for each row (edit, delete, custom actions)

Example::

    from is_core.generic_views.table_views import DjangoTableView

    class ArticleTableView(DjangoTableView):
        model = Article
        list_display = ('title', 'author', 'published_at', 'status')
        list_filter = ('status', 'author', 'published_at')

        def get_list_filter(self, request):
            qs = super().get_list_filter(request)
            # Custom filtering logic
            if not request.user.is_superuser:
                qs = qs.filter(author=request.user)
            return qs

Form Views
----------

Generic form views for various use cases.

BulkChangeFormView
^^^^^^^^^^^^^^^^^^

Allows bulk editing of multiple objects at once.

**Use case:** Change status of multiple articles from "draft" to "published"

DjangoCoreFormView
^^^^^^^^^^^^^^^^^^

Base form view integrated with IS Core features.

DjangoBaseFormView
^^^^^^^^^^^^^^^^^^

Minimal form view without Core-specific features.

Inline Views
------------

Inline views allow editing related objects within a parent object's detail page.

**Example:** Edit article tags directly in the article detail view without navigating to a separate page.

Inline Form Views
^^^^^^^^^^^^^^^^^

Edit related objects using forms embedded in the parent object's page.

TabularInlineFormView
  Displays related objects in a table-like layout (one row per object)

StackedInlineFormView
  Displays each related object as a separate stacked form section

ResponsiveInlineFormView
  Automatically adjusts layout based on screen size

Example::

    from is_core.generic_views.inlines import TabularInlineFormView

    class ArticleTagInlineView(TabularInlineFormView):
        model = Tag
        fk_name = 'article'
        fields = ('name', 'color')
        can_delete = True

Inline Generic Views
^^^^^^^^^^^^^^^^^^^^

Similar to inline form views but work with generic relations.

TabularGenericInlineFormView
  Tabular layout for generic relations

StackedGenericInlineFormView
  Stacked layout for generic relations

ResponsiveGenericInlineFormView
  Responsive layout for generic relations

Inline Object Views
^^^^^^^^^^^^^^^^^^^

Read-only display of related objects.

TabularInlineObjectsView
  Read-only tabular display of related objects

ResponsiveInlineObjectsView
  Responsive read-only display of related objects

Inline Table Views
^^^^^^^^^^^^^^^^^^

DjangoInlineTableView
  Interactive table of related objects with AJAX loading

**Features:**

- Automatic filtering by parent object
- Full table functionality (sorting, pagination)
- Actions available for each row

Example::

    from is_core.generic_views.inlines import DjangoInlineTableView

    class ArticleCommentInlineTableView(DjangoInlineTableView):
        model = Comment
        fk_name = 'article'
        list_display = ('author', 'created_at', 'excerpt')

        def get_list_filter(self, request, parent_instance):
            # Automatically filtered to parent article
            return Comment.objects.filter(article=parent_instance)

View Configuration in Cores
----------------------------

Views are typically configured within Core classes::

    from is_core.main import UIRestCore

    class ArticleCore(UIRestCore):
        model = Article

        list_display = ('title', 'author', 'published_at')
        form_fields = ('title', 'content', 'author')

        # Customize detail view
        detail_view_class = ArticleDetailView

        # Add inline views
        inlines = (ArticleTagInlineView, ArticleCommentInlineTableView)

Common View Patterns
--------------------

Custom Column Rendering
^^^^^^^^^^^^^^^^^^^^^^^

Define methods in your Core to customize column display::

    class ArticleCore(UIRestCore):
        list_display = ('title', 'author_name', 'word_count')

        def author_name(self, obj):
            return obj.author.get_full_name()
        author_name.short_description = 'Author'

        def word_count(self, obj):
            return len(obj.content.split())
        word_count.short_description = 'Words'

Conditional Field Display
^^^^^^^^^^^^^^^^^^^^^^^^^^

Show/hide fields based on permissions or object state::

    class ArticleDetailView(DjangoDetailFormView):
        def get_fields(self, request, obj=None):
            fields = list(super().get_fields(request, obj))
            if not request.user.is_superuser:
                fields.remove('internal_notes')
            return fields

Custom Actions
^^^^^^^^^^^^^^

Add custom actions to table rows::

    class ArticleCore(UIRestCore):
        def get_list_actions(self, obj, request):
            actions = super().get_list_actions(obj, request)
            if obj.status == 'draft':
                actions.append({
                    'name': 'publish',
                    'verbose_name': 'Publish',
                    'url': self.get_api_url('publish', obj.pk),
                    'type': 'api'
                })
            return actions
