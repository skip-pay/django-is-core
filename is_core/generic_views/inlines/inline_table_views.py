from typing import Dict, Any, List

from django.forms.models import _get_foreign_key
from django.urls import reverse

from is_core.generic_views.table_views import DjangoTableViewMixin, BaseModelTableViewMixin
from is_core.generic_views.inlines.base import RelatedInlineView
from is_core.utils import get_export_types_with_content_type
from is_core.rest.datastructures import ModelFlatRestFields


class BaseModelInlineTableViewMixin:

    template_name = 'is_core/forms/inline_table.html'
    inline_bulk_change = False
    inline_export = False

    def _get_field_labels(self):
        return (
            self.field_labels if self.field_labels is not None or not self.related_core
            else self.related_core.get_field_labels(self.request)
        )

    def _get_fields(self):
        return (
            self.related_core.get_list_fields(self.request) if self.related_core and self.fields is None
            else self.fields
        )

    def _get_export_fields(self):
        return (
            self.related_core.get_export_fields(self.request) if self.related_core and self.export_fields is None
            else self.export_fields
        )

    def _get_export_types(self) -> List | None:
        return (
            self.related_core.get_export_types(self.request) if self.related_core and
            getattr(self, 'export_types', None) is None
            else getattr(self, 'export_types', None)
        )

    def _get_list_per_page(self):
        list_per_page = self.related_core.get_list_per_page(self.request) if self.related_core else None
        return list_per_page if list_per_page is not None else super()._get_list_per_page()

    def _get_api_url(self):
        return self.related_core.get_api_url(self.request)

    def _get_menu_group_pattern_name(self):
        return self.related_core.get_menu_group_pattern_name()

    def get_title(self):
        return self.get_list_verbose_name() % {
            'verbose_name': self.get_verbose_name(),
            'verbose_name_plural': self.get_verbose_name_plural()
        } if self.title is None else self.title

    def is_bulk_change_enabled(self) -> bool:
        return (
            self.inline_bulk_change and
            hasattr(self.related_core, 'is_bulk_change_enabled') and
            self.related_core.is_bulk_change_enabled() and
            self.related_core.ui_patterns.get(self.related_core.get_bulk_change_url_name()).has_permission(
                'get', self.request
            )
        )

    def get_bulk_change_snippet_name(self) -> str:
        return '-'.join(('default', self.related_core.menu_group, 'form'))

    def get_bulk_change_form_url(self) -> str | None:
        if not self.is_bulk_change_enabled():
            return None
        return reverse(
            ''.join(('IS:', self.related_core.get_bulk_change_url_name(), '-', self.related_core.menu_group))
        )

    def _generate_rest_export_fieldset(self) -> ModelFlatRestFields:
        return ModelFlatRestFields.create_from_flat_list(
            list(self._get_allowed_export_fields()), self.model
        )

    def is_export_enabled(self) -> bool:
        """
        Returns whether export is enabled for this inline table.
        Checks both the inline_export flag and if export types/fields are available.
        """
        return (
            self.inline_export and
            self._get_export_types() and
            self._get_allowed_export_fields()
        )

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data.update({
            'inline_bulk_change': self.is_bulk_change_enabled(),
            'bulk_change_snippet_name': self.get_bulk_change_snippet_name(),
            'bulk_change_form_url': self.get_bulk_change_form_url(),
            'inline_export_enabled': self.is_export_enabled(),
        })
        if self.is_export_enabled():
            context_data.update({
                'rest_export_fieldset': self._generate_rest_export_fieldset(),
                'export_types': get_export_types_with_content_type(self._get_export_types()),
            })
        return context_data


class BaseModelInlineTableView(BaseModelInlineTableViewMixin, BaseModelTableViewMixin, RelatedInlineView):
    pass


class DjangoInlineTableView(BaseModelInlineTableViewMixin, DjangoTableViewMixin, RelatedInlineView):

    fk_name = None

    def _get_list_filter(self):
        list_filter = super()._get_list_filter()
        fk_name = _get_foreign_key(self.parent_instance.__class__, self.model, fk_name=self.fk_name).name
        list_filter['filter'] = filter = list_filter.get('filter', {})
        if 'filter' in list_filter:
            filter[fk_name] = self.parent_instance.pk
        return list_filter
