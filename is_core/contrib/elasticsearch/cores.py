from is_core.main import ModelCore, ModelUiCore, ModelUiRestCore, ModelRestCore

from .filters import CoreElasticsearchFilterManagerFilterManager
from .paginator import ElasticsearchOffsetBasedPaginator
from .resources import ElasticsearchCoreResource
from .views import ElasticsearchDetailView, ElasticsearchTableView


class ElasticsearchCore(ModelCore):
    """
    Base core for Elasticsearch models. Provides queryset handling and menu group generation for Elasticsearch
    documents.
    """

    abstract = True

    @property
    def menu_group(self):
        return self.model._index._name.replace('-', '_')

    def get_queryset(self, request):
        queryset = self.model.search()
        ordering = self.get_default_ordering()
        if ordering:
            queryset = queryset.sort(*ordering)
        return queryset


class ElasticsearchUiCore(ElasticsearchCore, ModelUiCore):
    """
    Elasticsearch UI core. Provides UI views for Elasticsearch documents with specialized table and detail views.
    """

    abstract = True

    ui_list_view = ElasticsearchTableView
    ui_detail_view = ElasticsearchDetailView


class ElasticsearchRestCore(ElasticsearchCore, ModelRestCore):
    """
    Elasticsearch REST core. Provides REST resources for Elasticsearch documents with specialized pagination
    and filtering.
    """

    abstract = True

    rest_resource_class = ElasticsearchCoreResource
    rest_paginator = ElasticsearchOffsetBasedPaginator()
    rest_filter_manager = CoreElasticsearchFilterManagerFilterManager()


class ElasticsearchUiRestCore(ElasticsearchRestCore, ElasticsearchUiCore, ModelUiRestCore):
    """
    Combined Elasticsearch UI and REST core. Provides both UI views and REST resources for Elasticsearch documents.
    """

    abstract = True
