.. _permissions:

Permissions
===========

The main goal of the permissions system is to check if a client has access to read/update/delete views. The implementation of Django IS Core's permissions system is very similar to Django REST Framework (DRF) permissions.

.. seealso::

   :ref:`cores`
      Setting permissions on Core classes

   :ref:`views`
      View-level permissions

   :ref:`rests`
      REST resource permissions

The base permission class is:

.. class:: is_core.auth.permissions.BasePermission

  Objects define structure of all permissions instances.

  .. method:: has_permission(name, request, view, obj=None)

    Method must be implemented for every permission object and should return True if all requirements was fulfilled to grant access to the client.
    First parameter name defines name of the wanted access, request is Django request object, view is Django view or REST resource and optional parameter obj is obj related with the given request.

Predefined permissions
----------------------

Quick Reference
^^^^^^^^^^^^^^^

+---------------------------+---------------------------+---------------------------+
| **Permission Class**      | **Use Case**              | **Grants Access When**    |
+===========================+===========================+===========================+
| AllowAny                  | Public endpoints          | Always                    |
+---------------------------+---------------------------+---------------------------+
| IsAuthenticated           | Logged-in users only      | User is authenticated     |
+---------------------------+---------------------------+---------------------------+
| IsAdminUser               | Staff members             | User is staff             |
+---------------------------+---------------------------+---------------------------+
| IsSuperuser               | Admin operations          | User is superuser         |
+---------------------------+---------------------------+---------------------------+
| CoreReadAllowed           | View-only access          | Core read permission OK   |
+---------------------------+---------------------------+---------------------------+
| CoreCreateAllowed         | Creating objects          | Core create permission OK |
+---------------------------+---------------------------+---------------------------+
| CoreUpdateAllowed         | Editing objects           | Core update permission OK |
+---------------------------+---------------------------+---------------------------+
| CoreDeleteAllowed         | Deleting objects          | Core delete permission OK |
+---------------------------+---------------------------+---------------------------+

Permission Classes
^^^^^^^^^^^^^^^^^^

.. class:: is_core.auth.permissions.PermissionsSet

  ``PermissionSet`` contains a set of permissions identified by name. Permission is granted if permission with the given name grants the access. Finally if no permission with the given name is found ``False`` is returned.

.. class:: is_core.auth.permissions.IsAuthenticated

  Grants permission if user is authenticated and is active.

.. class:: is_core.auth.permissions.IsSuperuser

  Grants permission if user is authenticated, is active and is superuser.

.. class:: is_core.auth.permissions.IsAdminUser

  Grants permission if user is authenticated, is active and is staff.

.. class:: is_core.auth.permissions.AllowAny

  Grants permission every time.

.. class:: is_core.auth.permissions.CoreAllowed

  Grants permission if core (related with the view) permission selected according to the name grants the access.

.. class:: is_core.auth.permissions.CoreReadAllowed

  Grants permission if core read permission grant access.

.. class:: is_core.auth.permissions.CoreCreateAllowed

  Grants permission if core create permission grant access.

.. class:: is_core.auth.permissions.CoreUpdateAllowed

  Grants permission if core update permission grant access.

.. class:: is_core.auth.permissions.CoreDeleteAllowed

  Grants permission if core delete permission grant access.

.. class:: is_core.auth.permissions.AndPermission

  ``AndPermission`` is only helper for joining more permissions with ``AND`` operator. ``AndPermission`` init method accepts any number of permission instances and returns ``True`` if every inner permission returns ``True``::

    AndPermission(IsAdminUser(), IsSuperuser(), IsAuthenticated())

  Because this style of implementation is badly readable you can join permissions ``&``, the result will be the same::

    IsAdminUser() & IsSuperuser() & IsAuthenticated()

