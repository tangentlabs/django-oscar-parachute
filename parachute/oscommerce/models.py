# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models


class AddressBook(models.Model):
    id = models.IntegerField(db_column='address_book_id', primary_key=True)
    customer = models.ForeignKey('Customer', db_column="customers_id", related_name='addresses')

    gender = models.CharField(db_column="entry_gender", max_length=3)
    company = models.CharField(db_column="entry_company", max_length=96, blank=True)
    firstname = models.CharField(db_column="entry_firstname", max_length=96)
    lastname = models.CharField(db_column="entry_lastname", max_length=96)
    street_address = models.CharField(db_column="entry_street_address", max_length=192)
    suburb = models.CharField(db_column="entry_suburb", max_length=96, blank=True)
    postcode = models.CharField(db_column="entry_postcode", max_length=30)
    city = models.CharField(db_column="entry_city", max_length=96)
    state = models.CharField(db_column="entry_state", max_length=96, blank=True)
    country = models.ForeignKey('Country', db_column="entry_country_id")
    zone = models.ForeignKey('Zone', db_column="entry_zone_id")

    def __unicode__(self):
        return "%s %s, %s, %s %s %s, %s" % (
            self.firstname, self.lastname,
            self.street_address,
            self.city, self.state, self.postcode,
            self.country
        )

    class Meta:
        managed=False
        db_table = u'address_book'


class Zone(models.Model):
    """ States in different countries """
    id = models.IntegerField(db_column="zone_id", primary_key=True)
    country = models.ForeignKey('Country', db_column="zone_country_id")
    code = models.CharField(db_column="zone_code", max_length=96)
    name = models.CharField(db_column="zone_name", max_length=96)

    class Meta:
        managed=False
        db_table = u'zones'


class Customer(models.Model):
    id = models.IntegerField(db_column="customers_id", primary_key=True)
    gender = models.CharField(db_column="customers_gender", max_length=3)
    firstname = models.CharField(db_column="customers_firstname", max_length=96)
    lastname = models.CharField(db_column="customers_lastname", max_length=96)
    dob = models.DateTimeField(db_column="customers_dob", )
    email = models.CharField(db_column="customers_email_address", max_length=288)
    telephone = models.CharField(db_column="customers_telephone", max_length=96)
    fax = models.CharField(db_column="customers_fax", max_length=96, blank=True)
    password = models.CharField(db_column="customers_password", max_length=120)
    newsletter = models.CharField(db_column="customers_newsletter", max_length=3, blank=True)
    view_category = models.IntegerField(db_column="customers_view_category", )

    default_address_id = models.IntegerField(
        db_column="customers_default_address_id",
        null=True, blank=True,
    )

    def __unicode__(self):
        return "%s, %s" % (self.lastname, self.firstname)

    class Meta:
        managed=False
        db_table = u'customers'


class AddressFormat(models.Model):
    id = models.IntegerField(db_column="address_format_id", primary_key=True)
    format = models.CharField(db_column="address_format", max_length=384)
    summary = models.CharField(db_column="address_summary", max_length=144)

    def __unicode__(self):
        return self.format

    class Meta:
        managed=False
        db_table = u'address_format'


class Country(models.Model):
    id = models.IntegerField(db_column="countries_id", primary_key=True)
    name = models.CharField(db_column="countries_name", max_length=192)
    iso_code_2 = models.CharField(db_column="countries_iso_code_2", max_length=6)
    iso_code_3 = models.CharField(db_column="countries_iso_code_3", max_length=9)
    address_format = models.ForeignKey('AddressFormat', db_column="address_format_id")

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.iso_code_3)

    class Meta:
        managed=False
        db_table = u'countries'


class CustomerInfo(models.Model):
    customer = models.OneToOneField(
        'Customer',
        db_column="customers_info_id",
        primary_key=True,
        related_name='info'
    )
    date_of_last_logon = models.DateTimeField(
        db_column="customers_info_date_of_last_logon",
        null=True, blank=True
    )
    number_of_logons = models.IntegerField(
        db_column="customers_info_number_of_logons",
        null=True, blank=True
    )
    date_account_created = models.DateTimeField(
        db_column="customers_info_date_account_created",
        null=True, blank=True
    )
    date_account_last_modified = models.DateTimeField(
        db_column="customers_info_date_account_last_modified",
        null=True, blank=True
    )
    global_product_notifications = models.IntegerField(
        db_column="global_product_notifications",
        null=True, blank=True
    )

    def __unicode__(self):
        return "Info for %s, %s" % (
            self.customer.lastname,
            self.customer.firstname
        )

    class Meta:
        managed=False
        db_table = u'customers_info'


