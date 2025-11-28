Prolog
======

Django IS Core is a lightweight framework built on Django. It augments Django great design patterns and minimizes
annoying programming work. It takes best from Django-admin. ISCore provides a simple way how to build a rich
administration. It is very simlar to Django admin but there are several differences that justifies why IS Core is
created.

Features
--------

* same detail/add/table views as Django admin, but it uses REST and AJAX call to achieve it (it adds easier usage and
broaden usability)
* it can be used for creation only REST resources without UI
* models UI (add/detail) is more linked together, links between foreign keys are automatically added
* it provides more posibilities for read-only fields (e.g. the fields defined only inside form can be readonly too)
* add new custom view is for Django admin is nightmare, with IS Core is very easy
* it uses class based views, it is cleaner and changes are simplier
* add new model administration without its registration
* generated forms from models with validations
* generated REST resources from models again with validations (no code duplication)
* automatic exports to XLSX, PDF, CSV can be very simply add to a table view
* automatic filtering and sorting for list views
* pre-built reusable views and forms
* automatic CRUD views for models (with REST resources)
* authorization (token based) and permissions
* advanced permissions (e.g. a link between objects is not added to UI if a user does not have permissions to see it)
* and much more ...

Docs
----

For more details see [docs](http://django-is-core.readthedocs.org/)


Development Setup
-----------------

All development (running tests, building docs, etc.) is done through the **example application**. The example app's virtual environment includes django-is-core installed in editable mode along with all required dependencies.

### Prerequisites

- Python 3
- `virtualenv` command available
- Docker (for running required services)

### Setting Up the Development Environment

1. Navigate to the example directory:
   ```bash
   cd example
   ```

2. Start the required Docker services (Elasticsearch and DynamoDB):
   ```bash
   make runservices
   ```

3. Install and set up the application:
   ```bash
   make install
   ```

   This will:
   - Create a virtual environment at `example/var/ve`
   - Install django-is-core in editable mode (from the parent directory)
   - Install all dependencies (Django, test tools, etc.)
   - Initialize the database
   - Set up logging directories

4. Activate the virtual environment:
   ```bash
   source var/ve/bin/activate
   ```

### Running Tests

With the virtual environment activated:

```bash
cd example
make test
```

### Running the Example Application

```bash
cd example
make runserver
```

The application will be available at http://localhost:8080

### Stopping Services

When done, stop the Docker services:

```bash
make stopservices
```

### Other Useful Commands

From the `example` directory:

```bash
make clean          # Remove Python bytecode files
make resetdb        # Reset the database
make showurls       # Display all registered URLs
```

Building Documentation
----------------------

Documentation requires the example app's virtual environment since it uses autodoc to generate API documentation from the django-is-core source code.

1. First, set up the development environment (see above)

2. Install documentation dependencies:
   ```bash
   source example/var/ve/bin/activate
   pip install sphinx sphinx_rtd_theme
   ```

3. Build the HTML documentation:
   ```bash
   cd docs
   make html
   ```

4. View the documentation by opening `docs/.build/html/index.html` in your browser, or serve it locally:
   ```bash
   python -m http.server 8000 --directory .build/html
   ```
   Then visit http://localhost:8000


Contribution
------------