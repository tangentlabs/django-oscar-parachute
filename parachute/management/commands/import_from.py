import logging
from optparse import make_option

from django.db.models.loading import load_app
from django.core.management.base import LabelCommand


class Command(LabelCommand):
    import_app = 'parachute'

    option_list = LabelCommand.option_list + (
        make_option('--database',
            dest='database',
            default=None,
            help='Force importer to updated existing DB entries with imported ones.'),
        make_option('--force-update',
            action='store_true',
            dest='force_update',
            default=False,
            help='Force importer to updated existing DB entries with imported ones.'),
        make_option('--import-customers',
            action='store_true',
            dest='import_customers',
            default=False,
            help='Import only the customers.'),
        make_option('--import-catalogue',
            action='store_true',
            dest='import_catalogue',
            default=False,
            help='Import only the catalogue.'),
        make_option('--import-orders',
            action='store_true',
            dest='import_orders',
            default=False,
            help='Import only the orders.'),
        make_option('--import-old-urls',
            action='store_true',
            dest='import_old_urls',
            default=False,
            help='Import the old urls of categories into url-tracker.'),
        )

    def handle_label(self, label, **options):
        platform_app = None

        logger = self._get_logger()

        logger.debug('attempting to import app: %s', label)

        try:
            load_app(label)
        except ImportError:
            logger.debug("could not import custom backend '%s'", label)
        else:
            platform_app = label

        if not platform_app:
            logger.debug('trying to import from parachute default apps')

            # import the correct app for the desired backend
            label = "%s.%s" % (self.import_app, label)
            try:
                load_app(label)
            except ImportError:
                logger.error("invalid import backend '%s' specified", label)
                return
            else:
                platform_app = label

        logger.info("succesfully loaded importer app for '%s'", platform_app)

        try:
            backend = __import__(platform_app, globals(), locals(), ['Importer'])
            importer = backend.Importer(
                force_update=options.get('force_update', False),
                verbosity=int(options.get('verbosity', logging.INFO)),
            )
        except AttributeError:
            logger.error("no importer available in backend '%s'", platform_app)
            return

        logger.debug("found importer object for '%s'", platform_app)

        importer.prepare_import(**options)

        if options.get('import_customers'):
            importer.import_customers()

        if options.get('import_catalogue'):
            importer.import_catalogue()

        if options.get('import_orders'):
            importer.import_orders()

        if options.get('import_old_urls'):
            importer.import_old_urls()

    def _get_logger(self):
        logger = logging.getLogger(__file__)
        stream = logging.StreamHandler(self.stdout)
        logger.addHandler(stream)
        logger.setLevel(logging.DEBUG)
        return logger
