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
