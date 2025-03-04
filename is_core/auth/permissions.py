from django.core.exceptions import ImproperlyConfigured


class BasePermission:
    """
    Base IS core permission object which has only one method has_permission which must be implemented in descendant.
    """

    def has_permission(self, name, request, view, obj=None):
        """
        Checks if request has permission to the given action.

        Args:
            name (str): name of the permission
            request (django.http.request.HttpRequest): Django request object
            view (object): Django view or REST view object
            obj (object): Object that is related with the given request

        Returns:
            True/False
        """
        raise NotImplementedError

    def _has_permission_in_permission_set(self, name, request, view, obj=None, parent=None):
        return self.has_permission(name, request, view, obj=obj)

    def __and__(self, other):
        assert isinstance(other, BasePermission), 'Only permission instances can be joined'

        return AndPermission(self, other)

    def __or__(self, other):
        assert isinstance(other, BasePermission), 'Only permission instances can be joined'

        return OrPermission(self, other)

    def __invert__(self):
        return NotPermission(self)


class OperatorPermission(BasePermission):

    operator = None
    operator_function = None

    def __init__(self, *permissions):
        self._permissions = list(permissions)

    def has_permission(self, name, request, view, obj=None):
        return self.operator_function(
            permission.has_permission(name, request, view, obj=obj) for permission in self._permissions
        )

    def _has_permission_in_permission_set(self, name, request, view, obj=None, parent=None):
        return self.operator_function(
            permission._has_permission_in_permission_set(name, request, view, obj=obj, parent=parent)
            for permission in self._permissions
        )

    def add(self, permission):
        assert isinstance(permission, BasePermission), 'Only permission instance can be added to the operator'

        self._permissions.append(permission)

    def __repr__(self):
        return '({})'.format(' {} '.format(self.operator).join(str(permission) for permission in self._permissions))

    def __iter__(self):
        for permission in self._permissions:
            yield permission


class AndPermission(OperatorPermission):
    """
    Helper for joining permissions with AND operator.
    """

    operator = '&'
    operator_function = all

    def __and__(self, other):
        assert isinstance(other, BasePermission), 'Only permission instances can be joined'
        return AndPermission(self, other)


class OrPermission(OperatorPermission):
    """
    Helper for joining permissions with OR operator.
    """

    operator = '|'
    operator_function = any

    def __or__(self, other):
        assert isinstance(other, BasePermission), 'Only permission instances can be joined'

        self.add(other)
        return self


class NotPermission(BasePermission):

    def __init__(self, permission):
        self._permission = permission

    def has_permission(self, name, request, view, obj=None):
        return not self._permission.has_permission(name, request, view, obj=obj)

    def _has_permission_in_permission_set(self, name, request, view, obj=None, parent=None):
        return not self._permission._has_permission_in_permission_set(name, request, view, obj=obj, parent=parent)


DEFAULT_PERMISSION = '__default__'


class PermissionsSet(BasePermission):
    """
    ``PermissionSet`` contains a set of permissions identified by name. Permission is granted if permission with the
    given name grants the access. Finally if no permission with the given name is found ``False`` is returned.
    """

    def __init__(self, **permissions_set):
        """
        Args:
            **permissions_set (BasePermission): permissions data
        """
        super().__init__()
        self._permissions = permissions_set

    def set(self, name, permission):
        """
        Adds permission with the given name to the set. Permission with the same name will be overridden.
        Args:
            name: name of the permission
            permission: permission instance
        """
        assert isinstance(permission, BasePermission), 'Only permission instances can be added to the set'

        self._permissions[name] = permission

    def has_permission(self, name, request, view, obj=None):
        permission = self._permissions.get(name, self._permissions.get(DEFAULT_PERMISSION, None))
        return (
            permission is not None
            and permission._has_permission_in_permission_set(name, request, view, obj=obj, parent=self)
        )

    def __iter__(self):
        for permission in self._permissions.values():
            yield permission


class IsAuthenticated(BasePermission):
    """
    Grant permission if user is authenticated and is active
    """

    def has_permission(self, name, request, view, obj=None):
        return request.user.is_authenticated and request.user.is_active


class IsSuperuser(BasePermission):
    """
    Grant permission if user is superuser
    """

    def has_permission(self, name, request, view, obj=None):
        return request.user.is_superuser


class IsAdminUser(BasePermission):
    """
    Grant permission if user is staff
    """

    def has_permission(self, name, request, view, obj=None):
        return request.user.is_staff


class AllowAny(BasePermission):
    """
    Grant permission every time
    """

    def has_permission(self, name, request, view, obj=None):
        return True


class CoreAllowed(BasePermission):
    """
    Grant permission if core permission with the name grants access
    """

    name = None

    def __init__(self, name=None):
        super().__init__()
        if name:
            self.name = name

    def has_permission(self, name, request, view, obj=None):
        return view.core.permission.has_permission(self.name or name, request, view, obj)


class CoreCreateAllowed(CoreAllowed):
    """
    Grant permission if core create permission grants access
    """

    name = 'create'


class CoreReadAllowed(CoreAllowed):
    """
    Grant permission if core read permission grants access
    """

    name = 'read'


class CoreUpdateAllowed(CoreAllowed):
    """
    Grant permission if core update permission grants access
    """

    name = 'update'


class CoreDeleteAllowed(CoreAllowed):
    """
    Grant permission if core delete permission grants access
    """

    name = 'delete'


class SelfPermission(CoreAllowed):
    """
    Self can be used in PermissionsSet and find in another permissions in the set to grant access
    """

    def __init__(self, name):
        super().__init__()
        self.name = name

    def _has_permission_in_permission_set(self, name, request, view, obj=None, parent=None):
        if not parent:
            raise ImproperlyConfigured('SelfPermission can be used only inside PermissionSet')

        return parent.has_permission(self.name, request, view, obj=obj)

    def has_permission(self, name, request, view, obj=None):
        raise ImproperlyConfigured('SelfPermission can be used only inside PermissionSet')


class FieldsPermission:

    def get_disallowed_fields(self, view):
        raise NotImplementedError

    def get_readonly_fields(self, view):
        raise NotImplementedError


class FieldsListPermission(FieldsPermission):

    def __init__(self, permission, fields):
        self.permission = permission
        self.fields = fields

    def _has_permission(self, name, request, view, obj=None):
        return self.permission.has_permission(name, request, view, obj=obj)

    def get_disallowed_fields(self, request, view, obj=None):
        return set(self.fields) if not self._has_permission('read', request, view, obj) else set()

    def get_readonly_fields(self, request, view, obj=None):
        return set(self.fields) if not self._has_permission('edit', request, view, obj) else set()


class FieldsSetPermission(FieldsPermission):

    def __init__(self, *fields_permissions):
        self.fields_permissions = fields_permissions

    def get_disallowed_fields(self, request, view, obj=None):
        allowed_fields = set()
        for fields_permission in self.fields_permissions:
            allowed_fields |= fields_permission.get_disallowed_fields(request, view, obj)
        return allowed_fields

    def get_readonly_fields(self, request, view, obj=None):
        readonly_fields = set()
        for fields_permission in self.fields_permissions:
            readonly_fields |= fields_permission.get_readonly_fields(request, view, obj)
        return readonly_fields
