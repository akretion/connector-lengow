# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock

from . import common
from openerp.addons.connector.session import ConnectorSession
from openerp.osv.expression import TRUE_LEAF

from ..models.connector import get_environment
from ..models.sale import SaleOrderBatchImporter


class TestImportSaleOrders20(common.SetUpLengowBase20):
    ''' Test form sale orders with API 2.0'''

    def setUp(self):
        super(TestImportSaleOrders20, self).setUp()

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
                'http://anyurl/V2/2016-10-11/2016-10-11/'
                'a4a506440102b8d06a0f63fdd1eadd5f/0/orders/'
                'commands/processing/json/',
                data={},
                params={},
                headers={})
            jobs = self.env['queue.job'].search([TRUE_LEAF])

            self.assertEqual(len(jobs), 2)
            job_names = [job.name for job in jobs]
            self.assertIn('Import lengow.sale.order 5541-2121515-6705141'
                          ' from Lengow Backend Test Lengow', job_names)
            self.assertIn('Import lengow.sale.order 99924234'
                          ' from Lengow Backend Test Lengow', job_names)
