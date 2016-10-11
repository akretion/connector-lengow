# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openerp import fields, models
import openerp.addons.decimal_precision as dp
from openerp.addons.connector.unit.mapper import ImportMapper

from .backend import lengow20
from .adapter import GenericAdapter20
from .import_synchronizer import DelayedBatchImporter
from .import_synchronizer import LengowImporter

_logger = logging.getLogger(__name__)


class LengowSaleOrder(models.Model):
    _name = 'lengow.sale.order'
    _inherit = 'lengow.binding'
    _inherits = {'sale.order': 'openerp_id'}
    _description = 'Lengow Sale Order'

    openerp_id = fields.Many2one(comodel_name='sale.order',
                                 string='Sale Order',
                                 required=True,
                                 ondelete='cascade')
    lengow_order_line_ids = fields.One2many(
        comodel_name='lengow.sale.order.line',
        inverse_name='lengow_order_id',
        string='Lengow Order Lines'
    )
    total_amount = fields.Float(
        string='Total amount',
        digits_compute=dp.get_precision('Account')
    )
    total_amount_tax = fields.Float(
        string='Total amount w. tax',
        digits_compute=dp.get_precision('Account')
    )
    lengow_order_id = fields.Char(string='Lengow Order ID')
    marketplace_id = fields.Many2one(string='MarketPlace',
                                     comodel_name='lengow.market.place')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lengow_bind_ids = fields.One2many(
        comodel_name='lengow.sale.order',
        inverse_name='openerp_id',
        string='Lengow Bindings',
    )

    is_from_lengow = fields.Boolean(string='Order imported from Lengow')


@lengow20
class LengowSaleOrderAdapter(GenericAdapter20):
    _model_name = 'lengow.sale.order'
    _api = "V2/%s/%s/%s/%s/%s/commands/%s/%s/"

    def search(self, filters=None, from_date=None, to_date=None):
        id_client = self.backend_record.id_client
        id_group = filters.pop('id_group', '0')
        id_flux = filters.pop('id_flux', 'orders')
        state = filters.pop('state', 'processing')
        from_date = filters.pop('from_date', fields.Date.today())
        to_date = filters.pop('to_date', fields.Date.today())
        self._api = str(self._api % (from_date,
                                     to_date,
                                     id_client,
                                     id_group,
                                     id_flux,
                                     state,
                                     'json'))
        return super(LengowSaleOrderAdapter, self).search()


@lengow20
class SaleOrderBatchImporter(DelayedBatchImporter):
    _model_name = 'lengow.sale.order'

    def _import_record(self, record_id, record_data):
        """ Import the record directly """
        return super(SaleOrderBatchImporter, self)._import_record(
            record_id, record_data)

    def run(self, filters=None):
        """ Run the synchronization """
        if filters is None:
            filters = {}
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)
        result = self.backend_adapter.search(
            filters,
            from_date=from_date,
            to_date=to_date)
        orders_data = result['statistics']['commandes']['commande'] or []
        order_ids = [data['com_id'] for data in orders_data]
        _logger.info('Search for lengow sale orders %s returned %s',
                     filters, order_ids)
        for order_data in orders_data:
            self._import_record(order_data['com_id'], order_data)


@lengow20
class SaleOrderMapper(ImportMapper):
    _model_name = 'lengow.sale.order'

    direct = []


@lengow20
class LengowSaleOrderImporter(LengowImporter):
    _model_name = 'lengow.sale.order'

    _base_mapper = SaleOrderMapper


class LengowSaleOrderLine(models.Model):
    _name = 'lengow.sale.order.line'
    _inherit = 'lengow.binding'
    _inherits = {'sale.order.line': 'openerp_id'}
    _description = 'Lengow Sale Order Line'

    openerp_id = fields.Many2one(comodel_name='sale.order.line',
                                 string='Sale Order Line',
                                 required=True,
                                 ondelete='cascade')
    lengow_order_id = fields.Many2one(comodel_name='lengow.sale.order',
                                      string='Lengow Sale Order',
                                      required=True,
                                      ondelete='cascade',
                                      select=True)
    lengow_orderline_id = fields.Char(string='Lengow Order Line ID')