.. class:: is_core.auth.permissions.OrPermission

  ``OrPermission`` is same as ``AndPermission`` but permissions are joined with ``OR`` operator. ``OrPermission`` returns ``True`` if any inner permission returns ``True``. Again you can use joining with ``|`` operator::

    OrPermission(IsAdminUser(), IsSuperuser(), IsAuthenticated())
    IsAdminUser() | IsSuperuser() | IsAuthenticated()

.. class:: is_core.auth.permissions.NotPermission

  ``NotPermission`` can be used for permission negation. You can use operator ``~`` for the same purpose::

    NotPermission(IsAdminUser())
    ~IsAdminUser()


.. class:: is_core.auth.permissions.SelfPermission

  If you are using ``PermissionSet`` you can use ``SelfPermission`` to remove duplicates::

    PermissionSet(
        admin=IsAdminUser(),
        superuser=IsSuperuser(),
        admin_and_superuser=SelfPermission('admin') & SelfPermission('superuser')
    )

Custom permission
-----------------

If you want to implement custom permission, you only must create subclass of ``is_core.auth.permissions.BasePermission`` and implement ``has_permission`` method.

Core permissions
----------------

.. important::
   Permissions defined on a Core cascade to all its views and REST resources by default.

As an example of how to define core permissions we use model core of User object::

    from django.contrib.auth.models import User

    from is_core.auth.permissions import IsSuperuser
    from is_core.main import DjangoUiRestCore

    class UserISCore(DjangoUiRestCore):

        model = User
        permission = IsSuperuser()


Now only a superuser has access to the User core. But this solution is a little bit dangerous, because there is no validated permission name and we only want create,read, update and delete permission names. Better solution is to use ``is_core.auth.permissions.PermissionsSet``::

    from django.contrib.auth.models import User

    from is_core.auth.permissions import PermissionsSet, IsSuperuser
    from is_core.main import DjangoUiRestCore

    class UserISCore(DjangoUiRestCore):

        model = User
        permission = PermissionsSet(
            add=IsSuperuser(),
            read=IsSuperuser(),
            update=IsSuperuser(),
            delete=IsSuperuser(),
        )

Because writing too much code can lead to typos you can use ``default_permission`` attribute from which is automatically generated ``permission`` the result will be same as in previous example::

    from django.contrib.auth.models import User

    from is_core.auth.permissions import IsSuperuser
    from is_core.main import DjangoUiRestCore

    class UserISCore(DjangoUiRestCore):

        model = User
        default_permission = IsSuperuser()

But if you want to disable for example deleting model instances the delete permission will not be added to the permission set::

    from django.contrib.auth.models import User

    from is_core.auth.permissions import IsSuperuser
    from is_core.main import DjangoUiRestCore

    class UserISCore(DjangoUiRestCore):

        model = User
        default_permission = IsSuperuser()
        can_delete = False

the attribute permission will be now::

   permission = PermissionsSet(
       add=IsSuperuser(),
       read=IsSuperuser(),
       update=IsSuperuser(),
   )



You can use operator joining for using more permission types::

    from django.contrib.auth.models import User

    from is_core.auth.permissions import IsSuperuser, IsAdminUser
    from is_core.main import DjangoUiRestCore

    class UserISCore(DjangoUiRestCore):

        model = User
        default_permission = IsSuperuser() & IsAdminUser()

