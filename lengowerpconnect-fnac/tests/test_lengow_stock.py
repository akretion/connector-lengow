# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock

from openerp.addons.connector.session import ConnectorSession
from openerp.osv.expression import TRUE_LEAF

from openerp.addons.lengowerpconnect.tests import common
from openerp.addons.lengowerpconnect.models.import_synchronizer import\
    import_record
from openerp.addons.lengowerpconnect.models.stock import\
    export_picking_done
from openerp.exceptions import ValidationError


class TestStock20(common.SetUpLengowBase20):

    def setUp(self):
        super(TestStock20, self).setUp()
        self.json_data.update({
            'fnac_update': {
                'status_code': 200,
                'json': {}}})
        self.session = ConnectorSession.from_env(self.env)
        order_message = self.json_data['orders']['json']
        order_data = order_message['orders'][0]
        order_data['marketplace'] = 'fnac'
        self.marketplace.write({'lengow_id': 'fnac'})
        import_record(self.session,
                      'lengow.sale.order',
                      self.backend.id,
                      '999-2121515-6705141', order_data)
        self.order = self.env['sale.order'].search([('client_order_ref',
                                                     '=',
                                                     '999-2121515-6705141')])
        self.order.action_button_confirm()
        self.picking = self.order.picking_ids[0]
        self.picking.force_assign()
        self.picking.do_transfer()
        self.post_method='openerp.addons.lengowerpconnect.models'\
                         '.stock.requests.post'

    def test_export_picking_done_no_tracking(self):
        with mock.patch(self.post_method) as mock_post:
            mock_post = self._configure_mock_request('fnac_update',
                                                     mock_post)
            with self.assertRaises(ValidationError):
                # For Fnac tracking information are mandatory
                export_picking_done(self.session,
                                    'lengow.stock.picking',
                                    self.picking.lengow_bind_ids.id)
                mock_post.assert_called_with(
                    'http://anywsdlurl/fnac/99128/999-2121515-6705141'
                    '/Shipped.xml', params={}, data={}, headers={})

    def test_export_picking_done_tracking(self):
        with mock.patch(self.post_method) as mock_post:
            mock_post = self._configure_mock_request('fnac_update',
                                                     mock_post)
            self.picking.write({'carrier_tracking_ref': 'tracking code test'})
            with self.assertRaises(ValidationError):
                # For Fnac carrier code are restricted to an allowed list
                export_picking_done(self.session,
                                    'lengow.stock.picking',
                                    self.picking.lengow_bind_ids.id)

            carrier = self.env.ref('lengowerpconnect-fnac.carrier_fnac_ups')
            self.picking.write({'carrier_id': carrier.id})

            export_picking_done(self.session,
                                    'lengow.stock.picking',
                                    self.picking.lengow_bind_ids.id)
            mock_post.assert_called_with(
                'http://anywsdlurl/fnac/99128/999-2121515-6705141'
                '/Shipped.xml',
                params={'trackingColis': 'tracking code test',
                        'transporteurColis': 'UPS'},
                data={}, headers={})
