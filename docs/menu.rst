.. _menu:

Menu Generator
==============

Django IS Core provides a flexible menu system for the admin interface. The menu generator automatically creates navigation based on registered Cores and can be customized for complex navigation structures.

.. seealso::

   :ref:`cores`
      Core classes that generate menu items

   :ref:`architecture`
      Understanding the Core registration system

Overview
--------

The menu system consists of:

- **Menu Generator**: Main class responsible for building the menu structure
- **Menu Groups**: Organized sections containing related menu items
- **Menu Items**: Individual navigation links
- **Breadcrumbs**: Hierarchical navigation trail
- **Tabs**: Section-level navigation within a Core

Default Menu Generation
-----------------------

By default, IS Core automatically generates a menu based on registered Cores.

Automatic Menu Items
^^^^^^^^^^^^^^^^^^^^

Each Core automatically creates menu items::

    class ArticleCore(UIRestCore):
        model = Article
        # Automatically creates "Articles" menu item

Menu Item Properties
^^^^^^^^^^^^^^^^^^^^

``verbose_name``
  Display name (defaults to model verbose_name_plural)

``menu_group``
  Group name for organizing menu items

``menu_url``
  URL for the menu item (defaults to list view)

``menu_order``
  Sort order within the group (default: 0)

Example::

    class ArticleCore(UIRestCore):
        model = Article
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        menu_group = 'Content'
        menu_order = 10

Disabling Menu Items
^^^^^^^^^^^^^^^^^^^^

Prevent a Core from appearing in the menu::

    class InternalCore(UIRestCore):
        model = InternalModel
        show_in_menu = False

Custom Menu Generator
---------------------

.. note::
   The default menu generator automatically creates menu items from all registered Cores. You only need a custom generator for complex navigation structures.

Create a custom menu generator for complex navigation requirements.

Basic Custom Generator
^^^^^^^^^^^^^^^^^^^^^^

::

    from is_core.menu import MenuGenerator, MenuItem

    class CustomMenuGenerator(MenuGenerator):
        def get_menu(self, request):
            menu = []

            # Dashboard
            menu.append(MenuItem(
                'dashboard',
                'Dashboard',
                url='/admin/',
                icon='dashboard'
            ))

            # Content section
            content_group = MenuGroup('content', 'Content')
            content_group.add_item(MenuItem(
                'articles',
                'Articles',
                url='/admin/articles/',
                icon='article'
            ))
            content_group.add_item(MenuItem(
                'pages',
                'Pages',
                url='/admin/pages/',
                icon='page'
            ))
            menu.append(content_group)

            return menu

Configuration::

    # settings.py
    IS_CORE_MENU_GENERATOR = 'myapp.menu.CustomMenuGenerator'

Advanced Menu Generation
^^^^^^^^^^^^^^^^^^^^^^^^

Menu with permissions and dynamic items::

    class AdvancedMenuGenerator(MenuGenerator):
        def get_menu(self, request):
            menu = []

            # Home
            menu.append(MenuItem(
                'home',
                'Home',
                url=reverse('admin:home'),
                icon='home',
                active_patterns=[r'^/admin/$']
            ))

            # Content Management (with permissions)
            if request.user.has_perm('articles.view_article'):
                content = MenuGroup('content', 'Content Management')

                if request.user.has_perm('articles.view_article'):
                    content.add_item(MenuItem(
                        'articles',
                        'Articles',
                        url=reverse('admin:article-list'),
                        icon='article',
                        badge=Article.objects.filter(status='draft').count()
                    ))

                if request.user.has_perm('pages.view_page'):
                    content.add_item(MenuItem(
                        'pages',
                        'Pages',
                        url=reverse('admin:page-list'),
                        icon='page'
                    ))

                menu.append(content)

            # Settings (superuser only)
            if request.user.is_superuser:
                settings = MenuGroup('settings', 'Settings')
                settings.add_item(MenuItem(
                    'users',
                    'Users',
                    url=reverse('admin:user-list'),
                    icon='users'
                ))
                menu.append(settings)

            return menu

Menu Items
----------

MenuItem Class
^^^^^^^^^^^^^^

Represents a single navigation link.

**Constructor:**

::

    MenuItem(
        name,              # Unique identifier
        verbose_name,      # Display text
        url,              # Target URL
        icon=None,        # Icon class/name
        active_patterns=None,  # URL patterns for active state
        css_class=None,   # Additional CSS classes
        badge=None,       # Badge number/text
        target=None       # Link target (_blank, etc.)
    )

