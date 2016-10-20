# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.connector.session import ConnectorSession
from openerp.osv.expression import TRUE_LEAF

from . import common
from ..models.import_synchronizer import import_record
from ..models.stock import export_picking_done


class TestStock20(common.SetUpLengowBase20):

    def setUp(self):
        super(TestStock20, self).setUp()

    def test_export_picking_done(self):
        session = ConnectorSession.from_env(self.env)
        order_message = self.json_data['orders']['json']
        order_data = order_message['orders'][0]
        import_record(session,
                      'lengow.sale.order',
                      self.backend.id,
                      '999-2121515-6705141', order_data)
        order = self.env['sale.order'].search([('client_order_ref',
                                                '=',
                                                '999-2121515-6705141')])
        order.action_button_confirm()
        self.assertEqual(order.state, 'manual')
        picking = order.picking_ids[0]
        picking.force_assign()
        picking.do_transfer()

        self.assertEqual(len(picking.lengow_bind_ids), 1)

        jobs = self.env['queue.job'].search([TRUE_LEAF])

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs.name, 'Export Lengow Picking %s'
                         ' (Order: AMAZON-999-2121515-6705141)' % picking.name)

        with self.assertRaises(AssertionError):
            export_picking_done(session,
                                'lengow.stock.picking',
                                picking.lengow_bind_ids.id)
