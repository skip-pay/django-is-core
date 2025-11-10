.. _rests:

REST Resources
==============

Django IS Core provides a powerful REST API system built on top of django-pyston. Resources define REST endpoints that serve as the backend for UI actions and can be used independently to build custom frontends.

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

Best Practices
--------------

1. **Use DjangoCoreResource** for standard CRUD operations over models

2. **Implement proper permissions** at resource, object, and method levels

3. **Validate input** using Django forms integrated with resources

4. **Control serialization** to avoid exposing sensitive data

5. **Implement pagination** for list endpoints to avoid performance issues

6. **Use appropriate HTTP methods** - GET for reads, POST for creates, PUT/PATCH for updates, DELETE for deletes

7. **Return proper status codes** - 200 for success, 201 for created, 400 for validation errors, 403 for permission denied, 404 for not found

8. **Document custom endpoints** so frontend developers know how to use them

9. **Version your API** if you plan to make breaking changes

10. **Test REST endpoints** thoroughly, including error cases and edge conditions
