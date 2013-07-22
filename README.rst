Oscar Parachute
===============

The Oscar Parachute provides a management command to move import your
existing ecommerce data from existing platforms to Oscar.


Installation & Setup
--------------------

Install parachute using ``pip``::

    pip install git+https://github.com/tangentlabs/django-oscar-parachute.git#egg=django-oscar-parachute-dev


Add parachute to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'parachute',
    )

Add the database you are using to import from to your database settings::

    DATABASES = {
        'default': {
            ...
        },

        ...

        'old_database': {
            'ENGINE': 'django.contrib.gis.db.backends.mysql',
            'NAME': 'old_database',
            'USER': 'root',
            'PASSWORD': 'rootpassword',
        },
    }

Use Exsiting Importer
---------------------

Importing data into Oscar uses the ``import_from`` management command that is
part of *parachute*. Assuming you have your database settings provided in your
settings file as described above, you can simply run::

    ./manage.py import_from oscommerce --database=old_database

Alternatively, you can omit the ``--database`` argument and you will be
prompted by the importer for your database settings.

Creating Your Own Importer
--------------------------

You are using a e-commerce platform that is not (yet) supported by *parachute*
or would like to import from your own e-commerce application? Writing your
own importer is a straight forward process.

    1. Start with creating a new python module that lives in a folder where it
       can be found by ``python``. This module should contain the following
       two files: ``__init__.py`` and ``models.py``.

    2. The ``models.py`` module should contain *Django* models that allow you
        to use the Django ORM to access the import database. A good starting
        point, if you don't want to start from scratch, is::

            ./manage.py inspectdb --database=old_database > myimporter/models.py

        This will generate a model for each table and, depending on naming
        conventions in you old database, might even contain related fields
        connecting models. You might want to go through the models and make
        changes where the auto-generated models aren't accurate.

    3. Subclass the ``BaseImporter`` in your ``__init__.py`` and implement the
        importer methods as required. Each commandline argument for the
        ``import_from`` command corresponds to an import method that is called
        when the argument is specified. E.g. to be able to import the catalogue
        of your application you should overwrite::

            class MyImporter(BaseImporter):

                def import_catalogue(self):
                    # magically importing all data into Oscar's catalogue

        This will allow you to run::

            ./manage.py import_from myimporter --database=old_database --import-catalogue


Available Importers
-------------------

* OSCommerce: `OSCommerce <www.oscommerce.com>`_


.. _`OSCommerce <www.oscommerce.com>`: http://www.oscommerce.com



The ``import_from`` Command
---------------------------

``Oscar Parachute`` provides a management command ``import_from`` that
that is used to import from your database directly using the
corresponding app to your ecommerce platform, e.g. ``oscommerce``, to
access the database through the Django ORM.

The database settings can either be specified in your settings file as
an additional entry in the ``DATABASES`` dictionary and then be provided
to the command using the ``--database`` option. Alternatively, you can
just run that command without specifying any database details and you
will be asked to enter them interactively.

By default, the import process will check for existing data and ignore
data entries in the source database that can be found in the Oscar
database and would overwrite existing data. The reason for that is that
it prevent accidentally overwriting existing data, that might have been
altered at an earlier point in time. If you would like to overwrite the
data you can use the ``--force-update`` option.

The ``import_from`` command excepts additional options to restrict the
the import to certain types of data. This might cause problems due to
interdependencies e.g. between orders, products and users. The available
options are:

    * ``--import-customers``
    * ``--import-catalogue``
    * ``--import-orders``

Importing customers and the catalogue (meaning products and categories)
are not related and can be ran in arbitrary order but should always be
run **before** importing the orders. Otherwise you will loose the
connection between orders, customers and products in the Oscar database.


Contributing
============

Do the usual github dance: create a fork, create a new branch for a feature or
bug fix and open a pull request. Or just open an issue, if you find something
that's not working.


License
=======

Oscar Parachute is released under the permissive `New BSD license
<https://github.com/tangentlabs/oscar-migrator/blob/master/LICENSE>`_.
