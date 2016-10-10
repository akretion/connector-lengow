# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession


class SetUpLengowBase(common.TransactionCase):
    """ Base class - Test the imports from a Lengow Mock.
    """
    def _configure_mock_request(self, key, mock_request):
        data = {
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


class SetUpLengowBase20(SetUpLengowBase):

    def setUp(self):
        super(SetUpLengowBase20, self).setUp()
        self.backend = self.backend_model.create(
            {'name': 'Test Lengow',
             'version': '2.0',
             'location': 'http://anyurl',
             'access_token': 'a4a506440102b8d06a0f63fdd1eadd5f',
             'secret': '66eb2d56a4e930b0e12193b954d6b2e4',
             'warehouse_id': self.warehouse.id}
        )

        self.catalogue = self.catalogue_model.create(
            {'name': 'Test Lengow Catalogue',
             'backend_id': self.backend.id,
             'product_ftp': False,
             'product_filename': 'products.csv',
             'warehouse_id': self.warehouse.id})


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