Example::

    MenuItem(
        'articles',
        'Articles',
        url='/admin/articles/',
        icon='article',
        active_patterns=[r'^/admin/articles/'],
        badge=Article.objects.filter(status='draft').count()
    )

Active State Detection
^^^^^^^^^^^^^^^^^^^^^^

Menu items are marked as active based on current URL::

    MenuItem(
        'articles',
        'Articles',
        url='/admin/articles/',
        active_patterns=[
            r'^/admin/articles/$',
            r'^/admin/articles/\d+/',
        ]
    )

Using Core Identifiers
^^^^^^^^^^^^^^^^^^^^^^

Reference a Core directly::

    MenuItem(
        'articles',
        'Articles',
        core='myapp.cores.ArticleCore'
    )

Menu Groups
-----------

MenuGroup Class
^^^^^^^^^^^^^^^

Groups related menu items together.

**Constructor:**

::

    MenuGroup(
        name,             # Unique identifier
        verbose_name,     # Display text
        icon=None,        # Icon for the group
        css_class=None,   # Additional CSS classes
        collapsed=False   # Initial collapsed state
    )

Example::

    content_group = MenuGroup(
        'content',
        'Content Management',
        icon='folder',
        collapsed=False
    )

    content_group.add_item(MenuItem('articles', 'Articles', url='/admin/articles/'))
    content_group.add_item(MenuItem('pages', 'Pages', url='/admin/pages/'))

Nested Groups
^^^^^^^^^^^^^

Create hierarchical menu structures::

    class MenuGenerator(MenuGenerator):
        def get_menu(self, request):
            main_group = MenuGroup('main', 'Main')

            content_group = MenuGroup('content', 'Content')
            content_group.add_item(MenuItem('articles', 'Articles', url='/admin/articles/'))

            settings_group = MenuGroup('settings', 'Settings')
            settings_group.add_item(MenuItem('general', 'General', url='/admin/settings/'))

            main_group.add_item(content_group)
            main_group.add_item(settings_group)

            return [main_group]

Combining Automatic and Custom
-------------------------------

Mix automatic Core-based menu items with custom items::

    from is_core.menu import MenuGenerator

    class HybridMenuGenerator(MenuGenerator):
        def get_menu(self, request):
            # Start with automatically generated menu
            menu = super().get_menu(request)

            # Add custom dashboard at the beginning
            menu.insert(0, MenuItem(
                'dashboard',
                'Dashboard',
                url='/admin/dashboard/',
                icon='dashboard'
            ))

            # Add custom settings at the end
            if request.user.is_superuser:
                menu.append(MenuItem(
                    'settings',
                    'Settings',
                    url='/admin/settings/',
                    icon='settings'
                ))

            return menu

Filtering Automatic Menu
^^^^^^^^^^^^^^^^^^^^^^^^^

Customize which Cores appear in automatic menu::

    class FilteredMenuGenerator(MenuGenerator):
        def get_menu(self, request):
            menu = super().get_menu(request)

            # Remove items based on condition
            menu = [item for item in menu if self.should_show_item(item, request)]

            return menu

        def should_show_item(self, item, request):
            # Custom logic
            if item.name == 'internal' and not request.user.is_staff:
                return False
            return True

Submenu
-------

Create dropdown submenus for complex navigation.

Simple Submenu
^^^^^^^^^^^^^^

::

    main_item = MenuItem('content', 'Content', url='#')
    main_item.add_submenu_item(MenuItem(
        'articles',
        'Articles',
        url='/admin/articles/'
    ))
    main_item.add_submenu_item(MenuItem(
        'pages',
        'Pages',
        url='/admin/pages/'
    ))

Multi-level Submenu
^^^^^^^^^^^^^^^^^^^

::

    main = MenuItem('admin', 'Administration', url='#')

    content = MenuItem('content', 'Content', url='#')
    content.add_submenu_item(MenuItem('articles', 'Articles', url='/admin/articles/'))
    content.add_submenu_item(MenuItem('pages', 'Pages', url='/admin/pages/'))

    settings = MenuItem('settings', 'Settings', url='#')
    settings.add_submenu_item(MenuItem('general', 'General', url='/admin/settings/'))

    main.add_submenu_item(content)
    main.add_submenu_item(settings)

Breadcrumbs
-----------

Breadcrumbs show the navigation path to the current page.

Automatic Breadcrumbs
^^^^^^^^^^^^^^^^^^^^^

IS Core automatically generates breadcrumbs based on the current view::

    Home > Articles > Edit Article #42

Custom Breadcrumbs
^^^^^^^^^^^^^^^^^^