class Order(models.Model):
    id = models.IntegerField(db_column="orders_id", primary_key=True)
    customer = models.ForeignKey('Customer', db_column="customers_id")
    customers_name = models.CharField(db_column="customers_name", max_length=192)
    customers_company = models.CharField(db_column="customers_company", max_length=96, blank=True)
    customers_street_address = models.CharField(max_length=192)
    customers_suburb = models.CharField(max_length=96, blank=True)
    customers_city = models.CharField(max_length=96)
    customers_postcode = models.CharField(max_length=30)
    customers_state = models.CharField(max_length=96, blank=True)
    customers_country = models.CharField(max_length=96)
    customers_telephone = models.CharField(max_length=96)
    customers_email_address = models.CharField(max_length=288)
    customers_address_format_id = models.IntegerField()

    delivery_name = models.CharField(max_length=192)
    delivery_company = models.CharField(max_length=96, blank=True)
    delivery_street_address = models.CharField(max_length=192)
    delivery_suburb = models.CharField(max_length=96, blank=True)
    delivery_city = models.CharField(max_length=96)
    delivery_postcode = models.CharField(max_length=30)
    delivery_state = models.CharField(max_length=96, blank=True)
    delivery_country = models.CharField(max_length=96)
    delivery_address_format_id = models.IntegerField()

    billing_name = models.CharField(max_length=192)
    billing_company = models.CharField(max_length=96, blank=True)
    billing_street_address = models.CharField(max_length=192)
    billing_suburb = models.CharField(max_length=96, blank=True)
    billing_city = models.CharField(max_length=96)
    billing_postcode = models.CharField(max_length=30)
    billing_state = models.CharField(max_length=96, blank=True)
    billing_country = models.CharField(max_length=96)
    billing_address_format_id = models.IntegerField()

    payment_method = models.CharField(max_length=96)

    cc_type = models.CharField(max_length=60, blank=True)
    cc_owner = models.CharField(max_length=192, blank=True)
    cc_number = models.CharField(max_length=96, blank=True)
    cc_expires = models.CharField(max_length=12, blank=True)

    last_modified = models.DateTimeField(null=True, blank=True)
    date_purchased = models.DateTimeField(null=True, blank=True)

    status = models.ForeignKey('OrderStatus', db_column="orders_status")
    date_finished = models.DateTimeField(
        db_column="orders_date_finished",
        null=True, blank=True
    )

    currency = models.CharField(max_length=9, blank=True)
    currency_value = models.DecimalField(null=True, max_digits=16, decimal_places=6, blank=True)

    def __unicode__(self):
        return 'Order #%d' % self.id

    class Meta:
        managed=False
        db_table = u'orders'


class Language(models.Model):
    id = models.IntegerField(db_column="languages_id", primary_key=True)
    name = models.CharField(max_length=96)
    code = models.CharField(max_length=6)
    image = models.CharField(max_length=192, blank=True)
    directory = models.CharField(max_length=96, blank=True)
    sort_order = models.IntegerField(null=True, blank=True)

    class Meta:
        managed=False
        db_table = u'languages'


class OrderStatus(models.Model):
    id = models.IntegerField(db_column='orders_status_id', primary_key=True)
    language = models.ForeignKey('Language', db_column="language_id")
    name = models.CharField(db_column="orders_status_name", max_length=96)

    def __unicode__(self):
        return self.name

    class Meta:
        managed=False
        db_table = u'orders_status'

################################################################################
# Unprocessed models following
################################################################################


class CustomersBasket(models.Model):
    customers_basket_id = models.IntegerField(primary_key=True)
    customers_id = models.IntegerField()
    products_id = models.TextField()
    customers_basket_quantity = models.IntegerField()
    final_price = models.DecimalField(null=True, max_digits=17, decimal_places=4, blank=True)
    customers_basket_date_added = models.CharField(max_length=24, blank=True)
    class Meta:
        managed=False
        db_table = u'customers_basket'


