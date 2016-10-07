# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp

from .backend import lengow
from .adapter import GenericAdapter


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


@lengow
class LengowSaleOrderAdapter(GenericAdapter):
    _model_name = 'lengow.msale.order'
    _api = "v3.0/marketplaces/"

    def search(self, params, with_account=False):
        return super(LengowSaleOrderAdapter, self).search(params)


class LengowSaleOrderLine(models.Model):
    _name = 'lengow.sale.order'
    _inherit = 'lengow.binding'
    _inherits = {'sale.order': 'openerp_id'}
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
