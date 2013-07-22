from __future__ import absolute_import

import urllib
import logging
import itertools

from getpass import getpass
from decimal import Decimal as D

from django.conf import settings
from django.core.files import File
from django.db.models import get_model
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify

from url_tracker.models import URLChangeRecord
from oscar.apps.customer.forms import generate_username

from ..base import BaseImporter


OscarUser = get_model('auth', 'user')
OscarBillingAddress = get_model('order', 'billingaddress')
OscarShippingAddress = get_model('order', 'shippingaddress')
OscarProduct = get_model('catalogue', 'product')
OscarProductImage = get_model('catalogue', 'productimage')
OscarProductClass = get_model('catalogue', 'productclass')
OscarProductAttribute = get_model('catalogue', 'productattribute')
OscarStockRecord = get_model('partner', 'stockrecord')
OscarPartner = get_model('partner', 'partner')
OscarOrder = get_model('order', 'order')
OscarLine = get_model('order', 'line')
OscarLinePrice = get_model('order', 'lineprice')
OscarCountry = get_model('address', 'country')
OscarBasket = get_model('basket', 'basket')


class Importer(BaseImporter):
    name = 'oscommerce'
    customer_mapping = {
        'customers_dob': 'date_of_birth',
        'customers_telephone': 'phone',
        'customers_fax': 'fax',
        'customers_newsletter': 'receive_newsletter',
        'customers_view_category': 'view_category',
    }
    nutrition_lookup = {
        'SF': ('Sugar free', 'boolean'),
        'DF': ('Dairy free', 'boolean'),
        'GF': ('Gluten free', 'boolean'),
        'NF': ('Nut free', 'boolean'),
        'AO': ('High in anti-oxidants', 'boolean'),
        'LF': ('Low fat', 'boolean'),
        'LC': ('Low carbohydrates', 'boolean'),
        'EF': ('Egg free', 'boolean'),

        'E:': ('Energy', 'richtext'),
        'P:': ('Protein', 'richtext'),
        'FT:': ('Fat -Total', 'richtext'),
        'FS:': ('Fat -Saturated', 'richtext'),
        'C:': ('Carbohydrate', 'richtext'),
        'Su:': ('Carbohydrate -Sugars', 'richtext'),
        'So:': ('Sodium', 'richtext'),
    }

    def import_customers(self):
        self.log.info(
            "start importing customer data from database '%s'",
            self.database
        )

        oscar_user = get_model('auth', 'user')
        oscom_customer = get_model(self.name, 'customer')

        customer_query = oscom_customer.objects.using(
            self.database
        ).select_related(
            'addresses'
        )
        for customer in customer_query.all():

            if not customer.email:
                self.log.error(
                    "cannot import user '%s' without email address",
                    customer
                )
                continue

            self.log.debug("importing customer '%s'", unicode(customer))

            email = customer.email.strip()
            try:
                user = oscar_user.objects.get(email=email)
                if not self.force_update:
                    continue
            except oscar_user.DoesNotExist:
                user = oscar_user()
                user.email = email

            username, __ = email.split('@')
            user.username = generate_username()
            user.first_name = customer.firstname
            user.last_name = customer.lastname

            user.password = self.convert_password_hash(customer.password)

            user.date_joined = customer.info.date_account_created
            if customer.info.date_of_last_logon:
                user.last_login = customer.info.date_of_last_logon
            user.save()

            profile = user.get_profile()
            for osc_field, oscar_field in self.customer_mapping.items():
                osc_value = getattr(customer, osc_field, None)
                if osc_value is not None:
                    setattr(profile, oscar_field, osc_value)

            profile.save()
            self.log.info("customer '%s' imported successfully", unicode(customer))

            oscar_user_address = get_model('address', 'useraddress')
            oscom_order = get_model(self.name, 'order')

            for address in customer.addresses.all():
                self.log.debug('creating new address in addressbook')

                country = self.get_oscar_country(address.country)

                if not address.company or address.company == address.street_address:
                    line1 = address.street_address
                    line2 = address.suburb
                    line3 = None
                else:
                    line1 = address.company
                    line2 = address.street_address
                    line3 = address.suburb

                zone_name = self.get_zone_name(address)

                is_default_address = False
                if address.id == customer.default_address_id:
                    is_default_address = True

                user_address, created = oscar_user_address.objects.get_or_create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    line1=line1,
                    line2=line2,
                    line3=line3,
                    line4=address.city,
                    state=zone_name,
                    postcode=address.postcode,
                    country=country,
                    is_default_for_shipping=is_default_address,
                    is_default_for_billing=is_default_address,
                )

                if created or self.force_update:
                    user_address.num_orders = oscom_order.objects.using(
                        self.database
                    ).filter(
                        customer=customer,
                        delivery_company=address.company or '',
                        delivery_street_address=address.street_address,
                        delivery_suburb=address.suburb or '',
                        delivery_city=address.city,
                        delivery_postcode=address.postcode,
                        delivery_country=address.country.name,
                    ).count()
                    user_address.save()

                    self.log.debug(
                        'address used %d times as shipping address',
                        user_address.num_orders
                    )

                self.log.info(
                    'address #%d added for customer %s',
                    user_address.id,
                    unicode(customer),
                )

    def import_orders(self):
        self.log.debug('starting importing orders from oscommerce')
        OscommerceOrder = get_model(self.name, 'order')
        OscommerceOrderTotal = get_model(self.name, 'ordertotal')

        current_site = Site.objects.get_current()
        old_site, __ = Site.objects.get_or_create(
            domain="oscommerce.%s" % current_site.domain,
            name="OSCommerce - %s" % current_site.name,
        )

        # prepare order model to not update 'date_placed' automatically
        # when saving order
        for field in OscarOrder._meta.fields:
            if field.name == u'date_placed':
                field.auto_add_now = False
                field.auto_now = False

        osc_orders = OscommerceOrder.objects.using(self.name).all()
        for idx, osc_order in enumerate(osc_orders):
            self.log.debug('importing order %d from %d', idx, len(osc_orders))
            try:
                order = OscarOrder.objects.get(number=osc_order.id)
                # orders cannot be updated !!!!!
                if not self.force_update:
                    continue
            except OscarOrder.MultipleObjectsReturned:
                self.log.error('too many orders with the same order number, ignoring this one')
                continue
            except OscarOrder.DoesNotExist:
                order = OscarOrder()
                order.number = osc_order.id

            try:
                shipping_cost = osc_order.totals.get(class_field='ot_shipping').value
            except OscommerceOrderTotal.DoesNotExist:
                shipping_cost = D('0')

            try:
                order_total = osc_order.totals.get(class_field='ot_total').value
            except OscommerceOrderTotal.DoesNotExist:
                order_total = D('0.00')
            except OscommerceOrderTotal.MultipleObjectsReturned:
                self.log.error('cannot get total order price, order total is ambiguous')
                continue

            try:
                user_id = OscarUser.objects.get(email=osc_order.customer.email).id
            except OscarUser.DoesNotExist:
                user_id = None

            first_name, last_name = self.get_first_last_from_name(
                osc_order.delivery_name
            )

            company = osc_order.delivery_company
            street_address = osc_order.delivery_street_address
            if not company or company == street_address:
                line1 = street_address
                line2 = osc_order.delivery_suburb
                line3 = None
            else:
                line1 = osc_order.delivery_company
                line2 = osc_order.delivery_street_address
                line3 = osc_order.delivery_suburb

            first_name, last_name = self.get_first_last_from_name(
                osc_order.delivery_name
            )
            country = self.get_oscar_country(osc_order.delivery_country)

            # create shipping address object
            shipping_address = OscarShippingAddress.objects.create(
                first_name=first_name,
                last_name=last_name,
                line1=line1,
                line2=line2,
                line3=line3,
                line4=osc_order.delivery_city,
                state=osc_order.delivery_state,
                postcode=osc_order.delivery_postcode,
                country=country,
            )

            company = osc_order.billing_company
            street_address = osc_order.billing_street_address
            if not company or company == street_address:
                line1 = street_address
                line2 = osc_order.billing_suburb
                line3 = None
            else:
                line1 = osc_order.billing_company
                line2 = osc_order.billing_street_address
                line3 = osc_order.billing_suburb

            first_name, last_name = self.get_first_last_from_name(
                osc_order.billing_name
            )
            country = self.get_oscar_country(osc_order.billing_country)

            # create billing address object
            billing_address = OscarBillingAddress.objects.create(
                first_name=first_name,
                last_name=last_name,
                line1=line1,
                line2=line2,
                line3=line3,
                line4=osc_order.billing_city,
                state=osc_order.billing_state,
                postcode=osc_order.billing_postcode,
                country=country,
            )

            order.site = old_site
            order.total_incl_tax = order_total
            order.total_excl_tax = order_total
            order.shipping_incl_tax = shipping_cost
            order.shipping_excl_tax = shipping_cost
            order.shipping_method = 'OSCommerce Delivery'
            order.status = osc_order.status.name
            order.shipping_address = shipping_address
            order.billing_address = billing_address
            order.user_id = user_id
            order.save()

            # overwriting the order date only works if it
            # has been saved before
            order.date_placed = osc_order.date_purchased
            order.save()

            assert order.date_placed == osc_order.date_purchased

            for osc_product in osc_order.products.all():
                self.add_product_to_order(order, osc_product)

            self.log.info('importing order #%d from %d', osc_order.id, len(osc_orders))

        self.log.info('Successfully imported %d orders from OSCommerce', idx)

    def add_product_to_order(self, order, osc_order_product):
        self.log.debug('adding product %d to current order', osc_order_product.id)

        try:
            try:
                osc_product = osc_order_product.product
                partner_name = osc_product.manufacturer.name
            except get_model(self.name, 'product').DoesNotExist:
                partner_name = ''
        except get_model(self.name, 'manufacturer').DoesNotExist:
            partner_name = ''

        try:
            partner = OscarPartner.objects.get(name=partner_name)
        except OscarPartner.DoesNotExist:
            partner = None

        tax = D(str(1.0)) + (osc_order_product.tax/D(str(100.0)))
        quantity = osc_order_product.quantity

        unit_price_excl_tax = osc_order_product.final_price
        unit_price_incl_tax = unit_price_excl_tax * tax

        final_price_excl_tax = quantity * unit_price_excl_tax
        final_price_incl_tax = final_price_excl_tax * tax

        product_upc = self.upc_base % osc_order_product.product_id

        try:
            product = OscarProduct.objects.get(upc=product_upc)
        except OscarProduct.DoesNotExist:
            product = None

        try:
            order_line = OscarLine._default_manager.get(
                order=order,
                partner_sku=product_upc,
            )
            if not self.force_update:
                return
        except OscarLine.DoesNotExist:
            order_line = OscarLine()
            order_line.order = order
            order_line.partner_sku = product_upc

        order_line.partner = partner
        order_line.partner_name = partner_name

        order_line.product = product
        order_line.title = osc_order_product.name
        order_line.upc = product_upc
        order_line.quantity = quantity

        order_line.line_price_excl_tax = final_price_excl_tax
        order_line.line_price_incl_tax = final_price_incl_tax
        order_line.line_price_before_discounts_excl_tax = final_price_excl_tax
        order_line.line_price_before_discounts_incl_tax = final_price_incl_tax

        order_line.unit_price_incl_tax = unit_price_incl_tax
        order_line.unit_price_excl_tax = unit_price_excl_tax
        order_line.status = osc_order_product.order.status

        order_line.save()

        try:
            line_price = OscarLinePrice._default_manager.get(order=order, line=order_line)
            if not self.force_update:
                return
        except OscarLinePrice.DoesNotExist:
            line_price = OscarLinePrice()

        line_price.order=order
        line_price.line=order_line
        line_price.quantity=quantity
        line_price.price_incl_tax=final_price_incl_tax
        line_price.price_excl_tax=final_price_excl_tax

        line_price.save()

    def import_old_urls(self):
        OscommerceCategory = get_model(self.name, 'category')

        osc_categories = OscommerceCategory.objects.using(self.name).all()
        for idx, osc_category in enumerate(osc_categories):

            osc_products = osc_category.products.all()
            if not osc_category.is_leaf or not len(osc_products):
                continue
            if len(osc_products) > 1:
                parent_upc = self.upc_base % osc_category.id
                try:
                    product = OscarProduct.objects.get(upc=parent_upc)
                except OscarProduct.DoesNotExist:
                    self.log.info(
                        "could not import category '%s' no corresponding product #%s found" % (
                            osc_category.description.heading_title,
                            parent_upc,
                        )
                    )
                    continue

                path = "_".join([str(p) for p in osc_category.tree_path])
                old_url = "/catalog/index.php?cPath=%s" % path

                record, created = URLChangeRecord.objects.get_or_create(
                    old_url=old_url,
                    new_url=product.get_absolute_url(),
                )

                if created:
                    msg = "created new URL mapping from '%s' to '%s'"
                else:
                    msg = "updated URL mapping from '%s' to '%s'"

                self.log.info(msg % (old_url, product.get_absolute_url()))

    def import_catalogue(self):
        OscommerceCategory = get_model(self.name, 'category')

        self.log.debug('starting import of catalogue')

        chocolate_pc, __ = OscarProductClass.objects.get_or_create(
            name="Chocolate", slug='chocolate'
        )

        for key, (attr, attr_type) in self.nutrition_lookup.items():
            try:
                pa = OscarProductAttribute.objects.get(name=attr)
            except OscarProductAttribute.DoesNotExist:
                pa = OscarProductAttribute.objects.create(
                    product_class=chocolate_pc,
                    name=attr,
                    code=slugify(attr).replace('-', '_'),
                    type=attr_type
                )
            self.nutrition_lookup[key] = pa

        hamper_pc, __ = OscarProductClass.objects.get_or_create(
            name="Hamper", slug='hamper'
        )

        osc_categories = OscommerceCategory.objects.using(self.name).all()
        for idx, osc_category in enumerate(osc_categories):

            # ignore all the categories that are not leafs in the category
            # tree as they are not parent products in the sense of Oscar's
            # products with variants
            osc_products = osc_category.products.all()
            if not osc_category.is_leaf or not len(osc_products):
                continue

            self.log.info('Processing parent product %d of %d', idx, len(osc_categories))

            parent = None
            if len(osc_products) > 1:
                self.log.debug('creating a parent product')

                parent_upc = self.upc_base % osc_category.id
                try:
                    parent = OscarProduct.objects.get(upc=parent_upc)
                    if not self.force_update:
                        self.log.debug("skipping product. already imported")
                        continue
                except OscarProduct.DoesNotExist:
                    parent = OscarProduct()
                    parent.upc = parent_upc

                parent.title = osc_category.description.heading_title

                if 'hamper' in parent.title.lower():
                    parent.product_class = hamper_pc
                else:
                    parent.product_class = chocolate_pc

                parent.save()

                self.update_product_details(
                    parent,
                    osc_category.description.description
                )

                if osc_category.image:
                    self.log.debug('start downloading file %s', osc_category.image)
                    image = self.get_product_image(parent, osc_category.image)
                    self.log.debug('download finished')

                    parent.images.add(image)
                    parent.save()

            size_iter = itertools.cycle(range(0, 4))

            for osc_product in osc_products.order_by('weight'):
                self.log.debug('creating new product from %s', osc_product.description.name)

                product_upc = self.upc_base % osc_product.id
                try:
                    product = OscarProduct.objects.get(upc=product_upc)
                    if not self.force_update:
                        continue
                except OscarProduct.DoesNotExist:
                    product = OscarProduct()
                    product.upc = product_upc

                product.title = osc_product.description.name

                if 'hamper' in product.title.lower():
                    product.product_class = hamper_pc
                else:
                    product.product_class = chocolate_pc

                if parent:
                    product.parent = parent
                    product.package_size = size_iter.next()

                product.save()

                if osc_product.image:
                    self.log.debug('start downloading file %s', osc_product.image)
                    image = self.get_product_image(product, osc_product.image)
                    self.log.debug('download finished')

                    product.images.add(image)
                    product.save()

                self.log.debug('created product %s', product)

                self.update_product_details(
                    product,
                    osc_product.description.description,
                    osc_product.weight,
                )

                try:
                    partner_name = osc_product.manufacturer.name
                except get_model(self.name, 'manufacturer').DoesNotExist:
                    continue

                try:
                    partner = OscarPartner.objects.get(name=partner_name)
                except OscarPartner.DoesNotExist:
                    partner = OscarPartner.objects.create(name=partner_name)

                try:
                    stockrecord = OscarStockRecord.objects.get(partner_sku=product.upc)
                    if not self.force_update:
                        continue
                except OscarStockRecord.DoesNotExist:
                    stockrecord = OscarStockRecord()
                    stockrecord.partner_sku = product.upc

                self.log.debug('adding stockrecord to product')
                stockrecord.product = product
                stockrecord.partner = partner
                stockrecord.price_excl_tax = osc_product.price
                # add 10% tax specifically for Chocolate Box
                stockrecord.price_retail = osc_product.price * D('1.1')
                stockrecord.num_in_stock = osc_product.quantity
                stockrecord.date_created = osc_product.date_added
                stockrecord.date_updated = osc_product.last_modified
                stockrecord.save()

    def update_product_details(self, product, original_description, weight=None):
        product_description = original_description.replace('\r', '')

        try:
            description, additional_data = product_description.split(
                '--INGREDIENTS--'
            )
        except ValueError:
            description, additional_data = product_description, ''

        try:
            ingredients, nutrition = additional_data.split('--NUTRITION--')
        except ValueError:
            ingredients, nutrition = None, None

        product.description = description.strip()

        if weight:
            try:
                attr = OscarProductAttribute.objects.get(code='weight')
            except OscarProductAttribute.DoesNotExist:
                attr = OscarProductAttribute.objects.create(
                    product_class=product.product_class,
                    name='Weight',
                    code='weight',
                    type='integer',
                )
            attr.save_value(product, int(weight * 1000))

        if ingredients:
            try:
                attr = OscarProductAttribute.objects.get(code='ingredients')
            except OscarProductAttribute.DoesNotExist:
                attr = OscarProductAttribute.objects.create(
                    product_class=product.product_class,
                    name='Ingredients',
                    code='ingredients',
                    type='richtext',
                )
            attr.save_value(product, ingredients.strip())

        if nutrition:
            nutrition = nutrition.strip()

            for line in nutrition.split('\n'):
                try:
                    key, value = line.split(' ')
                except ValueError:
                    continue

                key, value = key.strip(), value.strip()
                if value == 'FALSE':
                    value = False
                elif value == 'TRUE':
                    value = True

                if key in self.nutrition_lookup:
                    self.nutrition_lookup[key].save_value(
                        product,
                        value
                    )
        product.save()

    def get_first_last_from_name(self, osc_name):
        try:
            first_name, last_name = osc_name.rsplit(' ', 1)
        except ValueError:
            first_name, last_name = '', osc_name
        return first_name, last_name

    def get_zone_name(self, osc_obj, prefix=''):
        attr_name = 'zone'
        if prefix:
            attr_name = "%s_%s" % (prefix, attr_name)

        try:
            zone_name = getattr(osc_obj, attr_name).name
        except get_model(self.name, 'zone').DoesNotExist:
            zone_name = ''
        return zone_name

    def get_oscar_country(self, osc_country):
        queries = {}
        if isinstance(osc_country, basestring):
            queries['printable_name__iexact'] = osc_country
        else:
            queries['iso_3166_1_a3'] = osc_country.iso_code_3

        try:
            country = OscarCountry.objects.get(**queries)
        except OscarCountry.DoesNotExist:
            if isinstance(osc_country, basestring):
                try:
                    country = OscarCountry.objects.get(
                        printable_name__istartswith=osc_country
                    )
                except (OscarCountry.DoesNotExist,
                        OscarCountry.MultipleObjectsReturned):
                    self.log.info(
                        'cannot find country, using Fake Country instead'
                    )
                    country, created = OscarCountry.objects.get_or_create(
                        name="FAKE COUNTRY",
                        printable_name='Fake Country',
                        iso_3166_1_a2='XX',
                        iso_3166_1_a3='XXX',
                    )
                return country

            country = OscarCountry.objects.create(
                name=osc_country.name.upper(),
                printable_name=osc_country.name,
                iso_3166_1_a2=osc_country.iso_code_2,
                iso_3166_1_a3=osc_country.iso_code_3,
            )
        return country

    def get_product_image(self, product, name):
        try:
            image = OscarProductImage.objects.get(product=product)
            if not self.force_update:
                return image
        except OscarProductImage.DoesNotExist:
            image = OscarProductImage()

        image_url = self.image_base_url + name
        name, __ = urllib.urlretrieve(image_url)

        image.product = product
        image.original.save(name, File(open(name)))
        image.save()
        return image

    @classmethod
    def convert_password_hash(cls, password):
        algorithm = 'md5'
        pwhash, pwsalt = password.split(':')
        return r'%s$%s$%s' % (algorithm, pwsalt, pwhash)
