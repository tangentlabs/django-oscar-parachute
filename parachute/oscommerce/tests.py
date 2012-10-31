from django.test import TestCase

from importer.oscommerce import Importer


class ImportCustomerTests(TestCase):

    def test_convert_password_hash(self):
        osc_hash = 'ae1279a659dd4d21652517b1d7e3bdf3:6d'
        new_hash = Importer.convert_password_hash(osc_hash)

        self.assertEquals(new_hash, "md5$6d$ae1279a659dd4d21652517b1d7e3bdf3")

