Filters
=======

Filters allow users to narrow down data in table views. IS Core uses django-pyston filters to generate interactive list views where every column can have a filter input.

.. seealso::

   :ref:`views`
      Table views that use filters

   Django Pyston Documentation
      Full filter reference: https://github.com/druids/django-pyston

How Filters Work
----------------

When you define a Core with ``list_fields``, IS Core automatically creates filters for those fields. Users can type in filter inputs and the table updates automatically via AJAX.

Example::

    class ArticleCore(DjangoUiRestCore):
        model = Article
        list_fields = ('title', 'author', 'status', 'created_at')
        # Filters are automatically created for all fields

Filter Types
------------

Field Filters
^^^^^^^^^^^^^

Filters derived from model fields. The widget is determined automatically:

**Render as Select Box:**
  If the filter has a ``choices`` attribute set (e.g., CharField with choices, ForeignKey with limited options)

**Render as Text Input:**
  Otherwise, the filter widget is obtained from the model field using the ``formfield()`` method

Example::

    class Article(models.Model):
        STATUS_CHOICES = [
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ]
        status = models.CharField(max_length=20, choices=STATUS_CHOICES)
        # Filter renders as: <select> with 3 options

Custom Filters
--------------

UIFilterMixin
^^^^^^^^^^^^^

Django IS Core provides a special mixin for filters that adds the ability to customize the rendered widget.

**Use case:** Restrict ForeignKey choices based on permissions

Example::

    from is_core.filters import UIFilterMixin
    from pyston.filters.default_filters import ForeignKeyFilter

    class RestrictedAuthorFilter(UIFilterMixin, ForeignKeyFilter):

        def get_restricted_queryset(self, qs, request):
            # Only show authors from user's team
            if not request.user.is_superuser:
                return qs.filter(team=request.user.team)
            return qs

        def get_widget(self, request):
            formfield = self.field.formfield()
            formfield.queryset = self.get_restricted_queryset(
                formfield.queryset,
                request
            )
            return formfield.widget

Custom Filter Classes
^^^^^^^^^^^^^^^^^^^^^

Create completely custom filter logic::

    from pyston.filters import Filter

    class DateRangeFilter(Filter):
        def get_filter_term(self, value, operator_slug, request):
            # Parse date range like "2024-01-01:2024-12-31"
            start, end = value.split(':')
            return {
                f'{self.field_name}__gte': start,
                f'{self.field_name}__lte': end,
            }

    class ArticleCore(DjangoUiRestCore):
        model = Article

        def get_list_filter(self, request):
            from pyston.filters import FilterManager

            manager = super().get_list_filter(request)
            manager.add_filter('created_at', DateRangeFilter)
            return manager

**Example: Complex Q() Filters**

Create filters that query across multiple tables using Django's Q objects::

    from django.db.models import Q
    from pyston.filters import Filter

    class AppliedPromocodeIDFilter(Filter):
        """Filter customers by applied promocode ID"""

        def get_q(self, value, operator_slug, request):
            # Search across multiple related tables
            return Q(
                # Direct promocode usage
                customerpromocode__promocode_id__icontains=value
            ) | Q(
                # Promocode via orders
                order__customerpromocode__promocode_id__icontains=value
            ) | Q(
                # Promocode via subscriptions
                subscription__promocode_id__icontains=value
            )

    class CustomerCore(DjangoUiRestCore):
        model = Customer

        def get_list_filter(self, request):
            manager = super().get_list_filter(request)
            manager.add_filter('applied_promocode_id', AppliedPromocodeIDFilter)
            return manager

Common Filter Patterns
----------------------

Disable Filters
^^^^^^^^^^^^^^^

Disable filtering for specific columns::

    class ArticleCore(DjangoUiRestCore):
        list_fields = ('title', 'author', 'content_preview')

        def content_preview(self, obj):
            return obj.content[:100]
        content_preview.filter = False  # Disable filter

Default Filter Values
^^^^^^^^^^^^^^^^^^^^^

Set default filters to pre-filter the list::

    class ArticleCore(DjangoUiRestCore):
        model = Article
        default_list_filter = {
            'filter': {
                'status': 'published'  # Show only published by default
            }
        }

Filter by Related Fields
^^^^^^^^^^^^^^^^^^^^^^^^

Filter by fields in related models::

    class ArticleCore(DjangoUiRestCore):
        model = Article
        list_fields = ('title', 'author__email', 'author__team')
        # Filters automatically work for related fields

Case-Insensitive Search
^^^^^^^^^^^^^^^^^^^^^^^

Use ``icontains`` for case-insensitive text search::

    from pyston.filters import SimpleFilter

    class ArticleCore(DjangoUiRestCore):
        def get_list_filter(self, request):
            manager = super().get_list_filter(request)
            manager.add_filter(
                'title',
                SimpleFilter,
                allowed_operators=['icontains']
            )
            return manager

Filter Operators
----------------

Available filter operators:

