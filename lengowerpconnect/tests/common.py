# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession


class SetUpLengowBase(common.TransactionCase):
    """ Base class - Test the imports from a LEngow Mock.
    """

    def setUp(self):
        super(SetUpLengowBase, self).setUp()
        self.backend_model = self.env['lengow.backend']
        self.catalogue_model = self.env['lengow.catalogue']
        self.bind_wizard_model = self.env['lengow.product.binding.wizard']
        self.unbind_wizard_model = self.env['lengow.product.unbinding.wizard']
        self.product_bind_model = self.env['lengow.product.product']

        self.session = ConnectorSession(self.env.cr, self.env.uid,
                                        context=self.env.context)
        warehouse = self.env.ref('stock.warehouse0')
        self.backend = self.backend_model.create(
            {'name': 'Test Lengow',
             'version': '2.0',
             'location': 'http://anyurl',
             'username': 'acsone',
             'password': '42'}
        )
        self.catalogue = self.catalogue_model.create(
            {'name': 'Test Lengow Catalogue',
             'backend_id': self.backend.id,
             'product_ftp': False,
             'product_filename': 'products.csv',
             'warehouse_id': warehouse.id}
        )
