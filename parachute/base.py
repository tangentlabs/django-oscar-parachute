import logging

from getpass import getpass

from django.conf import settings
from django.db.models import get_model


class BaseImporter(object):
    customer_mapping = {
        'customers_dob': 'date_of_birth',
        'customers_telephone': 'phone',
        'customers_fax': 'fax',
        'customers_newsletter': 'receive_newsletter',
        'customers_view_category': 'view_category',
    }
    upc_base = "1%05d"
    image_base_url = "https://example.com"

    def __init__(self, app_name, force_update=False, verbosity=0):
        self.name = app_name
        self.log = logging.getLogger(self.name)
        self.log.addHandler(logging.StreamHandler())

        if verbosity > 0:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)

        self.force_update = force_update

        self.prepare_mappings()

    def get_import_model(self, model_name):
        """
        Convenience function to retrieve a model from the app to be imported
        and set the import database as the default to be used with the
        model manager.

        Returns The class of the model specified in *model_name*
        """
        model = get_model(self.name, model_name)
        model.objects = model.objects.db_manager(using=self.name)
        return model

    def prepare_mappings(self):
        #TODO load user data
        default_mapping = self.customer_mapping
        self.customer_mapping = {}
        for key, value in default_mapping.items():
            key = key.replace('customers_', '')
            self.customer_mapping[key] = value

    def prepare_import(self, **options):
        self.database = options.get('database', None)

        if self.database:
            ## a profile should be defined in settings
            return

        self.database = self.name
        if self.database not in settings.DATABASES:
            settings.DATABASES[self.database] = {}

        db_profile = settings.DATABASES[self.database]

        engine = options.get('engine', None)
        if not engine:
            engine = raw_input('Please enter the DB backend [mysql]: ')
            db_profile['ENGINE'] = 'django.db.backends.%s' % (engine or 'mysql')

        hostname = options.get('host', None)
        if not hostname:
            hostname = raw_input('Please enter the DB hostname [localhost]: ')
            db_profile['HOST'] = hostname or ''

        port = options.get('port', None)
        if not port:
            port = raw_input('Please enter the DB port [3306]: ')
            db_profile['PORT'] = hostname or ''

        name = options.get('name', None)
        if not name:
            name = raw_input('Please enter the DB name: ')
            db_profile['NAME'] = name

        user = options.get('user', None)
        if not user:
            user = raw_input('Please enter the DB user: ')
            db_profile['USER'] = user

        password = options.get('password', None)
        if not password:
            password = getpass('Please enter the DB password (will not be displayed): ')
            db_profile['PASSWORD'] = password

    def import_customers(self):
        raise NotImplementedError()

    def import_orders(self):
        raise NotImplementedError()

    def import_catalogue(self):
        raise NotImplementedError()

    def convert_password_hash(self, password):
        raise NotImplementedError()