+------------------+-------------------------+---------------------------+
| **Operator**     | **Django Lookup**       | **Example**               |
+==================+=========================+===========================+
| exact            | ``field=value``         | status=published          |
+------------------+-------------------------+---------------------------+
| iexact           | ``field__iexact``       | Case-insensitive exact    |
+------------------+-------------------------+---------------------------+
| contains         | ``field__contains``     | title contains "django"   |
+------------------+-------------------------+---------------------------+
| icontains        | ``field__icontains``    | Case-insensitive contains |
+------------------+-------------------------+---------------------------+
| gt               | ``field__gt``           | created_at > 2024-01-01   |
+------------------+-------------------------+---------------------------+
| gte              | ``field__gte``          | age >= 18                 |
+------------------+-------------------------+---------------------------+
| lt               | ``field__lt``           | price < 100               |
+------------------+-------------------------+---------------------------+
| lte              | ``field__lte``          | stock <= 10               |
+------------------+-------------------------+---------------------------+

.. note::
   Add database indexes on commonly filtered fields for better performance.

Enum-Based Filters
==================

Django IS Core integrates with `django-enumfields <https://github.com/hzdg/django-enumfields>`_, allowing you to create type-safe filters using Python enums. This pattern uses ``ChoicesEnum`` from enumfields to provide structured choices in filters.

When to Use Enum-Based Filters
-------------------------------

Enum-based filters are useful when:

- You need type-safe filter values checked at runtime and by type checkers
- Filter choices are defined centrally to reduce duplication
- You're filtering by ContentType for generic foreign keys
- You want IDE autocomplete and refactoring support

Basic Enum Filter
-----------------

Create an enum and a corresponding filter:

.. code-block:: python

    from typing import TYPE_CHECKING
    from django.db.models import Q
    from django.utils.translation import gettext_lazy as _l
    from enumfields import Choice
    from enumfields.enums import ChoicesEnum
    from pyston.filters.utils import OperatorSlug

    if TYPE_CHECKING:
        from django.core.handlers.wsgi import WSGIRequest

    # Define the enum
    class CustomerCommentContentTypeEnum(ChoicesEnum):
        ORDER = Choice('Order', _l('Order'))
        CUSTOMER = Choice('Customer', _l('Customer'))
        BILLING = Choice('Billing', _l('Billing'))
        APPLICATION = Choice('Application', _l('Application'))

    # Create the filter
    from utils.models.filters import ChoicesEnumFilter

    class CustomerCommentContentTypeFilter(ChoicesEnumFilter):
        choice_enum = CustomerCommentContentTypeEnum
        allowed_operators = (OperatorSlug.EQ,)

        def get_filter_term(
            self,
            value: CustomerCommentContentTypeEnum,
            operator_slug: str,
            request: WSGIRequest
        ) -> Q:
            # Filter by the enum value
            return Q(type=value.value)

ContentType-Based Enum Filter
------------------------------

A common pattern is filtering generic foreign keys by ContentType using enums:

.. code-block:: python

    from django.contrib.contenttypes.models import ContentType
    from common.apps.customers.models import Customer
    from common.apps.commerce.models import Order, Application

    class CommentableTypeEnum(ChoicesEnum):
        """Enum for objects that can have comments."""
        CUSTOMER = Choice(Customer, _l('Customer'))
        ORDER = Choice(Order, _l('Order'))
        APPLICATION = Choice(Application, _l('Application'))


    class CommentContentTypeFilter(ChoicesEnumFilter):
        choice_enum = CommentableTypeEnum
        allowed_operators = (OperatorSlug.EQ,)

        def get_filter_term(
            self,
            value: CommentableTypeEnum,
            operator_slug: str,
            request: WSGIRequest
        ) -> Q:
            # Get ContentType for the model class
            model_ct = ContentType.objects.get_for_model(value.value)
            return Q(content_type=model_ct)

Using Enum Filters in Cores
----------------------------

Apply enum filters to resource fields using the ``@filter_class`` decorator:

.. code-block:: python

    from is_core.main import DjangoUiRestCore
    from is_core.utils.decorators import short_description
    from pyston.utils.decorators import filter_class

    class CustomerCommentCore(DjangoUiRestCore):
        model = Comment

        list_fields = ('author', 'created_at', 'content_type_link', 'comment')

        @short_description(_l('object'))
        @filter_class(CommentContentTypeFilter)
        def content_type_link(self, obj: Comment, request):
            return render_model_object_with_link(request, obj.content_object)

Complex Enum with Multiple Models
----------------------------------

For sophisticated filtering across multiple related models:

.. code-block:: python

    from common.apps.installments.models import InstallmentContract, InstallmentApplication
    from common.apps.revolving_loan.models import RevolvingLoanContract, RevolvingLoanApplication

    class FinancialProductTypeEnum(ChoicesEnum):
        """Enum for all financial product types."""
        INSTALLMENT_CONTRACT = Choice(InstallmentContract, _l('Installment contract'))
        INSTALLMENT_APPLICATION = Choice(InstallmentApplication, _l('Installment application'))
        REVOLVING_CONTRACT = Choice(RevolvingLoanContract, _l('Revolving loan contract'))
        REVOLVING_APPLICATION = Choice(RevolvingLoanApplication, _l('Revolving loan application'))


    class FinancialProductTypeFilter(ChoicesEnumFilter):
        choice_enum = FinancialProductTypeEnum
        allowed_operators = (OperatorSlug.EQ,)

        def get_filter_term(
            self,
            value: FinancialProductTypeEnum,
            operator_slug: str,
            request: WSGIRequest
        ) -> Q:
            model_ct = ContentType.objects.get_for_model(value.value)
            return Q(content_type=model_ct)

.. note::
   The ``choice_enum`` attribute automatically generates the ``choices`` list. Only define ``choices`` explicitly when you want to restrict the filter to a subset of enum values.

JSON Field and Array Filters
=============================

PostgreSQL-specific fields like ``JSONField`` and ``ArrayField`` require specialized filtering approaches. Django IS Core supports these through custom filter implementations.

PostgreSQL Array Filtering
---------------------------

Filter by values contained in PostgreSQL array fields:

.. code-block:: python

    from django.db.models import Q
    from pyston.filters.django_filters import SimpleFilter
    from pyston.filters.utils import OperatorSlug

    class CustomerEnabledFeaturesFilter(SimpleFilter):
        """Filter customers by enabled features stored in an ArrayField."""

        allowed_operators = (OperatorSlug.EQ,)

        def get_filter_term(
            self,
            value: int,
            operator_slug: str,
            request: WSGIRequest
        ) -> Q:
            # PostgreSQL array contains operator
            return Q(enabled_features__contains=[value])

Using Array Filters in Cores
-----------------------------

Apply array filters to fields that store lists:

.. code-block:: python

    from is_core.main import DjangoUiRestCore
    from pyston.utils.decorators import filter_class

    class CustomerCore(DjangoUiRestCore):
        model = Customer

        list_fields = ('id', 'full_name', 'email', 'enabled_features')

        rest_extra_fields = ('enabled_features',)
        rest_extra_filter_fields = ('enabled_features',)

        @filter_class(CustomerEnabledFeaturesFilter)
        @property
        def enabled_features(self):
            """Expose enabled_features for filtering."""
            return None

This allows filtering like: ``GET /api/customers/?enabled_features=5``

JSON Field Filtering
--------------------

Filter by keys or values within JSON fields:

.. code-block:: python

    class JSONSettingsFilter(SimpleFilter):
        """Filter by JSON field content."""

        allowed_operators = (OperatorSlug.EQ, OperatorSlug.CONTAINS)

        def get_filter_term(self, value: str, operator_slug: str, request) -> Q:
            if operator_slug == OperatorSlug.EQ:
                # Exact JSON key-value match
                return Q(settings__theme=value)
            elif operator_slug == OperatorSlug.CONTAINS:
                # JSON field contains key
                return Q(settings__has_key=value)
            return Q()

Array Overlap Filtering
-----------------------

Check if arrays have any common elements:

.. code-block:: python

    class TagsOverlapFilter(SimpleFilter):
        """Filter objects with overlapping tags."""

        allowed_operators = (OperatorSlug.EQ,)

        def get_filter_term(self, value: str, operator_slug: str, request) -> Q:
            # Split comma-separated tags
            tags = [tag.strip() for tag in value.split(',')]
            # PostgreSQL && operator (overlap)
            return Q(tags__overlap=tags)

Usage: ``GET /api/articles/?tags=python,django`` finds articles tagged with python OR django.

Array Length Filtering
----------------------

Filter by array length:

.. code-block:: python

    from django.contrib.postgres.fields.array import ArrayField
    from django.db.models import Q
    from django.db.models.functions import Coalesce, JSONBArrayLength

    class ArrayLengthFilter(SimpleFilter):
        """Filter by number of items in array."""

        allowed_operators = (OperatorSlug.GT, OperatorSlug.LT, OperatorSlug.EQ)

        def get_filter_term(self, value: int, operator_slug: str, request) -> Q:
            # Use annotated queryset
            lookup = f'tags__len__{operator_slug}'
            return Q(**{lookup: value})

Multiple Array Values
---------------------

Filter where array contains ALL specified values:

.. code-block:: python

    class ArrayContainsAllFilter(SimpleFilter):
        """Filter arrays containing all specified values."""

        allowed_operators = (OperatorSlug.EQ,)

        def get_filter_term(self, value: str, operator_slug: str, request) -> Q:
            values = [int(v.strip()) for v in value.split(',')]
            # PostgreSQL @> operator (contains)
            return Q(feature_ids__contains=values)

Usage: ``GET /api/customers/?feature_ids=1,2,3`` finds customers with features 1 AND 2 AND 3.

.. note::
   PostgreSQL-specific filters require GIN indexes on JSON/Array fields for optimal performance. Add indexes using ``opclasses=['gin_integer_ops']`` or similar for the field type.