class CustomersBasketAttributes(models.Model):
    customers_basket_attributes_id = models.IntegerField(primary_key=True)
    customers_id = models.IntegerField()
    products_id = models.TextField()
    products_options_id = models.IntegerField()
    products_options_value_id = models.IntegerField()
    class Meta:
        managed=False
        db_table = u'customers_basket_attributes'


class CategoryDescription(models.Model):
    category = models.OneToOneField(
        'Category',
        primary_key=True,
        db_column='categories_id',
        related_name='description'
    )
    language_id = models.IntegerField(primary_key=True)
    name = models.CharField(db_column="categories_name", max_length=96)
    heading_title = models.CharField(
        db_column="categories_heading_title",
        max_length=192, blank=True
    )
    description = models.TextField(db_column="categories_description", blank=True)

    class Meta:
        managed=False
        db_table = u'categories_description'


class Category(models.Model):
    id = models.IntegerField(db_column="categories_id", primary_key=True)
    image = models.CharField(db_column="categories_image", max_length=192, blank=True)
    parent = models.ForeignKey('self', db_column="parent_id", related_name='children')

    sort_order = models.IntegerField(null=True, blank=True)
    date_added = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)

    hide = models.IntegerField(db_column="categories_hide", )
    status = models.IntegerField(db_column="categories_status", )

    @property
    def is_leaf(self):
        return bool(self.children.count() == 0)

    @property
    def is_toplevel(self):
        return bool(self.parent_id == 0)

    @property
    def tree_path(self):
        try:
            path = self.parent.tree_path
        except Category.DoesNotExist:
            path = []
        return path + [self.id]

    def __unicode__(self):
        try:
            return "%s #%d" % (self.description.name, self.id)
        except CategoryDescription.DoesNotExist:
            return 'Category #%d' % self.id

    class Meta:
        managed=False
        db_table = u'categories'


