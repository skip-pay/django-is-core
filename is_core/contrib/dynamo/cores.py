from django.utils.translation import gettext_lazy as _l

from is_core.main import ModelCore, ModelUiCore, ModelUiRestCore, ModelRestCore
from is_core.utils.decorators import short_description

from .paginator import DynamoCursorBasedPaginator
from .resources import DynamoCoreResource
from .views import DynamoDetailView, DynamoTableView


class DynamoCore(ModelCore):
    """
    Base core for DynamoDB models. Provides queryset handling and object retrieval for DynamoDB documents.
    """

    abstract = True

    rest_paginator = DynamoCursorBasedPaginator()

    rest_range_key = None

    @property
    def menu_group(self):
        return self.model.__class__.__name__.lower()

    def get_queryset(self, request):
        return self.model.objects.set_hash_key(self._get_hash_key(request))

    def _get_hash_key(self, request):
        raise NotImplementedError

    def _get_obj(self, request, pk):
        return self.model.get(self._get_hash_key(request), pk)

    def get_obj(self, request, pk):
        if not pk:
            return None
        try:
            return self._get_obj(request, pk)
        except self.model.DoesNotExist:
            return None

    @short_description(_l('object name'))
    def _obj_name(self):
        return self.verbose_name


class DynamoUiCore(DynamoCore, ModelUiCore):
    """
    DynamoDB UI core. Provides UI views for DynamoDB documents with specialized table and detail views.
    """

    abstract = True

    ui_list_view = DynamoTableView
    ui_detail_view = DynamoDetailView


class DynamoRestCore(DynamoCore, ModelRestCore):
    """
    DynamoDB REST core. Provides REST resources for DynamoDB documents with cursor-based pagination.
    """

    abstract = True

    rest_paginator = DynamoCursorBasedPaginator()
    rest_resource_class = DynamoCoreResource


class DynamoUiRestCore(DynamoUiCore, DynamoRestCore, ModelUiRestCore):
    """
    Combined DynamoDB UI and REST core. Provides both UI views and REST resources for DynamoDB documents.
    """

    abstract = True
