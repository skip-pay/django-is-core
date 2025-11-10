Filters
=======

Filters are documented in the django-pyston library. IS Core uses Pyston filters to generate list views. Every column can contain a form input that accepts filter data. There are several options for configuring the Django widget used for rendering the filter input HTML:

UIFilterMixin
^^^^^^^^^^^^^

Django IS Core provides a special mixin for filters that adds the ability to change the rendered widget inside the filter class.
For example, a ``ForeignKeyFilter`` with the ability to restrict field queryset choices::

    class RestrictedFkFilter(UIFilterMixin, ForeignKeyFilter):

        def get_restricted_queryset(self, qs, request):
            # There can be foreign key queryset restricted
            return qs

        def get_widget(self, request):
            formfield = self.field.formfield()
            formfield.queryset = self.get_restricted_queryset(formfield.queryset, request)
            return formfield.widget


Field Filter
^^^^^^^^^^^^

There are two possibilities:

1. If the filter has a ``choices`` attribute set, the filter is always rendered as a select box with those choices
2. Otherwise, the filter widget is obtained from the model field using the ``formfield()`` method

Method/Resource Filter
^^^^^^^^^^^^^^^^^^^^^^

The same rule applies as for field filters, but if ``choices`` is not defined, a simple text input is returned.