#class CbCorporateProducts(models.Model):
#    corpid = models.IntegerField(primary_key=True)
#    status = models.IntegerField()
#    name = models.CharField(max_length=765)
#    image = models.CharField(max_length=765)
#    sortorder = models.IntegerField()
#    setupcost = models.IntegerField()
#    unitbaseprice = models.FloatField()
#    unitname = models.CharField(max_length=96)
#    unitweight = models.FloatField()
#    itemname = models.CharField(max_length=96)
#    itemsperunit = models.IntegerField()
#    minimumunits = models.IntegerField()
#    unitincrements = models.IntegerField()
#    sizeoptions = models.TextField()
#    flavouroptions = models.TextField()
#    packagingoptions = models.TextField()
#    customisationoptions = models.TextField()
#    otheroptions = models.TextField()
#    description = models.TextField()
#    ingredients = models.TextField()
#    information = models.TextField()
#    class Meta:
#        managed=False
#        db_table = u'cb_corporate_products'
#
#
#class Configuration(models.Model):
#    configuration_id = models.IntegerField(primary_key=True)
#    configuration_title = models.CharField(max_length=192)
#    configuration_key = models.CharField(max_length=192)
#    configuration_value = models.CharField(max_length=765)
#    configuration_description = models.CharField(max_length=765)
#    configuration_group_id = models.IntegerField()
#    sort_order = models.IntegerField(null=True, blank=True)
#    last_modified = models.DateTimeField(null=True, blank=True)
#    date_added = models.DateTimeField()
#    use_function = models.CharField(max_length=765, blank=True)
#    set_function = models.CharField(max_length=765, blank=True)
#    class Meta:
#        managed=False
#        db_table = u'configuration'
#
#
#class ConfigurationGroup(models.Model):
#    configuration_group_id = models.IntegerField(primary_key=True)
#    configuration_group_title = models.CharField(max_length=192)
#    configuration_group_description = models.CharField(max_length=765)
#    sort_order = models.IntegerField(null=True, blank=True)
#    visible = models.IntegerField(null=True, blank=True)
#    class Meta:
#        managed=False
#        db_table = u'configuration_group'
#
#
#class Counter(models.Model):
#    startdate = models.CharField(max_length=24, blank=True)
#    counter = models.IntegerField(null=True, blank=True)
#    class Meta:
#        managed=False
#        db_table = u'counter'
#
#
#class CounterHistory(models.Model):
#    month = models.CharField(max_length=24, blank=True)
#    counter = models.IntegerField(null=True, blank=True)
#    class Meta:
#        managed=False
#        db_table = u'counter_history'
#
#
#class Currencies(models.Model):
#    currencies_id = models.IntegerField(primary_key=True)
#    title = models.CharField(max_length=96)
#    code = models.CharField(max_length=9)
#    symbol_left = models.CharField(max_length=36, blank=True)
#    symbol_right = models.CharField(max_length=36, blank=True)
#    decimal_point = models.CharField(max_length=3, blank=True)
#    thousands_point = models.CharField(max_length=3, blank=True)
#    decimal_places = models.CharField(max_length=3, blank=True)
#    value = models.FloatField(null=True, blank=True)
#    last_updated = models.DateTimeField(null=True, blank=True)
#    class Meta:
#        managed=False
#        db_table = u'currencies'
#
#
#class DiscountCoupons(models.Model):
#    coupons_id = models.CharField(max_length=96, primary_key=True)
#    coupons_description = models.CharField(max_length=192)
#    coupons_discount_amount = models.DecimalField(max_digits=17, decimal_places=12)
#    coupons_discount_type = models.CharField(max_length=24)
#    coupons_date_start = models.DateTimeField(null=True, blank=True)
#    coupons_date_end = models.DateTimeField(null=True, blank=True)
#    coupons_max_use = models.IntegerField()
#    coupons_min_order = models.DecimalField(max_digits=17, decimal_places=4)
#    coupons_min_order_type = models.CharField(max_length=24, blank=True)
#    coupons_number_available = models.IntegerField()
#    class Meta:
#        managed=False
#        db_table = u'discount_coupons'
#
#
#class DiscountCouponsToCategories(models.Model):
#    coupons_id = models.CharField(max_length=96, primary_key=True)
#    categories_id = models.IntegerField(primary_key=True)
#    class Meta:
#        managed=False
#        db_table = u'discount_coupons_to_categories'
#
#
#class DiscountCouponsToCustomers(models.Model):
#    coupons_id = models.CharField(max_length=96, primary_key=True)
#    customers_id = models.IntegerField(primary_key=True)
#    class Meta:
#        managed=False
#        db_table = u'discount_coupons_to_customers'
#
#
#class DiscountCouponsToManufacturers(models.Model):
#    coupons_id = models.CharField(max_length=96, primary_key=True)
#    manufacturers_id = models.IntegerField(primary_key=True)
#    class Meta:
#        managed=False
#        db_table = u'discount_coupons_to_manufacturers'
#
#
#class DiscountCouponsToOrders(models.Model):
#    coupons_id = models.CharField(max_length=96, primary_key=True)
#    orders_id = models.IntegerField(primary_key=True)
#    class Meta:
#        managed=False
#        db_table = u'discount_coupons_to_orders'
#
#
#class DiscountCouponsToProducts(models.Model):
#    coupons_id = models.CharField(max_length=96, primary_key=True)
#    products_id = models.IntegerField(primary_key=True)
#    class Meta:
#        managed=False
#        db_table = u'discount_coupons_to_products'
#
#
#class DiscountCouponsToZones(models.Model):
#    coupons_id = models.CharField(max_length=96, primary_key=True)
#    geo_zone_id = models.IntegerField(primary_key=True)
#    class Meta:
#        managed=False
#        db_table = u'discount_coupons_to_zones'


class Manufacturer(models.Model):
    id = models.IntegerField(db_column="manufacturers_id", primary_key=True)
    name = models.CharField(db_column="manufacturers_name", max_length=96)
    image = models.CharField(db_column="manufacturers_image", max_length=192, blank=True)
    date_added = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed=False
        db_table = u'manufacturers'


class ManufacturersInfo(models.Model):
    manufacturer = models.ForeignKey(
        "Manufacturer",
        db_column="manufacturers_id",
        primary_key=True
    )
    language = models.ForeignKey('Language', db_column="languages_id")
    url = models.CharField(db_column="manufacturers_url", max_length=765)
    url_clicked = models.IntegerField()
    date_last_click = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed=False
        unique_together = ('id', 'language')
        db_table = u'manufacturers_info'