For some cases is necessary update permissions in a class mixin for this purpose you can use method ``_init_permission(permission)`::

    from is_core.auth.permissions import IsSuperuser, IsAdminUser
    from is_core.main import DjangoUiRestCore


    class HistoryISCoreMixin:

        def _init_permission(self, permission):
            permission = super()._init_permission(permission)
            permission.set('history', IsSuperuser())
            return permission

    class UserISCore(DjangoUiRestCore):

        model = User
        permission = PermissionsSet(
            add=IsAdminUser(),
            read=IsAdminUser(),
            update=IsAdminUser(),
            delete=IsAdminUser(),
        )


View permissions
----------------

View permissions are used in the same way as core permissions::

    from is_core.auth.permissions import IsSuperuser
    from is_core.generic_views.form_views import ReadonlyDetailModelFormView

    class UserReadonlyDetailModelFormView(ReadonlyDetailModelFormView):

        permission = IsSuperuser()


Again you can set permissions according to names. For view permissions the names are HTTP method names::

    from is_core.auth.permissions import PermissionsSet, IsSuperuser
    from is_core.generic_views.form_views import DetailModelFormView

    class UserDetailModelFormView(DetailModelFormView):

        permission = PermissionsSet(
            post=IsSuperuser(),
            get=IsSuperuser()
        )

By default core views get access permissions from core. For example detail view permissions are set this way::

    from is_core.auth.permissions import PermissionsSet, CoreReadAllowed, CoreUpdateAllowed
    from is_core.generic_views.form_views import DetailModelFormView

    class UserDetailModelFormView(DetailModelFormView):

        permission = PermissionsSet(
            post=CoreUpdateAllowed(),
            get=CoreReadAllowed()
        )

If you want to have edit view accessible only if user is allowed to modify an object in core permissions. You can use very similar implementation::

    from is_core.auth.permissions import PermissionsSet, CoreUpdateAllowed
    from is_core.generic_views.form_views import DetailModelFormView

    class UserDetailModelFormView(DetailModelFormView):

        permission = PermissionsSet(
            post=CoreUpdateAllowed(),
            get=CoreUpdateAllowed()
        )


REST permissions
----------------

For the REST classes permissions you can use the same rules. The only difference is that there are more types of permissions because REST resource fulfills two functions - serializer and view (HTTP requests)::

    from is_core.rest.resource import PermissionsModelResourceMixin

    class PermissionsModelISCoreResourceMixin(PermissionsModelResourceMixin):

        permission = PermissionsSet(
            # HTTP permissions
            head=CoreReadAllowed(),
            options=CoreReadAllowed(),
            post=CoreCreateAllowed(),
            get=CoreReadAllowed(),
            put=CoreUpdateAllowed(),
            patch=CoreUpdateAllowed(),
            delete=CoreDeleteAllowed(),

            # Serializer permissions
            create_obj=CoreCreateAllowed(),
            read_obj=CoreReadAllowed(),
            update_obj=CoreUpdateAllowed(),
            delete_obj=CoreDeleteAllowed()
        )


Check permissions
-----------------

View/resource
^^^^^^^^^^^^^

If you want to check your custom permission in view or REST resource you can use method ``has_permission(name, obj=None)`` as an example we can use method ``is_readonly`` in th form view (form is readonly only if post permission returns ``False``)::


    def is_readonly(self):
        return not self.has_permission('post')


Because some permissions require obj parameter all views that inherit from ``is_core.generic_views.mixins.GetCoreObjViewMixin`` has automatically added objects to the permission check.


Core
^^^^

Sometimes you need to check permission in the core. But there is no view instance and you will have to create it. For better usability you can check permissions via view patterns, as an example we can use method ``get_list_actions`` which return edit action only if user has permission to update an object::

    def get_list_actions(self, request, obj):
        list_actions = super(DjangoUiRestCore, self).get_list_actions(request, obj)
        detail_pattern = self.ui_patterns.get('detail')
        if detail_pattern and detail_pattern.has_permission('get', request, obj=obj):
            return [
                WebAction(
                    'detail-{}'.format(self.get_menu_group_pattern_name()), _('Detail'),
                    'edit' if detail_pattern.has_permission('post', request, obj=obj) else 'detail'
                )
            ] + list(list_actions)
        else:
            return list_actions


Pattern method ``has_permission(name, request, obj=None, **view_kwargs)`` can be used with more ways. By default is ``view_kwargs`` get from request kwargs. If you can change it you can use method kwargs parameters. Parameter ``obj`` can be used for save system performance because object needn't be loaded from database again::

    detail_pattern = self.ui_patterns.get('detail')
    detail_pattern.has_permission('get', request)  # object id is get from request.kwargs
    detail_pattern.has_permission('get', request, id=obj.pk)  # request.kwargs "id" is overridden with obj.pk
    detail_pattern.has_permission('get', request, obj=obj)  # saves db queryes because object needn't be loaded from database


Field permissions
-----------------

Fields can be restricted with permissions too. You can define readonly or editable fields according to defined permissions. For example::

    class UserISCore(DjangoUiRestCore):

        model = User
        field_permissions = FieldsSetPermission(
            FieldsListPermission(
                permission=PermissionsSet(
                    read=IsAdminUser(),
                    edit=IsSuperuser()
                ),
                fields=(
                    'username',
                )
            ),
            FieldsListPermission(
                permission=PermissionsSet(
                    read=IsSuperuser(),
                    edit=IsSuperuser()
                ),
                fields=(
                    'is_superuser',
                )
            )
        )

Generated views and REST resources will have restricted fields according to defined permissions. For the example only superuser can read and edit field ``is_superuser`` and only superuser can edit field ``username``.  The permissions restrict defined fields in export, REST views, UI views or bulk change view.

Field-Level Permissions Implementation
=======================================

Field-level permissions allow you to control which fields users can view or edit based on their permissions. This is implemented using dynamic ``readonly_fields`` modification and permission checking in views.

Dynamic Readonly Fields
------------------------

Override ``get_readonly_fields()`` to make fields read-only based on permissions:

.. code-block:: python
    :caption: cores/customer/views.py

    from typing import TYPE_CHECKING
    from is_core.generic_views.detail_views import DjangoDetailFormView

    if TYPE_CHECKING:
        from django.http import HttpRequest
        from common.apps.customers.models import Customer


    class CustomerDetailView(DjangoDetailFormView):
        form_class = CustomerEditForm

        def get_readonly_fields(
            self,
            request: HttpRequest,
            obj: Customer | None = None
        ) -> tuple[str, ...]:
            readonly_fields = list(super().get_readonly_fields(request, obj))

            # Make personal_id readonly unless user has specific permission
            if not request.user.has_perm('customers.change_personal_id'):
                readonly_fields.extend(['personal_id', 'id_card_no', 'id_card_expiry_date'])

            # Make admin fields readonly for non-admins
            if not request.user.is_staff:
                readonly_fields.extend(['is_active', 'internal_notes'])

            return tuple(readonly_fields)

Conditional Field Visibility
-----------------------------

Remove fields entirely based on permissions:

.. code-block:: python

    class CustomerDetailView(DjangoDetailFormView):
        def get_fields(
            self,
            request: HttpRequest,
            obj: Customer | None = None
        ) -> tuple[str, ...]:
            fields = list(super().get_fields(request, obj))

            # Remove sensitive fields for non-superusers
            if not request.user.is_superuser:
                fields = [f for f in fields if f not in ('internal_id', 'test_account_flag')]

            return tuple(fields)

Using FieldsPermission
----------------------

Use ``FieldsPermission`` for declarative field-level control:

.. code-block:: python

    from is_core.auth.permissions import FieldsPermission


    class CustomerDetailView(DjangoDetailFormView):
        permission = FieldsPermission(
            read_permission='customers.view_customer',
            write_permission='customers.change_customer',
            readonly_fields={
                'personal_id': 'customers.change_personal_id',
                'points': 'customers.change_points',
            }
        )

This makes ``personal_id`` and ``points`` readonly unless the user has the specific permissions.

Using FieldsSetPermission
--------------------------

Group fields with different permission requirements:

.. code-block:: python

    from is_core.auth.permissions import FieldsSetPermission


    class CustomerDetailView(DjangoDetailFormView):
        permission = FieldsSetPermission(
            read=(
                ('customers.view_customer', ('first_name', 'last_name', 'email')),
                ('customers.view_customer_sensitive', ('personal_id', 'birth_date')),
            ),
            write=(
                ('customers.change_customer', ('first_name', 'last_name')),
                ('customers.change_customer_sensitive', ('personal_id',)),
            )
        )

Users need ``view_customer_sensitive`` permission to see ``personal_id`` and ``birth_date``, and ``change_customer_sensitive`` to edit ``personal_id``.

Fieldset-Level Permissions
---------------------------

Control visibility of entire fieldsets:

.. code-block:: python

    class CustomerDetailView(DjangoDetailFormView):
        def get_fieldsets(
            self,
            request: HttpRequest | None = None,
            obj: Customer | None = None
        ) -> tuple:
            fieldsets = [
                (_l('Basic Information'), {
                    'fields': ('first_name', 'last_name', 'email'),
                }),
            ]

            # Only show admin fieldset to staff
            if request and request.user.is_staff:
                fieldsets.append(
                    (_l('Admin Settings'), {
                        'fields': ('is_active', 'internal_notes', 'test_flag'),
                        'classes': ('collapse',),
                    })
                )

            return tuple(fieldsets)

Permission Sets with FPerms Integration
========================================

Django IS Core integrates with ``django-fperms`` for object-level permissions. The ``fperms-iscore`` package provides ``FPermPermission`` for fine-grained access control.

Basic FPermPermission Usage
----------------------------

Use ``FPermPermission`` to check for specific permissions:

.. code-block:: python
    :caption: cores/customer/resources.py

    from fperms_iscore.permissions import FPermPermission
    from is_core.auth.permissions import PermissionsSet
    from is_core.contrib.background_export.resource import CeleryDjangoCoreResource


    class SetCustomerABTestingCategoryResource(CeleryDjangoCoreResource):
        model = CustomerABTesting

        permission = PermissionsSet(
            post=FPermPermission(
                "customerabtesting__set_category_to_existing_customers",
                verbose_name=_l("Can set A/B testing categories to existing customers"),
            ),
            get=SelfPermission("post"),
        )

        def post(self):
            # Only users with the fperm can execute this
            get_django_command_task("set_customer_ab_testing_category").apply_async_on_commit()
            return RestOkResponse(_g("Assignment in progress."))

Permission Naming Convention
-----------------------------

FPerms use a specific naming format: ``model__action_description``

.. code-block:: python

    # Format: {model_name}__{action_description}
    FPermPermission("customer__export_sensitive_data")
    FPermPermission("order__approve_refund")
    FPermPermission("billing__override_payment")

Combining Permissions
----------------------

Use ``PermissionsSet`` to set different permissions per HTTP method:

.. code-block:: python

    from is_core.auth.permissions import PermissionsSet, SelfPermission


    class CustomerResource(CeleryDjangoCoreResource):
        permission = PermissionsSet(
            get=FPermPermission("customer__view_details"),
            post=FPermPermission("customer__create"),
            put=FPermPermission("customer__update"),
            delete=FPermPermission("customer__delete"),
        )

SelfPermission Shortcut
------------------------

Use ``SelfPermission`` to reuse another method's permission:

.. code-block:: python

    class CustomerResource(CeleryDjangoCoreResource):
        permission = PermissionsSet(
            post=FPermPermission("customer__bulk_update"),
            get=SelfPermission("post"),  # GET requires same permission as POST
        )

This is useful for custom actions where GET should require the same permission as the action itself.

View-Level FPermPermission
---------------------------

Apply FPerms to view classes:

.. code-block:: python

    from is_core.generic_views.detail_views import DjangoDetailFormView


    class CustomerDetailView(DjangoDetailFormView):
        permission = FPermPermission("customer__view_sensitive_data")

        def get_readonly_fields(self, request, obj=None):
            readonly = list(super().get_readonly_fields(request, obj))

            # Additional granular control
            if not request.user.has_perm('customer__edit_personal_id'):
                readonly.append('personal_id')

            return tuple(readonly)