Override breadcrumbs in views::

    class ArticleDetailView(DjangoDetailFormView):
        def get_breadcrumbs(self, request, obj=None):
            breadcrumbs = [
                ('Home', reverse('admin:home')),
                ('Content', None),  # None = no link
                ('Articles', reverse('admin:article-list')),
            ]

            if obj:
                breadcrumbs.append((str(obj), None))

            return breadcrumbs

Breadcrumb Customization
^^^^^^^^^^^^^^^^^^^^^^^^

::

    from is_core.generic_views import BreadcrumbsMixin

    class CustomView(BreadcrumbsMixin, DetailView):
        def get_breadcrumbs_items(self):
            items = super().get_breadcrumbs_items()

            # Add custom item
            items.append({
                'url': reverse('custom-view'),
                'label': 'Custom Section'
            })

            return items

Tabs
----

Tabs provide section-level navigation within a Core's views.

Configuration
^^^^^^^^^^^^^

Define tabs in your Core::

    class ArticleCore(UIRestCore):
        model = Article

        def get_tabs(self, request, obj=None):
            tabs = []

            # Detail tab
            tabs.append({
                'name': 'detail',
                'verbose_name': 'Details',
                'url': self.get_detail_url(obj),
                'active': request.resolver_match.url_name == 'article-detail'
            })

            # Comments tab
            if obj:
                tabs.append({
                    'name': 'comments',
                    'verbose_name': f'Comments ({obj.comments.count()})',
                    'url': reverse('admin:article-comments', args=[obj.pk]),
                    'active': 'comments' in request.path
                })

            # History tab
            if obj:
                tabs.append({
                    'name': 'history',
                    'verbose_name': 'History',
                    'url': reverse('admin:article-history', args=[obj.pk]),
                    'active': 'history' in request.path
                })

            return tabs

Tab Properties
^^^^^^^^^^^^^^

``name``
  Unique identifier for the tab

``verbose_name``
  Display text

``url``
  Target URL

``active``
  Boolean indicating if this tab is currently active

``icon`` (optional)
  Icon class/name

``badge`` (optional)
  Badge number/text

Dynamic Tabs
^^^^^^^^^^^^

Tabs that change based on permissions or object state::

    def get_tabs(self, request, obj=None):
        tabs = [
            {
                'name': 'detail',
                'verbose_name': 'Details',
                'url': self.get_detail_url(obj),
                'active': 'detail' in request.path
            }
        ]

        # Comments tab only for published articles
        if obj and obj.status == 'published':
            tabs.append({
                'name': 'comments',
                'verbose_name': 'Comments',
                'url': reverse('admin:article-comments', args=[obj.pk]),
                'active': 'comments' in request.path
            })

        # Settings tab only for superusers
        if request.user.is_superuser:
            tabs.append({
                'name': 'settings',
                'verbose_name': 'Settings',
                'url': reverse('admin:article-settings', args=[obj.pk]),
                'active': 'settings' in request.path
            })

        return tabs

Menu CSS and Styling
---------------------

Customize menu appearance with CSS classes.

Custom CSS Classes
^^^^^^^^^^^^^^^^^^

::

    MenuItem(
        'important',
        'Important Items',
        url='/admin/important/',
        css_class='menu-item-highlight'
    )

    MenuGroup(
        'admin',
        'Administration',
        css_class='admin-group collapsed'
    )

Icons
^^^^^

Add icons to menu items::

    MenuItem(
        'articles',
        'Articles',
        url='/admin/articles/',
        icon='fa fa-newspaper'  # FontAwesome
    )

    MenuItem(
        'users',
        'Users',
        url='/admin/users/',
        icon='people'  # Material Icons
    )

Badges
^^^^^^

Display counts or notifications::

    MenuItem(
        'pending',
        'Pending Approval',
        url='/admin/pending/',
        badge=PendingItem.objects.count(),
        css_class='menu-item-notification'
    )

Best Practices
--------------

1. **Organize logically**: Group related items together in MenuGroups

2. **Use clear labels**: Menu item names should be immediately understandable

3. **Respect permissions**: Only show menu items the user has access to

4. **Keep it simple**: Avoid too many levels of nesting (2-3 max)

5. **Highlight active items**: Use active_patterns to show current location

6. **Use icons consistently**: Pick one icon set and stick with it

7. **Show context**: Use badges to display counts or notifications

8. **Test with different roles**: Verify menu appears correctly for all user types

9. **Consider mobile**: Ensure menu works well on small screens

10. **Document custom menus**: If using a custom generator, document the structure for other developers
