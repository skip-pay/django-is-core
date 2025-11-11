.. _rests:

REST Resources
==============

Django IS Core provides a REST API system built on top of django-pyston. Resources define REST endpoints that serve as the backend for UI actions and can be used independently to build custom frontends.

.. seealso::

   :ref:`views`
      UI views that consume these REST endpoints

   :ref:`forms`
      Forms used for validation in resources

   :ref:`permissions`
      Securing your REST endpoints

Overview
--------

REST resources in IS Core:

- Provide CRUD operations over models
- Handle data serialization and deserialization
- Support filtering, sorting, and pagination
- Validate input data
- Define actions available for objects
- Can be used independently without UI

Resource Types
--------------

BaseResource
^^^^^^^^^^^^

The most basic resource class for creating custom REST endpoints.

**Use case:** Custom endpoints that don't follow the standard CRUD pattern

Example::

    from is_core.rest.resource import BaseResource
    from is_core.rest.decorators import rest_method

    class StatsResource(BaseResource):
        @rest_method('GET')
        def get(self, request):
            return {
                'total_articles': Article.objects.count(),
                'published': Article.objects.filter(status='published').count(),
                'drafts': Article.objects.filter(status='draft').count()
            }

        @classmethod
        def get_rest_patterns(cls):
            return patterns(
                url(r'^stats/$', cls.as_view(), name='stats'),
            )

DjangoCoreResource
^^^^^^^^^^^^^^^^^^

Internal "model resource" providing ready-made CRUD operations over Django models.

**Features:**

- Automatic CRUD endpoints (list, detail, create, update, delete)
- Built-in pagination
- Filtering and sorting support
- Field serialization
- Validation through forms
- Permission checking

**Configuration:**

``model``
  The Django model this resource operates on

``form_class``
  Form class used for validation

``serializer``
  Custom serializer for controlling output format

``filters``
  Filtering options for list endpoint

Example::

    from is_core.rest.resource import DjangoCoreResource
    from .models import Article
    from .forms import ArticleForm

    class ArticleResource(DjangoCoreResource):
        model = Article
        form_class = ArticleForm
        filters = ('status', 'author', 'created_at')

        allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

        def get_queryset(self, request):
            qs = super().get_queryset(request)
            if not request.user.is_superuser:
                qs = qs.filter(author=request.user)
            return qs

Generic Resource
^^^^^^^^^^^^^^^^

A custom endpoint where you implement HTTP methods and register via ``get_rest_patterns``.

**Use case:** Specialized endpoints with custom logic

Example::

    from is_core.rest.resource import BaseResource

    class ArticlePublishResource(BaseResource):
        def post(self, request, pk):
            article = get_object_or_404(Article, pk=pk)

            if not request.user.has_perm('articles.publish_article'):
                return self.error_response(
                    'Permission denied',
                    status=403
                )

            article.status = 'published'
            article.published_at = timezone.now()
            article.save()

            return {'status': 'success', 'article_id': article.pk}

        @classmethod
        def get_rest_patterns(cls):
            return patterns(
                url(r'^article/(?P<pk>\d+)/publish/$',
                    cls.as_view(),
                    name='article-publish'),
            )

REST Endpoints
--------------

Standard CRUD Endpoints
^^^^^^^^^^^^^^^^^^^^^^^

DjangoCoreResource automatically provides these endpoints:

