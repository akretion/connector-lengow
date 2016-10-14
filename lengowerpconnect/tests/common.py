# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession


class SetUpLengowBase(common.TransactionCase):
    """ Base class - Test the imports from a Lengow Mock.
    """

    def _configure_mock_request(self, key, mock_request):
        data = self.json_data
        mock_request.return_value.status_code = data[key]['status_code']
        mock_request.return_value.json.return_value = data[key]['json']
        return mock_request

    def setUp(self):
        super(SetUpLengowBase, self).setUp()
        self.backend_model = self.env['lengow.backend']
        self.catalogue_model = self.env['lengow.catalogue']
        self.marketplace_model = self.env['lengow.market.place']
        self.bind_wizard_model = self.env['lengow.product.binding.wizard']
        self.unbind_wizard_model = self.env['lengow.product.unbinding.wizard']
        self.product_bind_model = self.env['lengow.product.product']

        self.session = ConnectorSession(self.env.cr, self.env.uid,
                                        context=self.env.context)
        self.warehouse = self.env.ref('stock.warehouse0')
        self.post_method = 'openerp.addons.lengowerpconnect.models'\
                           '.adapter.requests.post'
        self.get_method = 'openerp.addons.lengowerpconnect.models'\
                          '.adapter.requests.get'
        self.json_data = {}


class SetUpLengowBase20(SetUpLengowBase):

    def setUp(self):
        super(SetUpLengowBase20, self).setUp()

        self.backend = self.backend_model.create(
            {'name': 'Test Lengow',
             'version': '2.0',
             'location': 'http://anyurl',
             'id_client': 'a4a506440102b8d06a0f63fdd1eadd5f',
             'warehouse_id': self.warehouse.id}
        )

        self.amazon_analytic = self.env['account.analytic.account'].create(
            {'name': 'Amazon Sales',
             'type': 'normal'})

        self.marketplace = self.marketplace_model.create(
            {'backend_id': self.backend.id,
             'name': 'Amazon',
             'lengow_id': 'amazon',
             'specific_account_analytic_id': self.amazon_analytic.id
             })

        self.catalogue = self.catalogue_model.create(
            {'name': 'Test Lengow Catalogue',
             'backend_id': self.backend.id,
             'product_ftp': False,
             'product_filename': 'products.csv',
             'warehouse_id': self.warehouse.id})

        self.json_data = {
            'orders': {
                'status_code': 200,
                'json': {
                    "statistics": {
                        "-ip": "127.0.0.1",
                        "-timeGenerated": "2013-09-16 12:00:00.120000",
                        "parsererror": {
                            "-style": "display: block; white-space: pre;"
                            " border: 2px solid #c77; padding: 0 1em 0 1em;"
                            " margin: 1em; background-color:"
                            " #fdd; color: black",
                            "h3": ["This page contains the following errors:",
                                   "Below is a rendering of the page up to the"
                                   " first error."],
                            "div": {
                                "-style": "font-family:monospace;"
                                          "font-size:12px",
                                "#text": "error on line 243 at column 5:"
                                         " error parsing attribute name"}
                        },
                        "orders_count": {
                            "count_total": "435",
                            "count_by_marketplace": {
                                "spartoo": "33",
                                "amazon": "287",
                                "cdiscount": "110",
                                "rueducommerce": "4",
                                "priceminister": "1"
                            },
                            "count_by_status": {
                                "cancel": "4",
                                "new": "0",
                                "shipped": "414",
                                "processing": "17"
                            }
                        },
                        "orders": {
                            "order": [{
                                "marketplace": "amazon",
                                "idFlux": "99128",
                                "order_status": {
                                    "marketplace": "accept",
                                    "lengow": "processing"
                                },
                                "order_id": "999-2121515-6705141",
                                "order_mrid": "999-2121515-6705141",
                                "order_refid": "999-2121515-6705141",
                                "order_external_id": "99341",
                                "order_purchase_date": "2016-10-01",
                                "order_purchase_heure": "04:51:24",
                                "order_amount": "105.85",
                                "order_tax": "0.00",
                                "order_shipping": "5.9",
                                "order_commission": "0.0",
                                "order_processing_fee": "0",
                                "order_currency": "EUR",
                                "order_payment": {
                                    "payment_checkout": "",
                                    "payment_status": "",
                                    "payment_type": "",
                                    "payment_date": "2016-10-01",
                                    "payment_heure": "04:51:24"
                                },
                                "order_invoice": {
                                    "invoice_number": "",
                                    "invoice_url": ""
                                },
                                "billing_address": {
                                    "billing_society": "",
                                    "billing_civility": "",
                                    "billing_lastname": "Lengow",
                                    "billing_firstname": "",
                                    "billing_email": "Lengow@marketplace."
                                                     "amazon.de",
                                    "billing_address": "Lengow",
                                    "billing_address_2": "",
                                    "billing_address_complement": "Lengow",
                                    "billing_zipcode": "44000",
                                    "billing_city": "Nantes",
                                    "billing_country": "FR",
                                    "billing_country_iso": "FR",
                                    "billing_phone_home": "099999689492",
                                    "billing_phone_office": "",
                                    "billing_phone_mobile": "",
                                    "billing_full_address": "Lengow"
                                },
                                "delivery_address": {
                                    "delivery_society": "",
                                    "delivery_civility": "",
                                    "delivery_lastname": "Lengow",
                                    "delivery_firstname": "",
                                    "delivery_email": "",
                                    "delivery_address": "Lengow",
                                    "delivery_address_2": "",
                                    "delivery_address_complement": "Lengow",
                                    "delivery_zipcode": "44000",
                                    "delivery_city": "Nantes",
                                    "delivery_country": "FR",
                                    "delivery_country_iso": "FR",
                                    "delivery_phone_home": "099999689492",
                                    "delivery_phone_office": "",
                                    "delivery_phone_mobile": "",
                                    "delivery_full_address": "Lengow"
                                },
                                "tracking_informations": {
                                    "tracking_method": "",
                                    "tracking_carrier": "Standard",
                                    "tracking_number": "",
                                    "tracking_url": "",
                                    "tracking_shipped_date": "2016-10-01"
                                                             " 09:32:16",
                                    "tracking_relay": "",
                                    "tracking_deliveringByMarketPlace": "0",
                                    "tracking_parcel_weight": ""
                                },
                                "order_comments": "",
                                "customer_id": "",
                                "order_ip": "",
                                "order_items": "1",
                                "cart": {
                                    "nb_orders": "1",
                                    "products": {
                                        "product": [{
                                            "idLengow": "9999_33544",
                                            "idMP": "9999_33544",
                                            "sku": {
                                                 "-field": "ID_PRODUCT",
                                                 "#text": "9999_33544"
                                            },
                                            "title": "Pantalon G-star rovic"
                                                     " slim, micro stretch "
                                                     "twill GS Dk Fig Taille "
                                                     "W29/L32",
                                            "category": "Accueil > HOMME > "
                                                        "JEANS/PANTALONS > "
                                                        "PANTALONS",
                                            "url_product": "http://lengow.com"
                                                           "/product.php?id\\"
                                                           "_product=11199",
                                            "url_image": "http://lengow.com/"
                                                         "img/p/11199-42104-"
                                                         "large.jpg",
                                            "quantity": "1",
                                            "price": "99.95",
                                            "price_unit": "99.95"},
                                            {
                                            "idLengow": "9999_33543",
                                            "idMP": "9999_33543",
                                            "sku": {
                                                "-field": "ID_PRODUCT",
                                                "#text": "9999_33543"
                                            },
                                            "title": "Pantalon G-star rovic"
                                                     " slim, micro stretch "
                                                     "twill GS Dk Fig Taille "
                                                     "W30/L33",
                                            "category": "Accueil > HOMME > "
                                                        "JEANS/PANTALONS > "
                                                        "PANTALONS",
                                            "url_product": "http://lengow.com"
                                                           "/product.php?id\\"
                                                           "_product=11198",
                                            "url_image": "http://lengow.com/"
                                                         "img/p/11199-42108-"
                                                         "large.jpg",
                                            "quantity": "2",
                                            "price": "99.95",
                                            "price_unit": "99.95"
                                        }]
                                    }
                                }
                            }]
                        }
                    }
                }}}
        self.product1 = self.env.ref('product.product_product_35')
        self.product2 = self.env.ref('product.product_product_36')