class Newsletters(models.Model):
    newsletters_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=765)
    content = models.TextField()
    module = models.CharField(max_length=765)
    date_added = models.DateTimeField()
    date_sent = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    locked = models.IntegerField(null=True, blank=True)
    class Meta:
        managed=False
        db_table = u'newsletters'


class OrderProduct(models.Model):
    id = models.IntegerField(db_column="orders_products_id", primary_key=True)
    order = models.ForeignKey('Order', db_column="orders_id", related_name='products')
    product = models.ForeignKey('Product', db_column="products_id", related_name='order_products')
    model = models.CharField(db_column="products_model", max_length=36, blank=True)
    name = models.CharField(db_column="products_name", max_length=192)
    price = models.DecimalField(db_column="products_price", max_digits=17, decimal_places=4)
    final_price = models.DecimalField(max_digits=17, decimal_places=4)
    tax = models.DecimalField(db_column="products_tax", max_digits=9, decimal_places=4)
    quantity = models.IntegerField(db_column="products_quantity", )

    class Meta:
        managed=False
        db_table = u'orders_products'


class OrdersProductsAttributes(models.Model):
    orders_products_attributes_id = models.IntegerField(primary_key=True)
    orders_id = models.IntegerField()
    orders_products_id = models.IntegerField()
    products_options = models.CharField(max_length=96)
    products_options_values = models.CharField(max_length=96)
    options_values_price = models.DecimalField(max_digits=17, decimal_places=4)
    price_prefix = models.CharField(max_length=3)
    class Meta:
        managed=False
        db_table = u'orders_products_attributes'


class OrdersProductsDownload(models.Model):
    orders_products_download_id = models.IntegerField(primary_key=True)
    orders_id = models.IntegerField()
    orders_products_id = models.IntegerField()
    orders_products_filename = models.CharField(max_length=765)
    download_maxdays = models.IntegerField()
    download_count = models.IntegerField()
    class Meta:
        managed=False
        db_table = u'orders_products_download'


class OrdersStatusHistory(models.Model):
    orders_status_history_id = models.IntegerField(primary_key=True)
    orders_id = models.IntegerField()
    orders_status_id = models.IntegerField()
    date_added = models.DateTimeField()
    customer_notified = models.IntegerField(null=True, blank=True)
    comments = models.TextField(blank=True)
    class Meta:
        managed=False
        db_table = u'orders_status_history'


class OrderTotal(models.Model):
    id = models.IntegerField(db_column="orders_total_id", primary_key=True)
    order = models.ForeignKey('Order', db_column="orders_id", related_name='totals')
    title = models.CharField(max_length=765)
    text = models.CharField(max_length=765)
    value = models.DecimalField(max_digits=17, decimal_places=4)
    class_field = models.CharField(max_length=96, db_column='class')
    sort_order = models.IntegerField()

    class Meta:
        managed=False
        db_table = u'orders_total'


class Product(models.Model):
    id = models.IntegerField(db_column="products_id", primary_key=True)
    model = models.CharField(
        db_column="products_model",
        max_length=36, blank=True
    )

    quantity = models.IntegerField(db_column="products_quantity")

    image = models.CharField(
        db_column="products_image",
        max_length=192, blank=True
    )

    price = models.DecimalField(
        db_column="products_price",
        max_digits=17, decimal_places=4
    )

    date_added = models.DateTimeField(db_column="products_date_added")

    last_modified = models.DateTimeField(
        db_column="products_last_modified",
        null=True, blank=True
    )
    date_available = models.DateTimeField(
        db_column="products_date_available",
        null=True, blank=True
    )

    weight = models.DecimalField(
        db_column="products_weight",
        max_digits=7, decimal_places=2
    )
    status = models.IntegerField(db_column="products_status")

    tax_class_id = models.IntegerField(db_column="products_tax_class_id")

    manufacturer = models.ForeignKey(
        'Manufacturer',
        db_column="manufacturers_id",
        null=True, blank=True
    )

    ordered = models.IntegerField(db_column="products_ordered")
    sort_order = models.IntegerField(db_column="products_sort_order")

    categories = models.ManyToManyField(
        'Category',
        through='ProductsToCategories',
        related_name='products'
    )

    def __unicode__(self):
        try:
            return '%s #%d' % (self.description.name, self.id)
        except ProductDescription.DoesNotExist:
            return 'Product #%d' % self.id

    class Meta:
        managed=False
        db_table = u'products'


