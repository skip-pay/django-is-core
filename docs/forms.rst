.. _forms:

Forms
=====

Django IS Core extends Django's form system with additional features for building rich admin interfaces. Forms handle validation, sanitization of input, and rendering of fields through enhanced widgets.

.. seealso::

   :ref:`views`
      Views that use these forms

   :ref:`rests`
      REST resources use forms for validation

Form Features
-------------

IS Core forms provide several enhancements over standard Django forms:

- **Enhanced widgets** with custom rendering and CSS classes
- **Read-only field support** for display-only contexts
- **Automatic placeholder generation**
- **Custom date/time pickers**
- **File and image upload widgets** with preview
- **Multiple choice improvements**

Form Types
----------

DjangoForm
^^^^^^^^^^

Base form class with IS Core enhancements.

Example::

    from is_core.forms import DjangoForm
    from .models import Article

    class ArticleForm(DjangoForm):
        class Meta:
            model = Article
            fields = ('title', 'content', 'author', 'published_at')

        def clean_title(self):
            title = self.cleaned_data['title']
            if len(title) < 10:
                raise ValidationError('Title must be at least 10 characters')
            return title

SmartModelForm
^^^^^^^^^^^^^^

Advanced model form with automatic field generation and validation.

Example::

    from is_core.forms import SmartModelForm

    class ArticleForm(SmartModelForm):
        class Meta:
            model = Article
            exclude = ('slug',)
            readonly_fields = ('created_at', 'updated_at')

Widgets
-------

IS Core provides enhanced widgets that extend Django's default widgets with additional functionality.

Enhanced Default Widgets
^^^^^^^^^^^^^^^^^^^^^^^^^

During IS Core initialization, default Django widgets are monkey-patched with the following enhancements:

**className attribute**
  Automatic CSS class assignment for consistent styling

**Placeholder support**
  Placeholders automatically generated from field help_text or verbose_name

**Custom rendering**
  Enhanced HTML rendering with wrapper elements and data attributes

Text Widgets
^^^^^^^^^^^^

TextInput
  Single-line text input with placeholder support

Textarea
  Multi-line text input with auto-resize capability

Example::

    from django import forms
    from is_core.forms import DjangoForm

    class ArticleForm(DjangoForm):
        title = forms.CharField(
            widget=forms.TextInput(attrs={
                'placeholder': 'Enter article title',
                'class': 'large-input'
            })
        )
        content = forms.CharField(
            widget=forms.Textarea(attrs={
                'rows': 10,
                'placeholder': 'Write your article content here'
            })
        )

Date and Time Widgets
^^^^^^^^^^^^^^^^^^^^^

IS Core provides enhanced date/time widgets with picker functionality.

DateInput
  Date picker with calendar interface

TimeInput
  Time picker with hour/minute selection

DateTimeInput
  Combined date and time picker

SplitDateTimeWidget
  Separate inputs for date and time

Example::

    from is_core.forms.widgets import DateInput, DateTimeInput

    class ArticleForm(DjangoForm):
        published_at = forms.DateTimeField(
            widget=DateTimeInput()
        )
        deadline = forms.DateField(
            widget=DateInput(attrs={
                'data-min-date': 'today'
            })
        )

File and Image Widgets
^^^^^^^^^^^^^^^^^^^^^^

Enhanced file and image upload widgets with preview and clear functionality.

FileInput
  File upload with current file display and clear option

ClearableFileInput
  File input with explicit "clear" checkbox

ImageInput
  Image upload with thumbnail preview

Example::

    from is_core.forms.widgets import ImageInput

    class ArticleForm(DjangoForm):
        featured_image = forms.ImageField(
            widget=ImageInput(attrs={
                'accept': 'image/*'
            })
        )

**Features:**

- Thumbnail preview of current image
- "Clear" checkbox to remove existing file
- File size display
- Upload progress indication

Multiple Choice Widgets
^^^^^^^^^^^^^^^^^^^^^^^^

Enhanced widgets for handling multiple selections.

