# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock

from . import common
from openerp.addons.connector.session import ConnectorSession
from openerp.osv.expression import TRUE_LEAF

from ..models.connector import get_environment
from ..models.sale import SaleOrderBatchImporter
from ..models.import_synchronizer import import_record


class TestImportSaleOrders20(common.SetUpLengowBase20):
    ''' Test form sale orders with API 2.0'''

    def setUp(self):
        super(TestImportSaleOrders20, self).setUp()

        bind_wizard = self.bind_wizard_model.create(
            {'catalogue_id': self.catalogue.id,
             'product_ids': [(6, 0, [self.product1.id, self.product2.id])]})
        bind_wizard.bind_products()

        catalogue = self.catalogue_model.create(
            {'name': 'Test Lengow Catalogue 2',
             'backend_id': self.backend.id,
             'product_ftp': False,
             'product_filename': 'products2.csv',
             'warehouse_id': self.warehouse.id})
        bind_wizard = self.bind_wizard_model.create(
            {'catalogue_id': catalogue.id,
             'product_ids': [(6, 0, [self.product1.id, self.product2.id])]})
        bind_wizard.bind_products()

    def test_import_sale_orders(self):
        with mock.patch(self.get_method) as mock_get:
            # mock get request for orders data
            mock_get = self._configure_mock_request('orders', mock_get)
            env = get_environment(ConnectorSession.from_env(self.env),
                                  'lengow.sale.order', self.backend.id)
            importer = SaleOrderBatchImporter(env)
            importer.run(filters={'from_date': '2016-10-01',
                                  'to_date': '2016-10-01'})
            mock_get.assert_called_with(
                'http://anyurl/V2/2016-10-01/2016-10-01/'
                'a4a506440102b8d06a0f63fdd1eadd5f/0/orders/'
                'commands/processing/json/',
                data={},
                params={},
                headers={})
            jobs = self.env['queue.job'].search([TRUE_LEAF])

            self.assertEqual(len(jobs), 1)
            job_names = [job.name for job in jobs]
            self.assertIn('Import lengow.sale.order 999-2121515-6705141'
                          ' from Lengow Backend Test Lengow', job_names)

    def test_import_sale_order(self):
        session = ConnectorSession.from_env(self.env)
        import_record(session,
                      'lengow.sale.order',
                      self.backend.id,
                      '999-2121515-6705141',
                      {"marketplace": "amazon",
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
                       "order_amount": "305.65",
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
                                   "idLengow": "9999_33543",
                                   "idMP": "9999_33543",
                                   "sku": {
                                        "-field": "ID_PRODUCT",
                                        "#text": "9999_33543"
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
                                   "quantity": "2",
                                   "price": "199.8",
                                   "price_unit": "99.90"
                               }, {
                                   "idLengow": "9999_33544",
                                   "idMP": "9999_33544",
                                   "sku": {
                                       "-field": "ID_PRODUCT",
                                       "#text": "9999_33544"
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
                                                "img/p/11199-42102-"
                                                "large.jpg",
                                   "quantity": "1",
                                   "price": "99.95",
                                   "price_unit": "99.95"}]}}})

        order = self.env['lengow.sale.order'].search([('client_order_ref',
                                                       '=',
                                                       '999-2121515-6705141')])
        self.assertEqual(len(order), 1)

        # check partner linked
        self.assertEqual(order.partner_id.name, 'Lengow')
        self.assertEqual(order.partner_id.id, order.partner_shipping_id.id)

        # order should not be assigned to a vendor
        self.assertFalse(order.user_id)

        # order should be linked to the right marketplace
        self.assertEqual(order.marketplace_id.id, self.marketplace.id)

        # order should be assigned to analytic for Amazon
        self.assertEqual(order.project_id.id, self.amazon_analytic.id)

        # order should have 2 order lines and one shipping cost line
        self.assertEqual(len(order.order_line), 3)

        # check amount total
        self.assertEqual(order.lengow_total_amount, 305.65)
        self.assertAlmostEqual(order.lengow_total_amount, order.amount_total)

        # check order lines
        order_line = order.order_line[0]
        self.assertEqual(order_line.product_id.id, self.product1.id)
        self.assertEqual(order_line.name, "Pantalon G-star rovic"
                                          " slim, micro stretch "
                                          "twill GS Dk Fig Taille W29/L32")
        self.assertEqual(order_line.product_uom_qty, 2)
        self.assertEqual(order_line.price_unit, 99.90)
        self.assertEqual(order_line.price_subtotal, 199.8)

        order_line = order.order_line[1]
        self.assertEqual(order_line.product_id.id, self.product2.id)
        self.assertEqual(order_line.name, "Pantalon G-star rovic"
                                          " slim, micro stretch "
                                          "twill GS Dk Fig Taille W30/L33")
        self.assertEqual(order_line.product_uom_qty, 1)
        self.assertEqual(order_line.price_unit, 99.95)
        self.assertEqual(order_line.price_subtotal, 99.95)

        order_line = order.order_line[2]
        self.assertEqual(order_line.product_id.id,
                         self.env.ref('connector_ecommerce.'
                                      'product_product_shipping').id)
        self.assertEqual(order_line.name, "Shipping costs")
        self.assertEqual(order_line.product_uom_qty, 1)
        self.assertEqual(order_line.price_unit, 5.9)
        self.assertEqual(order_line.price_subtotal, 5.9)
