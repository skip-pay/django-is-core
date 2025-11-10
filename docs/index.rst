.. django-is-core documentation master file, created by
   sphinx-quickstart on Wed Aug 26 20:27:52 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============================
Django IS Core Documentation
==============================

Django IS Core is a framework for rapid development of information systems and admin interfaces. It is similar to Django Admin but offers several key differences that justify its existence as a separate implementation.

Key Features
============

- **REST + AJAX Architecture**: Same detail/add/table views as Django Admin, but powered by REST API and AJAX for better interactivity
- **Flexible REST Resources**: Can be used to create REST-only resources without UI
- **Smart Relationships**: Foreign key links are automatically added between related objects
- **Advanced Read-only Fields**: Any field (even form-only fields) can be made read-only
- **Built-in Exports**: Add Excel, PDF, and CSV exports to any table view with zero configuration
- **Granular Permissions**: Links and actions are hidden if users lack permissions
- **Easy Customization**: Adding custom views is straightforward (unlike Django Admin)
- **Class-based Views**: Cleaner architecture using generic class-based views
- **Auto-registration**: Model administration without explicit registration
- **Smart Filtering**: UI filters respond to user typing; easy to implement custom filters
- **Token Authentication**: Built-in token-based authentication support
- **And much more...**

Project Home
------------
https://github.com/matllubos/django-is-core

Documentation
-------------
https://django-is-core.readthedocs.org/en/latest

Content
=======

.. toctree::
   :maxdepth: 2

   installation
   architecture
   cores
   views
   rests
   permissions
   forms
   filters
   utils
   menu
   elasticsearch
   dynamodb