Select
  Enhanced select widget with search functionality

SelectMultiple
  Multiple selection with better UX

CheckboxSelectMultiple
  Multiple checkboxes with "select all" option

RadioSelect
  Radio button group with enhanced styling

Example::

    from django import forms

    class ArticleForm(DjangoForm):
        categories = forms.ModelMultipleChoiceField(
            queryset=Category.objects.all(),
            widget=forms.CheckboxSelectMultiple
        )
        status = forms.ChoiceField(
            choices=[
                ('draft', 'Draft'),
                ('published', 'Published'),
                ('archived', 'Archived')
            ],
            widget=forms.RadioSelect
        )

Read-only Fields
----------------

IS Core provides comprehensive support for read-only fields, allowing fields to be displayed without edit capability.

.. important::
   Unlike Django Admin, IS Core allows **any field** (including form-only fields) to be read-only, not just model fields.

Configuration
^^^^^^^^^^^^^

Read-only fields can be configured at multiple levels:

**Form level**::

    class ArticleForm(SmartModelForm):
        class Meta:
            model = Article
            readonly_fields = ('created_at', 'author', 'view_count')

**View level**::

    class ArticleDetailView(DjangoDetailFormView):
        readonly_fields = ('created_at', 'author')

        def get_readonly_fields(self, request, obj=None):
            fields = list(self.readonly_fields)
            if not request.user.is_superuser:
                fields.append('published_at')
            return fields

**Field level**::

    class ArticleForm(DjangoForm):
        created_at = forms.DateTimeField(
            widget=ReadonlyWidget(),
            required=False
        )

Read-only Widgets
^^^^^^^^^^^^^^^^^

When a field is marked as read-only, IS Core automatically uses special read-only widgets:

ReadonlyWidget
  Base read-only widget that displays the field value without input element

ReadonlyTextWidget
  Read-only display for text fields

ReadonlyDateWidget
  Formatted date display

ReadonlyURLWidget
  URL displayed as clickable link

ReadonlyFileWidget
  File name with download link

Example of read-only rendering::

    # In template, read-only fields render as:
    <div class="readonly-field">
        <label>Created At:</label>
        <div class="readonly-value">2024-01-15 14:30:00</div>
    </div>

Form Validation
---------------

IS Core forms support Django's validation system with additional features.

Field Validation
^^^^^^^^^^^^^^^^

Standard Django field validation::

    class ArticleForm(DjangoForm):
        title = forms.CharField(
            max_length=200,
            min_length=10,
            required=True
        )

        def clean_title(self):
            title = self.cleaned_data['title']
            if Article.objects.filter(title=title).exists():
                raise ValidationError('Article with this title already exists')
            return title

Form-level Validation
^^^^^^^^^^^^^^^^^^^^^

Validate multiple fields together::

    class ArticleForm(DjangoForm):
        def clean(self):
            cleaned_data = super().clean()
            start_date = cleaned_data.get('start_date')
            end_date = cleaned_data.get('end_date')

            if start_date and end_date:
                if start_date > end_date:
                    raise ValidationError(
                        'End date must be after start date'
                    )

            return cleaned_data

Model Validation
^^^^^^^^^^^^^^^^

Model-level validation is automatically included::

    # models.py
    class Article(models.Model):
        title = models.CharField(max_length=200)
        content = models.TextField()

        def clean(self):
            if self.title and self.content:
                if self.title.lower() in self.content.lower():
                    raise ValidationError(
                        'Content should not contain the title'
                    )

Custom Validators
^^^^^^^^^^^^^^^^^

Create reusable validators::

    from django.core.exceptions import ValidationError

    def validate_word_count(value):
        word_count = len(value.split())
        if word_count < 100:
            raise ValidationError(
                f'Content must be at least 100 words (currently {word_count})'
            )

    class ArticleForm(DjangoForm):
        content = forms.CharField(
            widget=forms.Textarea,
            validators=[validate_word_count]
        )

Fieldsets
---------