class ProductDescription(models.Model):
    product = models.OneToOneField(
        "Product",
        db_column="products_id",
        primary_key=True,
        related_name='description'
    )
    language = models.ForeignKey(
        "Language",
        db_column="language_id",
        related_name='languages'
    )
    name = models.CharField(db_column="products_name", max_length=192)
    description = models.TextField(db_column="products_description", blank=True)
    url = models.CharField(db_column="products_url", max_length=765, blank=True)
    viewed = models.IntegerField(db_column="products_viewed", null=True, blank=True)

    class Meta:
        unique_together = ('product', 'language')
        managed=False
        db_table = u'products_description'


class ProductAttribute(models.Model):
    id = models.IntegerField(db_column="products_attributes_id", primary_key=True)
    product = models.ForeignKey(
        "Product",
        db_column="products_id",
        related_name='attributes'
    )
    product_option = models.ForeignKey(
        "ProductOption",
        db_column="options_id"
    )
    product_option_value = models.ForeignKey(
        "ProductsOptionValues",
        db_column="options_values_id"
    )
    options_values_price = models.DecimalField(
        db_column="options_values_price",
        max_digits=17, decimal_places=4
    )
    price_prefix = models.CharField(max_length=3)

    class Meta:
        managed=False
        db_table = u'products_attributes'


class ProductsAttributesDownload(models.Model):
    id = models.IntegerField(
        db_column="products_attributes_id",
        primary_key=True
    )
    filename = models.CharField(
        db_column="products_attributes_filename",
        max_length=765
    )
    maxdays = models.IntegerField(
        db_column="products_attributes_maxdays",
        null=True, blank=True
    )
    maxcount = models.IntegerField(
        db_column="products_attributes_maxcount",
        null=True, blank=True
    )

    class Meta:
        managed=False
        db_table = u'products_attributes_download'


class ProductNotification(models.Model):
    product = models.IntegerField(
        'Product',
        db_column="products_id",
        primary_key=True
    )
    customer = models.IntegerField('Customer', db_column="customers_id")
    date_added = models.DateTimeField()

    class Meta:
        unique_together = ('product', 'customer')
        managed=False
        db_table = u'products_notifications'


class ProductOption(models.Model):
    products_options_id = models.IntegerField(primary_key=True)
    language_id = models.IntegerField(primary_key=True)
    products_options_name = models.CharField(max_length=96)

    class Meta:
        managed=False
        db_table = u'products_options'


class ProductOptionValue(models.Model):
    products_options_values_id = models.IntegerField(primary_key=True)
    language_id = models.IntegerField(primary_key=True)
    products_options_values_name = models.CharField(max_length=192)

    class Meta:
        managed=False
        db_table = u'products_options_values'


class ProductsOptionsValuesToProductsOptions(models.Model):
    products_options_values_to_products_options_id = models.IntegerField(primary_key=True)
    products_options_id = models.IntegerField()
    products_options_values_id = models.IntegerField()

    class Meta:
        managed=False
        db_table = u'products_options_values_to_products_options'


class ProductsToCategories(models.Model):
    product = models.ForeignKey("Product", db_column="products_id")
    category = models.ForeignKey("Category", db_column="categories_id")

    class Meta:
        unique_together = ('product', 'category')
        managed=False
        db_table = u'products_to_categories'


class Reviews(models.Model):
    reviews_id = models.IntegerField(primary_key=True)
    products_id = models.IntegerField()
    customers_id = models.IntegerField(null=True, blank=True)
    customers_name = models.CharField(max_length=192)
    reviews_rating = models.IntegerField(null=True, blank=True)
    date_added = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    reviews_read = models.IntegerField()
    class Meta:
        managed=False
        db_table = u'reviews'


class ReviewsDescription(models.Model):
    reviews_id = models.IntegerField(primary_key=True)
    language = models.ForeignKey('Language', db_column="languages_id", primary_key=True)
    reviews_text = models.TextField()
    class Meta:
        managed=False
        db_table = u'reviews_description'


class Sessions(models.Model):
    sesskey = models.CharField(max_length=96, primary_key=True)
    expiry = models.IntegerField()
    value = models.TextField()
    class Meta:
        managed=False
        db_table = u'sessions'


