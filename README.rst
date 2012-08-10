Oscar Migrator
==============

The Oscar Migrator provides a management command to move import your
existing ecommerce data from existing platforms to Oscar. 

The Basic
---------

``Oscar Migrator`` provides a management command ``import_from`` that
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

OSCommerce
----------

Website: `OSCommerce <www.oscommerce.com>`_



Contributing
============

Fork it and change it. 

License
=======

Oscar Migrator is released under the permissive `New BSD license
<https://github.com/tangentlabs/oscar-migrator/blob/master/LICENSE>`_.
