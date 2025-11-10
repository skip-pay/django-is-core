.. _utils:

Utility Functions
=================

Django IS Core provides utility functions for common tasks like rendering objects as links, displaying values, and checking permissions.

.. seealso::

   :ref:`views`
      Using utilities in custom views

   :ref:`cores`
      Using utilities in Core methods

Display Utilities
-----------------

render_model_object_with_link
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. function:: render_model_object_with_link(request, obj, display_value=None)

   Returns clickable HTML link to a model object's detail view.

   **Parameters:**
     - ``request`` - Current HTTP request (for permission checking)
     - ``obj`` - Model instance to render
     - ``display_value`` (optional) - Override default text representation

   **Returns:**
     HTML string with link if user has permission, plain text otherwise

   **Example:**

   Display related object as clickable link in a view::

       class Article(models.Model):
           author = models.ForeignKey(User)

           @property
           def author_link(self):
               from is_core.utils import render_model_object_with_link
               # Returns: <a href="/admin/users/5/">John Doe</a>
               return render_model_object_with_link(
                   self.request,
                   self.author
               )

       class ArticleCore(DjangoUiRestCore):
           model = Article
           list_display = ('title', 'author_link')

   Use custom display text::

       author_link = render_model_object_with_link(
           request,
           article.author,
           display_value=f"{article.author.first_name} {article.author.last_name}"
       )

render_model_objects_with_link
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. function:: render_model_objects_with_link(request, objs)

   Generates humanized value from multiple objects with links.

   **Parameters:**
     - ``request`` - Current HTTP request
     - ``objs`` - Queryset or list of model instances

   **Returns:**
     Comma-separated HTML links

   **Example:**

   Display ManyToMany relationships::

       class Article(models.Model):
           tags = models.ManyToManyField(Tag)

           @property
           def tags_links(self):
               from is_core.utils import render_model_objects_with_link
               # Returns: <a href="/tags/1/">Django</a>, <a href="/tags/2/">Python</a>
               return render_model_objects_with_link(
                   self.request,
                   self.tags.all()
               )

display_for_value
^^^^^^^^^^^^^^^^^

.. function:: display_for_value(value, request=None)

   Returns humanized format of any value type.

   **Handles:**
     - Model objects → String representation with optional link
     - Lists/Querysets → Comma-separated values
     - Dicts → Key-value pairs
     - Numbers → Formatted numbers
     - Booleans → ✓ / ✗ icons
     - Datetime → Localized datetime
     - None → Empty string
     - Other → String representation

   **Example:**

   Format values for display::

       from is_core.utils import display_for_value

       # Boolean → "✓"
       display_for_value(True)

       # DateTime → "Jan 15, 2024, 2:30 PM"
       display_for_value(datetime.now())

       # List → "Item 1, Item 2, Item 3"
       display_for_value([obj1, obj2, obj3])

       # Dict → "key1: value1, key2: value2"
       display_for_value({'name': 'John', 'age': 30})

display_json
^^^^^^^^^^^^

.. function:: display_json(value)

   Returns pretty-printed JSON with syntax highlighting.

   **Parameters:**
     - ``value`` - JSON string

   **Returns:**
     HTML with formatted JSON

   **Example:**

   Display JSON field in readable format::

       class APILog(models.Model):
           response_data = models.JSONField()

           @property
           def formatted_response(self):
               from is_core.utils import display_json
               import json
               return display_json(json.dumps(self.response_data))

display_code
^^^^^^^^^^^^

.. function:: display_code(value)

   Formats code with preserved whitespace and monospace font.

   **Parameters:**
     - ``value`` - Code string

   **Returns:**
     HTML with preserved formatting

   **Example:**

   Display code snippets::

       from is_core.utils import display_code

       code = """
       def hello():
           print("Hello, World!")
       """
       formatted = display_code(code)
       # Preserves indentation and line breaks

URL and Permission Utilities
-----------------------------

get_link_or_none
^^^^^^^^^^^^^^^^

.. function:: get_link_or_none(pattern_name, request, view_kwargs=None)

   Generates URL if user has permission, otherwise returns None.

   **Parameters:**
     - ``pattern_name`` - Django URL pattern name
     - ``request`` - Current HTTP request
     - ``view_kwargs`` (optional) - URL parameters

   **Returns:**
     URL string if permitted, None otherwise

   **Example:**

   Conditionally show links based on permissions::

       from is_core.utils import get_link_or_none

       class ArticleCore(DjangoUiRestCore):
           def get_list_actions(self, obj, request):
               actions = []

               # Only add edit link if user has permission
               edit_url = get_link_or_none(
                   'article-edit',
                   request,
                   view_kwargs={'pk': obj.pk}
               )
               if edit_url:
                   actions.append({
                       'name': 'edit',
                       'url': edit_url,
                       'verbose_name': 'Edit'
                   })

               return actions

Common Patterns
---------------

Custom Display Methods
^^^^^^^^^^^^^^^^^^^^^^^

Create custom display methods for Core list views::

    class OrderCore(DjangoUiRestCore):
        model = Order
        list_display = ('order_number', 'customer_link', 'total_formatted')

        def customer_link(self, obj):
            return render_model_object_with_link(
                self.request,
                obj.customer,
                display_value=obj.customer.get_full_name()
            )
        customer_link.short_description = 'Customer'

        def total_formatted(self, obj):
            return display_for_value(obj.total)
        total_formatted.short_description = 'Total'

Permission-Based Display
^^^^^^^^^^^^^^^^^^^^^^^^

Show different content based on permissions::

    class ArticleCore(DjangoUiRestCore):
        def internal_notes_display(self, obj):
            if self.request.user.is_staff:
                return display_for_value(obj.internal_notes)
            return "—"  # Hide from non-staff

Read-only Field Rendering
^^^^^^^^^^^^^^^^^^^^^^^^^^

Use in fieldsets for read-only display::

    class ArticleDetailView(DjangoDetailFormView):
        fieldsets = (
            ('Info', {
                'fields': ('title', 'author_display')
            }),
        )

        def author_display(self, obj):
            return render_model_object_with_link(
                self.request,
                obj.author
            )

Best Practices
--------------

1. **Use display utilities in list_display** - Keep views clean and readable
2. **Check permissions** - Use ``get_link_or_none`` to avoid broken links
3. **Custom display text** - Override default ``__str__`` when needed
4. **Handle None values** - ``display_for_value`` handles None gracefully
5. **Cache expensive queries** - Don't call database in display methods repeatedly