class Specials(models.Model):
    specials_id = models.IntegerField(primary_key=True)
    products_id = models.IntegerField()
    specials_new_products_price = models.DecimalField(max_digits=17, decimal_places=4)
    specials_date_added = models.DateTimeField(null=True, blank=True)
    specials_last_modified = models.DateTimeField(null=True, blank=True)
    expires_date = models.DateTimeField(null=True, blank=True)
    date_status_change = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField()
    class Meta:
        managed=False
        db_table = u'specials'


class Storelocations(models.Model):
    shopid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=765)
    sortorder = models.IntegerField()
    jobsavailable = models.IntegerField()
    phone = models.CharField(max_length=48)
    email = models.CharField(max_length=765)
    address = models.CharField(max_length=765)
    manager = models.CharField(max_length=765)
    class Meta:
        managed=False
        db_table = u'storelocations'


class TaxClass(models.Model):
    id = models.IntegerField(db_column="tax_class_id", primary_key=True)
    title = models.CharField(db_column="tax_class_title", max_length=96)
    description = models.CharField(db_column="tax_class_description", max_length=765)
    last_modified = models.DateTimeField(null=True, blank=True)
    date_added = models.DateTimeField()

    class Meta:
        managed=False
        db_table = u'tax_class'


class TaxRates(models.Model):
    id = models.IntegerField(db_column="tax_rates_id", primary_key=True)
    zone = models.ForeignKey('Zone', db_column="tax_zone_id", )
    tax_class = models.ForeignKey('TaxClass', db_column="tax_class_id", )
    priority = models.IntegerField(db_column="tax_priority", null=True, blank=True)
    rate = models.DecimalField(db_column="tax_rate", max_digits=9, decimal_places=4)
    description = models.CharField(db_column="tax_description", max_length=765)
    last_modified = models.DateTimeField(null=True, blank=True)
    date_added = models.DateTimeField()

    class Meta:
        managed=False
        db_table = u'tax_rates'


class WhosOnline(models.Model):
    customer_id = models.IntegerField(null=True, blank=True)
    full_name = models.CharField(max_length=192)
    session_id = models.CharField(max_length=384)
    ip_address = models.CharField(max_length=45)
    time_entry = models.CharField(max_length=42)
    time_last_click = models.CharField(max_length=42)
    last_page_url = models.CharField(max_length=765)
    class Meta:
        managed=False
        db_table = u'whos_online'


class ZonesToGeoZones(models.Model):
    association_id = models.IntegerField(primary_key=True)
    zone_country_id = models.IntegerField()
    zone_id = models.IntegerField(null=True, blank=True)
    geo_zone_id = models.IntegerField(null=True, blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    date_added = models.DateTimeField()
    class Meta:
        managed=False
        db_table = u'zones_to_geo_zones'
#
#
#class Banners(models.Model):
#    banners_id = models.IntegerField(primary_key=True)
#    banners_title = models.CharField(max_length=192)
#    banners_url = models.CharField(max_length=765)
#    banners_image = models.CharField(max_length=192)
#    banners_group = models.CharField(max_length=30)
#    banners_html_text = models.TextField(blank=True)
#    expires_impressions = models.IntegerField(null=True, blank=True)
#    expires_date = models.DateTimeField(null=True, blank=True)
#    date_scheduled = models.DateTimeField(null=True, blank=True)
#    date_added = models.DateTimeField()
#    date_status_change = models.DateTimeField(null=True, blank=True)
#    status = models.IntegerField()
#    class Meta:
#        managed=False
#        db_table = u'banners'
#
#
#class BannersHistory(models.Model):
#    banners_history_id = models.IntegerField(primary_key=True)
#    banners_id = models.IntegerField()
#    banners_shown = models.IntegerField()
#    banners_clicked = models.IntegerField()
#    banners_history_date = models.DateTimeField()
#    class Meta:
#        managed=False
#        db_table = u'banners_history'
#
#
#class GeoZones(models.Model):
#    id = models.IntegerField(primary_key=True)
#    name = models.CharField(max_length=96)
#    description = models.CharField(max_length=765)
#    last_modified = models.DateTimeField(null=True, blank=True)
#    date_added = models.DateTimeField()
#
#    class Meta:
#        managed=False
#        db_table = u'geo_zones'
