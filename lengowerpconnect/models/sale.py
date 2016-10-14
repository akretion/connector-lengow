# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.connector_ecommerce.sale import ShippingLineBuilder

from .backend import lengow, lengow20
from .adapter import GenericAdapter20
from .import_synchronizer import DelayedBatchImporter
from .import_synchronizer import LengowImporter
from .import_synchronizer import LengowImportMapper

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
    lengow_total_amount = fields.Float(
        string='Lengow Total amount',
        digits_compute=dp.get_precision('Account')
    )
    lengow_total_amount_tax = fields.Float(
        string='Lengow Total amount w. tax',
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
        if not from_date:
            from_date = fields.Date.today()
        if not to_date:
            to_date = fields.Date.today()
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
        orders_data = result['statistics']['orders']['order'] or []
        order_ids = [data['order_id'] for data in orders_data]
        _logger.info('Search for lengow sale orders %s returned %s',
                     filters, order_ids)
        for order_data in orders_data:
            self._import_record(order_data['order_id'], order_data)


@lengow20
class SaleOrderMapper(LengowImportMapper):
    _model_name = 'lengow.sale.order'

    direct = [('order_id', 'client_order_ref'),
              ('order_purchase_date', 'date_order'),
              ('order_comments', 'note'),
              ('order_amount', 'lengow_total_amount'),
              ('order_tax', 'lengow_total_amount_tax')]

    children = [('cart', 'lengow_order_line_ids', 'lengow.sale.order.line'),
                ]

    def _add_shipping_line(self, map_record, values):
        record = map_record.source
        ship_amount = float(record.get('order_shipping') or 0.0)
        if not ship_amount:
            return values
        line_builder = self.unit_for(LengowShippingLineBuilder)
        line_builder.price_unit = ship_amount

        line = (0, 0, line_builder.get_line())
        values['order_line'].append(line)
        return values

    def _get_partner_id(self, partner_data):
        binding_model = 'lengow.res.partner'
        importer = self.unit_for(LengowImporter, model=binding_model)
        partner_lengow_id = importer._generate_hash_key(partner_data)
        binder = self.binder_for(binding_model)
        partner_id = binder.to_openerp(partner_lengow_id, unwrap=True)
        assert partner_id is not None, (
            "partner %s should have been imported in "
            "LengowSaleOrderImporter._import_dependencies"
            % partner_data)
        return partner_id

    @mapping
    def partner_id(self, record):
        partner_id = self._get_partner_id(record['billing_address'])
        return {'partner_id': partner_id,
                'partner_invoice_id': partner_id}

    @mapping
    def partner_shipping_id(self, record):
        partner_id = self._get_partner_id(record['delivery_address'])
        return {'partner_shipping_id': partner_id}

    @mapping
    def user_id(self, record):
        return {'user_id': False}

    @mapping
    def markeplace_id(self, record):
        return {'marketplace_id': self.options.marketplace.id or False}

    @mapping
    def project_id(self, record):
        analytic_account = self.options.marketplace.account_analytic_id
        return {'project_id': analytic_account.id or False}

    @mapping
    def fiscal_position(self, record):
        fiscal_position = self.options.marketplace.fiscal_position_id
        return {'fiscal_position': fiscal_position.id or False}

    @mapping
    def warehouse_id(self, record):
        warehouse = self.options.marketplace.warehouse_id
        return {'warehouse_id': warehouse.id or False}

    @mapping
    def payment_method_id(self, record):
        return {'payment_method_id':
                self.options.marketplace.payment_method_id.id or False}

    def finalize(self, map_record, values):
        values.setdefault('order_line', [])
        values = self._add_shipping_line(map_record, values)
        return values


@lengow20
class LengowSaleOrderImporter(LengowImporter):
    _model_name = 'lengow.sale.order'

    _base_mapper = SaleOrderMapper

    def _create_payment(self, binding):
        assert binding.payment_method_id.journal_id, (
            'No payment journal defined on payment method %s' %
            binding.payment_method_id.name)
        amount = self.lengow_record.get('order_amount')
        if amount:
            amount = float(amount)
            binding.openerp_id.automatic_payment(amount)

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        """ Convert items of the record as defined by children """
        child_records = map_record.source[from_attr]['prods']
        mapper_child = self._get_map_child_unit(model_name)
        items = mapper_child.get_items(child_records, map_record,
                                       to_attr, options=self.options)
        return items

    def _import_dependencies(self):
        record = self.lengow_record
        billing_partner_data = record['billing_address']
        self._import_dependency(False,
                                billing_partner_data,
                                'lengow.res.partner')
        delivery_partner_data = record['delivery_address']
        self._import_dependency(False,
                                delivery_partner_data,
                                'lengow.res.partner')

    def _get_market_place(self, record):
        marketplace_binder = self.binder_for('lengow.market.place')
        marketplace = marketplace_binder.to_openerp(record['marketplace'],
                                                    browse=True)
        assert marketplace, (
            "MarketPlace %s does not exists."
            % record['marketplace'])
        return marketplace

    def _create_data(self, map_record, **kwargs):
        marketplace = self._get_market_place(map_record.source)
        return super(LengowSaleOrderImporter, self)._create_data(
            map_record,
            marketplace=marketplace,
            lengow_order_id=self.lengow_id,
            **kwargs)

    def _after_import(self, binding):
        self._create_payment(binding)

    def run(self, lengow_id, lengow_data):
        # simply message structure for child mapping
        lengow_data['cart'] = lengow_data['cart']['products']['product']
        super(LengowSaleOrderImporter, self).run(lengow_id, lengow_data)


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

    @api.model
    def create(self, vals):
        lengow_order_id = vals['lengow_order_id']
        binding = self.env['lengow.sale.order'].browse(lengow_order_id)
        vals['order_id'] = binding.openerp_id.id
        return super(LengowSaleOrderLine, self).create(vals)


@lengow20
class LengowSaleOrderLineMapper(LengowImportMapper):
    _model_name = 'lengow.sale.order.line'

    direct = [('title', 'name'),
              ('quantity', 'product_uom_qty'),
              ('quantity', 'product_uos_qty'),
              ('price_unit', 'price_unit')]

    @mapping
    def lengow_order_id(self, record):
        return {'lengow_order_id': self.options.lengow_order_id}

    @mapping
    def product_id(self, record):
        binder = self.binder_for('lengow.product.product')
        product_id = binder.to_openerp(record['sku']['#text'], unwrap=True)
        assert product_id is not None, (
            "product_id %s is not binded to a Lengow catalogue")
        return {'product_id': product_id}


@lengow
class LengowShippingLineBuilder(ShippingLineBuilder):
    _model_name = 'lengow.sale.order'
