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

Method/Resource Filters
^^^^^^^^^^^^^^^^^^^^^^^

Filters for calculated fields or methods.

The same rule applies as for field filters, but if ``choices`` is not defined, a simple text input is returned.

Example::

    class ArticleCore(DjangoUiRestCore):
        model = Article
        list_fields = ('title', 'word_count')

        def word_count(self, obj):
            return len(obj.content.split())
        word_count.filter = True  # Enable filtering
        word_count.filter_by = 'content'  # Filter by content field

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

**Example: Enum-based Filters**

Filter by choices from Python Enums::

    from pyston.filters import SimpleFilter

    class ChoicesEnumFilter(SimpleFilter):
        """Filter with choices from an Enum"""

        def __init__(self, enum_class, **kwargs):
            self.enum_class = enum_class
            super().__init__(**kwargs)

        def get_filter_term(self, value, operator_slug, request):
            # Convert enum value to database value
            if hasattr(self.enum_class, value):
                db_value = getattr(self.enum_class, value).value
                return {f'{self.field_name}__exact': db_value}
            return {}

        def get_choices(self):
            # Generate choices from enum
            return [(e.name, e.value) for e in self.enum_class]

    # Usage with ContentType filtering
    from django.contrib.contenttypes.models import ContentType

    class PaymentMethodFilter(ChoicesEnumFilter):
        def get_filter_term(self, value, operator_slug, request):
            # Filter by ContentType for polymorphic relationships
            content_types = ContentType.objects.filter(
                model__in=['creditcard', 'banktransfer', 'paypal']
            )
            return {
                f'{self.field_name}__in': content_types
            }

    class OrderCore(DjangoUiRestCore):
        model = Order

        def get_list_filter(self, request):
            manager = super().get_list_filter(request)
            manager.add_filter(
                'payment_method_type',
                PaymentMethodFilter,
                enum_class=PaymentMethodEnum
            )
            return manager

**Example: JSON Field Filters**

Filter by values within JSON fields::

    from pyston.filters import Filter

    class JSONFieldFilter(Filter):
        """Filter customers by features enabled in JSON field"""

        def get_q(self, value, operator_slug, request):
            # Filter by JSON array contains
            return Q(**{
                f'{self.field_name}__contains': [value]
            })

    class CustomerCore(DjangoUiRestCore):
        model = Customer

        def get_list_filter(self, request):
            manager = super().get_list_filter(request)
            # Filter by enabled features in JSON field
            manager.add_filter('enabled_features', JSONFieldFilter)
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

Best Practices
--------------

.. tip::
   **Performance Tip**: Filters generate database queries. Add database indexes on commonly filtered fields.

1. **Keep filters simple** - Users should understand what each filter does
2. **Limit ForeignKey choices** - Use UIFilterMixin to prevent huge dropdowns
3. **Set sensible defaults** - Use ``default_list_filter`` for common cases
4. **Test performance** - Complex filters can slow down queries
5. **Add help text** - Use field ``help_text`` to explain filter behavior

.. warning::
   Filtering on non-indexed fields with large datasets can cause slow queries. Always add indexes for filtered fields.