**List: GET /api/articles/**
  Returns paginated list of objects

  Query parameters:
  - ``offset``: Pagination offset
  - ``limit``: Number of results (default from ``IS_CORE_LIST_PER_PAGE``)
  - ``order_by``: Sort field (prefix with ``-`` for descending)
  - Filter parameters based on ``filters`` configuration

  Response::

      {
          "results": [
              {
                  "id": 1,
                  "title": "First Article",
                  "author": "John Doe",
                  "status": "published"
              },
              ...
          ],
          "total": 42,
          "offset": 0,
          "limit": 20
      }

**Detail: GET /api/articles/{id}/**
  Returns single object details

  Response::

      {
          "id": 1,
          "title": "First Article",
          "content": "Article content...",
          "author": {
              "id": 5,
              "name": "John Doe"
          },
          "status": "published",
          "created_at": "2024-01-15T10:30:00Z"
      }

**Create: POST /api/articles/**
  Creates new object

  Request body::

      {
          "title": "New Article",
          "content": "Content here...",
          "author": 5,
          "status": "draft"
      }

  Response: Created object data with ``201 Created`` status

**Update: PUT /api/articles/{id}/**
  Updates existing object

  Request body: Full object data

  Response: Updated object data

**Partial Update: PATCH /api/articles/{id}/**
  Partially updates object

  Request body: Only fields to update

**Delete: DELETE /api/articles/{id}/**
  Deletes object

  Response: ``204 No Content``

Actions System
--------------

Actions define operations available for objects in table views. They appear as buttons or menu items in the UI.

get_list_actions
^^^^^^^^^^^^^^^^

Method that returns a list of actions for each object in a table.

**Action Types:**

``ui``
  UI-only action (e.g., redirect to detail page) - no backend call

``api``
  API action that calls a REST endpoint - JS handles the call and UI updates

Example::

    class ArticleCore(UIRestCore):
        model = Article

        def get_list_actions(self, obj, request):
            actions = []

            # Always show view action
            actions.append({
                'name': 'view',
                'verbose_name': 'View',
                'url': self.get_detail_url(obj),
                'type': 'ui',
                'class': 'btn-primary'
            })

            # Edit action - requires permission
            if request.user.has_perm('articles.change_article'):
                actions.append({
                    'name': 'edit',
                    'verbose_name': 'Edit',
                    'url': self.get_edit_url(obj),
                    'type': 'ui',
                    'icon': 'edit'
                })

            # Publish action - API call, only for drafts
            if obj.status == 'draft' and request.user.has_perm('articles.publish_article'):
                actions.append({
                    'name': 'publish',
                    'verbose_name': 'Publish',
                    'url': self.get_api_url('publish', obj.pk),
                    'type': 'api',
                    'icon': 'check',
                    'confirm': 'Are you sure you want to publish this article?'
                })

            # Delete action - API call
            if request.user.has_perm('articles.delete_article'):
                actions.append({
                    'name': 'delete',
                    'verbose_name': 'Delete',
                    'url': self.get_api_url('delete', obj.pk),
                    'type': 'api',
                    'icon': 'trash',
                    'confirm': 'Are you sure you want to delete this article?',
                    'class': 'btn-danger'
                })

            return actions

Action Properties
^^^^^^^^^^^^^^^^^

``name``
  Unique identifier for the action

``verbose_name``
  Display name shown to user

``url``
  Target URL for the action

``type``
  Either ``'ui'`` (redirect) or ``'api'`` (REST call)

``icon`` (optional)
  Icon class or name

``class`` (optional)
  CSS classes for button styling

``confirm`` (optional)
  Confirmation message before executing action

``method`` (optional)
  HTTP method for API actions (default: ``'POST'``)

Bulk Actions
^^^^^^^^^^^^

Actions that operate on multiple selected objects.

Example::

    class ArticleCore(UIRestCore):
        model = Article

        def get_bulk_actions(self, request):
            actions = []

            if request.user.has_perm('articles.change_article'):
                actions.append({
                    'name': 'bulk_publish',
                    'verbose_name': 'Publish Selected',
                    'url': self.get_api_url('bulk-publish'),
                    'confirm': 'Publish {count} articles?'
                })

            return actions

        @rest_resource_method('POST', url='bulk-publish')
        def bulk_publish(self, request):
            ids = request.data.get('ids', [])
            updated = Article.objects.filter(
                id__in=ids,
                status='draft'
            ).update(
                status='published',
                published_at=timezone.now()
            )
            return {'updated': updated}

Serialization
-------------

Control how objects are serialized to JSON.

Custom Serializer
^^^^^^^^^^^^^^^^^

Define custom serialization logic::

    from is_core.rest.serializers import Serializer

    class ArticleSerializer(Serializer):
        def serialize(self, article, request, fields=None):
            data = {
                'id': article.pk,
                'title': article.title,
                'excerpt': article.content[:200],
                'author': {
                    'id': article.author.pk,
                    'name': article.author.get_full_name(),
                    'avatar': article.author.avatar.url if article.author.avatar else None
                },
                'url': article.get_absolute_url(),
                'published': article.status == 'published'
            }

            # Include full content only for detail view
            if fields and 'content' in fields:
                data['content'] = article.content

            return data

    class ArticleResource(DjangoCoreResource):
        model = Article
        serializer = ArticleSerializer()

Field Selection
^^^^^^^^^^^^^^^

Control which fields are included::

    class ArticleResource(DjangoCoreResource):
        model = Article

        # Fields for list endpoint
        list_fields = ('id', 'title', 'author', 'status', 'created_at')

        # Fields for detail endpoint
        detail_fields = ('id', 'title', 'content', 'author', 'status',
                        'created_at', 'updated_at', 'published_at')

Filtering and Sorting
----------------------

Filter Configuration
^^^^^^^^^^^^^^^^^^^^

Define filtering options::

    class ArticleResource(DjangoCoreResource):
        model = Article
        filters = {
            'status': ('exact',),
            'author': ('exact',),
            'created_at': ('gte', 'lte'),
            'title': ('icontains',)
        }

Usage::

    GET /api/articles/?status=published&author=5&created_at__gte=2024-01-01

Custom Filters
^^^^^^^^^^^^^^

Implement custom filtering logic::

    class ArticleResource(DjangoCoreResource):
        model = Article

        def get_queryset(self, request):
            qs = super().get_queryset(request)

            # Custom filter: my articles
            if request.GET.get('mine'):
                qs = qs.filter(author=request.user)

            # Custom filter: recent (last 7 days)
            if request.GET.get('recent'):
                week_ago = timezone.now() - timedelta(days=7)
                qs = qs.filter(created_at__gte=week_ago)

            return qs

Sorting
^^^^^^^

Default sorting::

    class ArticleResource(DjangoCoreResource):
        model = Article
        ordering = ('-created_at', 'title')

User-controlled sorting::

    GET /api/articles/?order_by=-published_at
    GET /api/articles/?order_by=title

Pagination
----------

Configuration
^^^^^^^^^^^^^

Control pagination behavior::

    # settings.py
    IS_CORE_LIST_PER_PAGE = 20
    IS_CORE_REST_PAGINATOR_MAX_TOTAL = 10000

Custom Pagination::

    class ArticleResource(DjangoCoreResource):
        model = Article
        paginator_class = CustomPaginator
        default_limit = 50
        max_limit = 200

Usage::

    GET /api/articles/?limit=50&offset=100

Validation
----------

Resources use Django forms for validation.

Form-based Validation
^^^^^^^^^^^^^^^^^^^^^

::

    class ArticleForm(SmartModelForm):
        class Meta:
            model = Article
            fields = ('title', 'content', 'author', 'status')

        def clean_title(self):
            title = self.cleaned_data['title']
            if len(title) < 10:
                raise ValidationError('Title must be at least 10 characters')
            return title

    class ArticleResource(DjangoCoreResource):
        model = Article
        form_class = ArticleForm

Error Response::

    POST /api/articles/
    {
        "title": "Short"
    }

    Response: 400 Bad Request
    {
        "errors": {
            "title": ["Title must be at least 10 characters"],
            "content": ["This field is required"]
        }
    }

Permissions
-----------

Resource-level Permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^

Control access to the entire resource::

    class ArticleResource(DjangoCoreResource):
        model = Article

        def has_permission(self, request, obj=None):
            if request.method == 'GET':
                return True
            return request.user.has_perm('articles.change_article')

Object-level Permissions
^^^^^^^^^^^^^^^^^^^^^^^^

Control access to specific objects::

    class ArticleResource(DjangoCoreResource):
        model = Article

        def has_object_permission(self, request, obj):
            if request.method == 'GET':
                return True
            # Only author or superuser can modify
            return obj.author == request.user or request.user.is_superuser

Method-level Permissions
^^^^^^^^^^^^^^^^^^^^^^^^

Control specific operations::

    class ArticleResource(DjangoCoreResource):
        model = Article

        def has_delete_permission(self, request, obj):
            # Only superuser can delete
            return request.user.is_superuser

        def has_create_permission(self, request):
            # Check if user has reached article limit
            user_articles = Article.objects.filter(author=request.user).count()
            return user_articles < 100

Standalone REST API
-------------------

.. tip::
   **Building a React/Vue frontend?** Use ``DjangoRestCore`` to get a REST API without the built-in UI.

Resources can be used independently without the IS Core UI to build custom frontends.

REST-only Core
^^^^^^^^^^^^^^

Create a REST-only core::

    from is_core.main import RESTCore

    class ArticleAPICore(RESTCore):
        model = Article
        resource_class = ArticleResource

This exposes only REST endpoints without any UI views.

Custom Frontend Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the REST API with React, Vue, or any other frontend::

    // JavaScript example
    async function fetchArticles() {
        const response = await fetch('/api/articles/?limit=20&offset=0');
        const data = await response.json();
        return data.results;
    }

    async function createArticle(articleData) {
        const response = await fetch('/api/articles/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(articleData)
        });
        return response.json();
    }

Background Tasks with Celery
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use Celery integration for long-running operations::

    from is_core.rest.resource import CeleryDjangoCoreResource

    class CustomerResource(CeleryDjangoCoreResource):
        """Resource with background task support"""
        model = Customer

        @short_description(_('Total Orders'))
        def total_orders(self, obj):
            """Computed field - available as extra field"""
            return obj.orders.count()

        @short_description(_('Lifetime Value'))
        def lifetime_value(self, obj):
            """Expensive aggregation - computed on demand"""
            from django.db.models import Sum
            return obj.orders.aggregate(
                total=Sum('amount')
            )['total'] or 0

        def _create_task(self, request, data):
            """Called when object creation is queued as background task"""
            from .tasks import create_customer_task
            return create_customer_task.delay(data)

    # tasks.py
    from celery import shared_task

    @shared_task
    def create_customer_task(customer_data):
        """Background task for customer creation"""
        # Perform expensive operations
        customer = Customer.objects.create(**customer_data)

        # Register with external CRM
        external_crm = ExternalCRM()
        external_crm.register_customer(customer)

        # Send welcome email
        send_welcome_email(customer)

        return customer.pk

Key features of ``CeleryDjangoCoreResource``:

- Automatically queues long-running operations as Celery tasks
- Returns task ID immediately for tracking
- Client can poll for task status
- Ideal for imports, exports, batch operations
- Built-in error handling and retry logic

.. note::
   Use ``CeleryDjangoCoreResource`` when operations take more than 2-3 seconds to complete. This prevents HTTP timeouts and improves user experience.

Celery Background Export Integration
=====================================

Django IS Core integrates with Celery to handle large dataset exports in the background. The ``CeleryDjangoCoreResource`` class processes export requests asynchronously, preventing timeouts on large queries.

When to Use Background Export
------------------------------

Background export is useful when:

- Exporting large datasets that take more than a few seconds
- You want to avoid request timeouts
- Users need to continue working while export processes
- Export results should be emailed or stored for later download

Basic Setup
-----------

Extend ``CeleryDjangoCoreResource`` instead of the standard resource class:

.. code-block:: python
    :caption: cores/customer/resources.py

    from typing import TYPE_CHECKING
    from is_core.contrib.background_export.resource import CeleryDjangoCoreResource
    from is_core.utils.decorators import short_description

    if TYPE_CHECKING:
        from django.db.models import QuerySet
        from common.apps.customers.models import Customer


    class CustomerResource(CeleryDjangoCoreResource):
        model = Customer

        @short_description(_l("Coin balance"))
        def coin_balance(self, obj: Customer) -> int:
            """Computed field included in export."""
            return CoinTransaction.objects.compute_balance_for_customer(obj)

Using in Cores
--------------

Apply the resource to your core:

.. code-block:: python
    :caption: cores/customer/__init__.py

    from is_core.main import DjangoUiRestCore
    from .resources import CustomerResource


    class CustomerCore(DjangoUiRestCore):
        model = Customer
        rest_resource_class = CustomerResource

        list_fields = ('id', 'full_name', 'email', 'coin_balance')
        rest_extra_fields = ('coin_balance',)

When users click the export button, the task runs in the background and they receive a notification when complete.

Export Configuration
--------------------

Configure background export behavior in Django settings:

.. code-block:: python
    :caption: settings.py

    # Background export settings
    IS_CORE_BACKGROUND_EXPORT_ENABLED = True
    IS_CORE_BACKGROUND_EXPORT_TASK_EXPIRES = 3600  # Task expires after 1 hour
    IS_CORE_BACKGROUND_EXPORT_FILE_EXPIRES = 86400  # File available for 24 hours

    # Optional: Callback before export starts
    IS_CORE_BACKGROUND_EXPORT_TASK_CALLBACK = 'your.module.log_export_start'

Export Callback Hook
--------------------

Execute custom logic before export starts:

.. code-block:: python
    :caption: your/module.py

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from django.http import HttpRequest
        from django.db.models import QuerySet


    def log_export_start(
        request: HttpRequest,
        queryset: QuerySet,
        filename: str,
        **kwargs
    ) -> None:
        """Called before export task starts."""
        logger.info(
            f"User {request.user.id} exporting {queryset.count()} records to {filename}"
        )

Custom Resource Actions
========================

Resources can define custom POST/PUT/DELETE methods beyond standard CRUD operations. This is useful for triggering background tasks, running calculations, or executing business logic.

Defining Custom Actions
------------------------

Add custom methods to your resource:

.. code-block:: python
    :caption: cores/customer/resources.py

    from django.utils.translation import gettext as _g
    from django_celery_extensions.task import get_django_command_task
    from is_core.auth.permissions import PermissionsSet
    from is_core.contrib.background_export.resource import CeleryDjangoCoreResource
    from fperms_iscore.permissions import FPermPermission
    from pyston.response import RestOkResponse


    class SetCustomerABTestingCategoryResource(CeleryDjangoCoreResource):
        model = CustomerABTesting

        permission = PermissionsSet(
            post=FPermPermission(
                "customerabtesting__set_category_to_existing_customers",
                verbose_name=_l("Can set A/B testing categories"),
            ),
            get=SelfPermission("post"),  # GET requires same permission as POST
        )

        def post(self) -> RestOkResponse:
            """Trigger background task to set A/B testing categories."""
            get_django_command_task("set_customer_ab_testing_category").apply_async_on_commit()
            return RestOkResponse(
                _g("Assigning A/B testing categories to existing customers in progress.")
            )

Registering Custom Actions
---------------------------

Register the action in your core using ``get_rest_patterns()``:

.. code-block:: python
    :caption: cores/customer/__init__.py

    from is_core.patterns import RestPattern


    class CustomerCore(DjangoUiRestCore):
        model = Customer

        def get_rest_patterns(self):
            rest_patterns = super().get_rest_patterns()

            rest_patterns["set-ab-testing"] = RestPattern(
                "set-ab-testing-customer",
                self.site_name,
                r"set-ab-testing/",
                SetCustomerABTestingCategoryResource,
                self,
                methods=["post"],
            )

            return rest_patterns

This creates endpoint: ``POST /api/customer/set-ab-testing/``

Using Custom Actions
---------------------

Custom actions can be triggered from list actions or custom UI buttons:

.. code-block:: python

    from is_core.generic_views.actions import RestAction


    class CustomerCore(DjangoUiRestCore):
        def get_list_actions(self, request, obj=None):
            actions = super().get_list_actions(request, obj)

            actions.append(
                RestAction(
                    verbose_name=_l("Set A/B Testing"),
                    url=self.get_rest_pattern_url("set-ab-testing"),
                    method="POST",
                    confirm=_l("Start A/B testing assignment for all customers?"),
                )
            )

            return actions

Resource Field Decorators
==========================

Django IS Core provides decorators to enhance resource fields with filtering and sorting capabilities. These decorators work with ``rest_extra_fields`` to expose computed properties via the REST API.

@short_description Decorator
-----------------------------

Provides a human-readable label for the field:

.. code-block:: python

    from is_core.utils.decorators import short_description


    class CustomerResource(CeleryDjangoCoreResource):
        @short_description(_l("Total orders"))
        def total_orders(self, obj: Customer) -> int:
            return obj.orders.count()

@filter_class Decorator
------------------------

Enables filtering on computed fields:

.. code-block:: python

    from pyston.utils.decorators import filter_class
    from admin.apps.utils.filters import ValueWithCurrencyFilter


    class BankTransferRefundOrderResource(CeleryDjangoCoreResource):
        @short_description(_l("Amount"))
        @filter_class(ValueWithCurrencyFilter)
        def value_with_filtering(self, obj: BankTransferRefundOrder):
            return obj.value

This allows filtering: ``GET /api/refunds/?value_with_filtering__gte=1000``

@sorter_class Decorator
------------------------

Enables sorting on computed fields:

.. code-block:: python

    from pyston.utils.decorators import sorter_class
    from admin.apps.utils.sorters import ValueWithCurrencySorter


    class BankTransferRefundOrderResource(CeleryDjangoCoreResource):
        @short_description(_l("Amount"))
        @filter_class(ValueWithCurrencyFilter)
        @sorter_class(ValueWithCurrencySorter)
        def value_with_filtering(self, obj: BankTransferRefundOrder):
            return obj.value

This allows sorting: ``GET /api/refunds/?order=value_with_filtering``

Combining Decorators
--------------------

Stack decorators to provide full functionality:

.. code-block:: python

    class CustomerResource(CeleryDjangoCoreResource):
        @short_description(_l("Account balance"))
        @filter_class(MoneyFilter)
        @sorter_class(MoneySorter)
        def account_balance(self, obj: Customer):
            return obj.calculate_balance()

Using with rest_extra_fields
-----------------------------

Expose decorated fields via ``rest_extra_fields``:

.. code-block:: python

    class BankTransferRefundOrderCore(DjangoUiRestCore):
        model = BankTransferRefundOrder
        rest_resource_class = BankTransferRefundOrderResource

        list_fields = ('id', 'created_at', 'state', 'value_with_filtering')

        rest_extra_fields = ('value_with_filtering',)
        rest_extra_filter_fields = ('value_with_filtering',)

        @short_description(_l("Amount"))
        @filter_class(ValueWithCurrencyFilter)
        @sorter_class(ValueWithCurrencySorter)
        def value_with_filtering(self, obj):
            return obj.value

.. note::
   When using decorators on computed fields, the decorators must be defined on the resource or core class that has ``rest_extra_fields`` configuration.
