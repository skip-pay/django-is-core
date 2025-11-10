.. _views:

Views
=====

Django IS Core provides a comprehensive set of generic views for building admin interfaces. Views handle the UI presentation layer and can work in two modes:

1. **Server-side rendered**: Traditional Django template rendering
2. **AJAX-powered**: HTML structure with data loaded via REST endpoints

.. seealso::

   :ref:`rests`
      REST Resources that power the AJAX views

   :ref:`forms`
      Form classes and widgets used in views

   :ref:`permissions`
      Controlling access to views

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

.. note::
   **Use Case**: Inline views are perfect for parent-child relationships like Order → Order Items, Article → Tags, or Invoice → Line Items.

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

**Example: Complex Inline Configuration**

Use multiple inline views with different configurations::

    from is_core.generic_views.inlines import (
        TabularInlineFormView,
        DjangoInlineTableView,
        ResponsiveInlineObjectsView
    )

    class CustomerAddressInlineView(TabularInlineFormView):
        """Edit customer addresses inline"""
        model = Address
        fk_name = 'customer'
        fields = ('street', 'city', 'postal_code', 'country', 'is_billing')
        can_delete = True
        max_num = 5
        extra = 1  # One empty form for new address

    class CustomerOrdersInlineTableView(DjangoInlineTableView):
        """Table of customer orders with full AJAX functionality"""
        model = Order
        fk_name = 'customer'
        list_display = ('order_number', 'created_at', 'total', 'status')
        list_actions = ('view', 'cancel')

        def get_list_filter(self, request, parent_instance):
            return Order.objects.filter(customer=parent_instance)

    class CustomerNotesInlineView(ResponsiveInlineObjectsView):
        """Read-only display of customer notes"""
        model = Note
        fk_name = 'customer'
        fields = ('created_at', 'author', 'content')

    class CustomerCore(DjangoUiRestCore):
        model = Customer

        inlines = (
            CustomerAddressInlineView,      # Editable addresses
            CustomerOrdersInlineTableView,  # Interactive orders table
            CustomerNotesInlineView,        # Read-only notes
        )

Tabs System
^^^^^^^^^^^

Use tabs to organize complex detail views::

    class CustomerTabsViewMixin:
        """Mixin adding tabs to customer detail view"""

        def get_tabs(self, request, obj):
            tabs = [
                {
                    'name': 'detail',
                    'title': _('Customer Details'),
                    'url': self.core.get_ui_url('change', pk=obj.pk),
                },
                {
                    'name': 'orders',
                    'title': _('Orders'),
                    'url': self.core.get_ui_url('orders', customer_pk=obj.pk),
                    'badge': obj.orders.count(),
                },
                {
                    'name': 'invoices',
                    'title': _('Invoices'),
                    'url': self.core.get_ui_url('invoices', customer_pk=obj.pk),
                },
                {
                    'name': 'payments',
                    'title': _('Payment Methods'),
                    'url': self.core.get_ui_url('payments', customer_pk=obj.pk),
                },
            ]

            # Conditional tabs based on permissions
            if request.user.has_perm('customers.view_audit_log'):
                tabs.append({
                    'name': 'audit',
                    'title': _('Audit Log'),
                    'url': self.core.get_ui_url('audit', customer_pk=obj.pk),
                })

            # Conditional tabs based on object state
            if obj.has_subscription:
                tabs.append({
                    'name': 'subscription',
                    'title': _('Subscription'),
                    'url': self.core.get_ui_url('subscription', customer_pk=obj.pk),
                    'badge': 'Active' if obj.subscription.is_active else 'Inactive',
                })

            return tabs

    class CustomerDetailView(CustomerTabsViewMixin, DjangoDetailFormView):
        model = Customer
        form_class = CustomerForm

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

Field-Level Permissions
^^^^^^^^^^^^^^^^^^^^^^^^

Control access to individual fields based on user permissions::

    from is_core.auth.permissions import FieldsSetPermission

    class CustomerDetailView(DjangoDetailFormView):
        model = Customer
        form_class = CustomerForm

        def get_permission_obj_or_none(self, request, obj):
            # Set field permissions based on user role
            if request.user.has_perm('customers.view_sensitive_data'):
                # Full access to all fields
                return obj
            else:
                # Restricted access - hide sensitive fields
                return FieldsSetPermission(
                    obj=obj,
                    read_only_fields=(
                        'ssn',           # Social security number
                        'tax_id',        # Tax identification
                        'credit_score',  # Financial data
                    )
                )

        def get_readonly_fields(self, request, obj=None):
            readonly = list(super().get_readonly_fields(request, obj))

            # Make fields read-only based on object state
            if obj and obj.is_anonymized:
                readonly.extend([
                    'email',
                    'phone_number',
                    'billing_address',
                ])

            return readonly

**Read-Only Guard Mixin**

Protect archived or anonymized data from modification::

    class CustomerReadonlyGuardMixin:
        """Prevent editing of archived/anonymized customers"""

        def get_readonly_fields(self, request, obj=None):
            readonly = list(super().get_readonly_fields(request, obj))

            if obj and (obj.is_anonymized or obj.is_archived):
                # Make all fields read-only
                readonly = list(self.get_fields(request, obj))

            return readonly

        def has_update_permission(self, request, obj=None):
            if obj and (obj.is_anonymized or obj.is_archived):
                return False
            return super().has_update_permission(request, obj)

    class CustomerDetailView(CustomerReadonlyGuardMixin, DjangoDetailFormView):
        model = Customer
        form_class = CustomerForm

Dynamic Fieldsets
^^^^^^^^^^^^^^^^^

Adjust form organization based on object state::

    class CustomerDetailView(DjangoDetailFormView):
        model = Customer

        def get_fieldsets(self, request, obj=None):
            # Basic fieldset for all customers
            fieldsets = [
                ('Basic Information', {
                    'fields': ('email', 'first_name', 'last_name', 'phone')
                }),
            ]

            # Add billing fieldset only for active customers
            if obj and obj.is_active:
                fieldsets.append(
                    ('Billing', {
                        'fields': ('billing_address', 'payment_method')
                    })
                )

            # Add subscription fieldset if customer has subscription
            if obj and obj.has_subscription:
                fieldsets.append(
                    ('Subscription', {
                        'fields': ('subscription_plan', 'subscription_status', 'renewal_date')
                    })
                )

            # Add admin-only fieldset for superusers
            if request.user.is_superuser:
                fieldsets.append(
                    ('Admin', {
                        'fields': ('is_test_account', 'internal_notes'),
                        'classes': ('collapse',)
                    })
                )

            return fieldsets