class SetUpLengowBase30(SetUpLengowBase):

    def setUp(self):
        super(SetUpLengowBase30, self).setUp()
        self.backend = self.backend_model.create(
            {'name': 'Test Lengow',
             'version': '3.0',
             'location': 'http://anyurl',
             'access_token': 'a4a506440102b8d06a0f63fdd1eadd5f',
             'secret': '66eb2d56a4e930b0e12193b954d6b2e4',
             'warehouse_id': self.warehouse.id}
        )
        self.expected_token = "6b7280eb-e7d4-4b94-a829-7b3853a20126"
        self.expected_user = "1"
        self.expected_account = 1
        self.json_data = {
            'token': {
                'status_code': 200,
                'json': {
                    'token': self.expected_token,
                    'user_id': self.expected_user,
                    'account_id': self.expected_account}},
            'token_fail': {
                'status_code': 400,
                'json': {
                    "error": {
                        "code": 403,
                        "message": "Forbidden"}}},
            'marketplace': {
                'status_code': 200,
                'json': {
                    'admarkt': {
                        'country': 'NLD',
                        'description': 'Admarkt is a Dutch marketplace which'
                                       ' lets you generate qualified traffic'
                                       ' to your online shop.',
                        'homepage': 'http://www.marktplaatszakelijk.nl/'
                                    'admarkt/',
                        'logo': 'cdn/partners//_.jpeg',
                        'name': 'Admarkt',
                        'orders': {'actions': {},
                                   'carriers': {},
                                   'status': {}}},
                    'amazon_fr': {
                        'country': 'FRA',
                        'description': 'Coming soon : description',
                        'homepage': 'http://www.amazon.com/',
                        'logo': 'http://psp-img.gamergen.com/'
                                'amazon-fr-logo_027200C800342974.jpg',
                        'name': 'Amazon FR',
                        'orders': {
                            'actions': {
                                'accept': {
                                    'args': [],
                                    'optional_args': [],
                                    'status': ['new']},
                                'cancel': {
                                    'args': ['cancel_reason'],
                                    'optional_args': [],
                                    'status': ['new',
                                               'waiting_shipment',
                                               'shipped']},
                                'partially_cancel': {
                                    'args': ['line', 'cancel_reason'],
                                    'optional_args': [],
                                    'status': ['new',
                                               'waiting_shipment']},
                                'partially_refund': {
                                    'args': ['line', 'refund_reason'],
                                    'optional_args': [],
                                    'status': ['shipped']},
                                'ship': {
                                    'args': [],
                                    'optional_args': ['line',
                                                      'shipping_date',
                                                      'carrier',
                                                      'tracking_number',
                                                      'shipping_method'],
                                    'status': ['waiting_shipment']}},
                            'carriers': {},
                            'status': {
                                'canceled': ['Canceled'],
                                'new': ['PendingAvailability', 'Pending'],
                                'shipped': ['Shipped', 'InvoiceUnconfirmed'],
                                'waiting_shipment': ['Unshipped',
                                                     'PartiallyShipped',
                                                     'Unfulfillable']}}}}}}