Organize form fields into logical groups for better UX.

Configuration::

    class ArticleDetailView(DjangoDetailFormView):
        fieldsets = (
            ('Basic Information', {
                'fields': ('title', 'author', 'status')
            }),
            ('Content', {
                'fields': ('content', 'excerpt'),
                'classes': ('wide',)
            }),
            ('Publishing', {
                'fields': ('published_at', 'featured_image'),
                'description': 'Set publishing date and featured image'
            }),
            ('Advanced', {
                'fields': ('slug', 'meta_description'),
                'classes': ('collapse',)
            })
        )

Fieldset Options
^^^^^^^^^^^^^^^^

``fields``
  Tuple of field names to include in the fieldset

``classes``
  CSS classes to apply to fieldset (e.g., 'wide', 'collapse')

``description``
  Help text displayed at the top of the fieldset

Dynamic Forms
-------------

Create forms that adapt based on user permissions or object state.

Conditional Fields
^^^^^^^^^^^^^^^^^^

Show/hide fields dynamically::

    class ArticleForm(SmartModelForm):
        def __init__(self, *args, **kwargs):
            request = kwargs.pop('request', None)
            super().__init__(*args, **kwargs)

            if request and not request.user.is_superuser:
                # Remove admin-only fields
                self.fields.pop('featured', None)
                self.fields.pop('pinned', None)

            if self.instance and self.instance.status == 'published':
                # Make certain fields read-only for published articles
                self.fields['published_at'].widget.attrs['readonly'] = True

Dynamic Choices
^^^^^^^^^^^^^^^

Update field choices based on context::

    class ArticleForm(SmartModelForm):
        def __init__(self, *args, **kwargs):
            user = kwargs.pop('user', None)
            super().__init__(*args, **kwargs)

            if user:
                # Limit author choices to user's team
                self.fields['author'].queryset = User.objects.filter(
                    team=user.team
                )

Monkey Patching on Initialization
----------------------------------

.. warning::
   IS Core modifies Django's default form widgets and fields during initialization. This is usually beneficial, but be aware if you have custom widget code.

During IS Core initialization, several Django form components are enhanced:

Widget Enhancements
^^^^^^^^^^^^^^^^^^^

**className Addition**
  All widgets automatically get appropriate CSS classes for styling

**Placeholder Support**
  Widgets that support placeholders get automatic placeholder generation from field metadata

**Date/Time Enhancements**
  Date and time widgets are replaced with enhanced picker widgets

**File/Image Improvements**
  File and image inputs get preview and clear functionality

**Multiple Choice Updates**
  Select and multiple choice widgets get search and better interaction

Model Enhancements
^^^^^^^^^^^^^^^^^^

**Relationship Display**
  Improved display of ForeignKey and ManyToManyField relationships

**URLField Enhancement**
  URLField values displayed as clickable links

**Object Naming**
  Better ``__str__`` representation for admin display

Global Defaults
^^^^^^^^^^^^^^^

**Read-only Default**
  Global default: ``readonly=False``
  Fields can be switched to read-only at render time

**Form Field Generation**
  Automatic form field generation from model fields with proper widgets

Example of monkey-patched behavior::

    # Before IS Core initialization
    class MyForm(forms.Form):
        name = forms.CharField()
        # Renders as: <input type="text" name="name">

    # After IS Core initialization
    # Same form now renders as:
    # <input type="text" name="name" class="text-input"
    #        placeholder="Enter name">

Best Practices
--------------

1. **Use SmartModelForm** for model-based forms to get automatic field generation and validation

2. **Leverage read-only fields** instead of disabling inputs for better UX

3. **Use fieldsets** to organize complex forms into logical sections

4. **Implement proper validation** at the appropriate level (field, form, or model)

5. **Make forms dynamic** when needed but keep the logic clear and maintainable

6. **Use custom widgets** for specialized input types (date pickers, file uploads, etc.)

7. **Test form validation** thoroughly, especially for complex multi-field validation
