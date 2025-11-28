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
- Configurable columns via ``list_fields``

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

``list_fields``
  Tuple of field names or callables to display as columns

``list_filter``
  Filter classes for queryset filtering

``list_actions``
  Actions available for each row (edit, delete, custom actions)

Example::

    from is_core.generic_views.table_views import DjangoTableView

    class ArticleTableView(DjangoTableView):
        model = Article
        list_fields = ('title', 'author', 'published_at', 'status')
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

Allows bulk editing of multiple objects at once from a table view. Users can select multiple rows in a ``DjangoTableView`` and apply changes to all selected objects simultaneously.

**Use case:** Select multiple articles in a table view and change their status from "draft" to "published" in one operation.

.. note::
   Bulk change functionality is only available for **table views** (``DjangoTableView``). It appears as a button/action in the table interface when enabled.

**Configuration in Core:**

To enable bulk change functionality, you must configure it in your Core class:

``bulk_change_enabled``
  Set to ``True`` to enable bulk change functionality (default: ``False``)

``bulk_change_fields``
  Tuple of field names that can be bulk edited

Example::

    from is_core.main import DjangoUiRestCore

    class ArticleCore(DjangoUiRestCore):
        model = Article

        # Enable bulk change functionality
        bulk_change_enabled = True

        # Specify which fields can be bulk edited
        bulk_change_fields = ('status', 'category', 'author')

        list_fields = ('title', 'status', 'author', 'published_at')

You can also dynamically control bulk change fields by overriding ``get_bulk_change_fields``::

    class ArticleCore(DjangoUiRestCore):
        model = Article
        bulk_change_enabled = True

        def get_bulk_change_fields(self, request):
            fields = ['status', 'category']
            if request.user.is_superuser:
                fields.append('author')
            return fields

To disable bulk changes for a specific table view (even when enabled in Core)::

    class ArticleTableView(DjangoTableView):
        model = Article

        def is_bulk_change_enabled(self):
            return False

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
   **Use Case**: Inline views are suitable for parent-child relationships like Order → Order Items, Article → Tags, or Invoice → Line Items.

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
        list_fields = ('author', 'created_at', 'excerpt')

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
        list_fields = ('order_number', 'created_at', 'total', 'status')
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

        list_fields = ('title', 'author', 'published_at')
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
        list_fields = ('title', 'author_name', 'word_count')

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

Inline Views in Fieldsets
==========================

Django IS Core allows you to embed related object management directly within a detail form view using inline views in fieldsets. Unlike Django Admin's inline system, IS Core inline views are defined in the ``fieldsets`` configuration using the ``inline_view`` key.

Why Use Inline Views in Fieldsets?
-----------------------------------

Inline views in fieldsets allow you to:

- Display and edit related objects without leaving the parent object's detail page
- Mix regular fields with inline views in a single fieldset structure
- Use both table-based and form-based inline views
- Apply custom permissions and visibility logic to inline sections
- Create a seamless user experience for managing one-to-many and many-to-many relationships

Basic Inline View Configuration
--------------------------------

Inline views are added to fieldsets using the ``inline_view`` key in the fieldset dictionary:

.. code-block:: python
    :caption: cores/customer/views.py

    from typing import Any
    from django.utils.translation import gettext_lazy as _l
    from is_core.generic_views.detail_views import DjangoDetailFormView
    from is_core.generic_views.inlines import TabularInlineFormView

    class CustomerDetailView(DjangoDetailFormView):
        form_class = CustomerEditForm

        # Regular fieldsets with fields
        fieldsets = (
            (_l('Basic Information'), {
                'fields': ('first_name', 'last_name', 'email', 'phone'),
                'class': 'col-lg-6'
            }),
            (_l('Account Details'), {
                'fields': ('is_active', 'created_at', 'points'),
                'class': 'col-lg-6'
            }),
            # Inline view fieldsets
            (_l('E-mail addresses'), {
                'inline_view': CustomerEmailTabularInlineFormView
            }),
            (_l('Phone numbers'), {
                'inline_view': CustomerPhoneTabularInlineFormView
            }),
            (_l('Addresses'), {
                'inline_view': CustomerAddressInlineTableView
            }),
        )

Types of Inline Views
----------------------

**TabularInlineFormView - Editable Table:**

.. code-block:: python

    from is_core.generic_views.inlines import TabularInlineFormView

    class CustomerEmailTabularInlineFormView(TabularInlineFormView):
        model = CustomerEmail
        form_class = CustomerEmailForm
        fields = ('email', 'is_verified', 'primary')
        extra = 1
        can_delete = True

**DjangoInlineTableView - Read-Only Table:**

.. code-block:: python

    from is_core.generic_views.inlines import DjangoInlineTableView

    class CustomerAddressInlineTableView(DjangoInlineTableView):
        model = CustomerAddress
        list_display = ('type', 'street', 'city', 'zip_code', 'country')
        paginate_by = 10

**StackedInlineFormView - Stacked Forms:**

.. code-block:: python

    from is_core.generic_views.inlines import StackedInlineFormView

    class CustomerBlockingInlineFormView(StackedInlineFormView):
        model = CustomerBlocking
        form_class = CustomerBlockingForm
        fields = ('reason', 'activated_at', 'terminated_at')
        extra = 0
        can_delete = False

Dynamic Fieldsets with Inline Views
------------------------------------

You can generate fieldsets dynamically based on permissions or object state:

.. code-block:: python

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from django.http import HttpRequest


    class CustomerDetailView(DjangoDetailFormView):
        def get_fieldsets(
            self,
            request: HttpRequest | None = None,
            obj: Customer | None = None
        ) -> tuple[Any, ...]:
            fieldsets = [
                (_l('Basic Info'), {'fields': ('first_name', 'last_name')}),
                (_l('Addresses'), {'inline_view': CustomerAddressInlineTableView}),
            ]

            # Add bank accounts inline only if customer is verified
            if obj and obj.is_verified:
                fieldsets.append(
                    (_l('Bank accounts'), {'inline_view': CustomerBankAccountInlineTableView})
                )

            # Add admin-only inline views
            if request and request.user.has_perm('customers.view_blocking'):
                fieldsets.append(
                    (_l('Blocking History'), {'inline_view': CustomerBlockingInlineFormView})
                )

            return tuple(fieldsets)

Using fieldsets_postfix
------------------------

For views that extend other view classes, use ``fieldsets_postfix`` to append inline views without overriding the parent's fieldsets:

.. code-block:: python

    from user_comments.contrib.is_core.cores import CommentCoreMixin

    class CustomerDetailView(CommentCoreMixin, DjangoDetailFormView):
        # Standard fields configuration
        fields = ('first_name', 'last_name', 'email', 'phone')

        # Append inline views after parent fieldsets
        fieldsets_postfix = CommentCoreMixin.notes_fieldset + (
            (_l('Addresses'), {'inline_view': CustomerAddressInlineTableView}),
            (_l('Bank accounts'), {'inline_view': CustomerBankAccountInlineTableView}),
            (_l('E-mail addresses'), {'inline_view': CustomerEmailTabularInlineFormView}),
        )

This pattern is useful when:

- You're extending a mixin that provides its own fieldsets
- You want to add inline views without duplicating parent configuration
- You need to maintain a consistent order of fieldsets across multiple views

Inline Views for Nested Resources
----------------------------------

Inline views can display resources nested under the parent object:

.. code-block:: python

    class CustomerCommentTableView(DjangoDetailFormView):
        """Dedicated view for customer comments using only an inline view."""

        def get_fieldsets(self) -> tuple[Any, ...]:
            return (
                (_l('Comments'), {'inline_view': CustomerCommentInlineView}),
            )


    class CustomerCommentInlineView(DjangoInlineTableView):
        model = Comment
        list_display = ('author', 'created_at', 'content_type_link', 'comment')

        def get_queryset(self) -> QuerySet[Comment]:
            customer_pk = self.request.kwargs.get('customer_pk')
            # Filter comments related to this customer
            return Comment.objects.filter(
                content_type=ContentType.objects.get_for_model(Customer),
                object_pk=str(customer_pk)
            )

Combining Multiple Inline Types
--------------------------------

You can mix different inline view types in a single detail view:

.. code-block:: python

    class CustomerDetailView(DjangoDetailFormView):
        fieldsets = (
            # Regular fields
            (_l('Personal Information'), {
                'fields': ('first_name', 'last_name', 'birth_date'),
                'class': 'col-lg-6'
            }),

            # Editable inline form (TabularInlineFormView)
            (_l('E-mail addresses'), {
                'inline_view': CustomerEmailTabularInlineFormView
            }),

            # Read-only inline table (DjangoInlineTableView)
            (_l('Order History'), {
                'inline_view': CustomerOrdersInlineTableView
            }),

            # Stacked inline form (StackedInlineFormView)
            (_l('Blocking Details'), {
                'inline_view': CustomerBlockingInlineFormView
            }),
        )

Inline View Permissions
------------------------

Control inline view visibility using permissions:

.. code-block:: python

    class CustomerDocumentsInlineTableView(DjangoInlineTableView):
        model = Document

        def has_get_permission(self, **kwargs) -> bool:
            """Only show documents to users with view permission."""
            return self.request.user.has_perm('documents.view_document')


    class CustomerDetailView(DjangoDetailFormView):
        def get_fieldsets(self, request=None, obj=None):
            fieldsets = [
                (_l('Basic Info'), {'fields': ('first_name', 'last_name')}),
            ]

            # Conditionally add inline based on permission check
            inline_view_class = CustomerDocumentsInlineTableView
            # Check if the inline view's permission method would pass
            temp_view = inline_view_class()
            temp_view.request = request

            if temp_view.has_get_permission():
                fieldsets.append(
                    (_l('Documents'), {'inline_view': CustomerDocumentsInlineTableView})
                )

            return tuple(fieldsets)

Styling Inline Views
---------------------

Control the appearance of inline view sections using CSS classes:

.. code-block:: python

    class CustomerDetailView(DjangoDetailFormView):
        fieldsets = (
            # Full-width inline
            (_l('Addresses'), {
                'inline_view': CustomerAddressInlineTableView,
                'class': 'col-12'
            }),

            # Half-width inline (side-by-side with other fieldset)
            (_l('E-mails'), {
                'inline_view': CustomerEmailTabularInlineFormView,
                'class': 'col-lg-6'
            }),

            # Collapsible inline
            (_l('Advanced Settings'), {
                'inline_view': CustomerAdvancedSettingsInlineView,
                'classes': ('collapse',)  # Note: 'classes' not 'class'
            }),
        )

