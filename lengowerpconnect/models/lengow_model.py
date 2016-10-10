# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
from openerp.exceptions import Warning
from openerp.addons.connector.unit.mapper import ImportMapper
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.connector.session import ConnectorSession

from .backend import lengow, lengow30
from .adapter import GenericAdapter
from .import_synchronizer import import_batch
from .import_synchronizer import DirectBatchImporter
from .import_synchronizer import LengowImporter


_logger = logging.getLogger(__name__)


class LengowBackend(models.Model):
    _name = 'lengow.backend'
    _description = 'Lengow Backend'
    _inherit = 'connector.backend'

    _backend_type = 'lengow'

    @api.model
    def select_versions(self):
        """ Available versions in the backend.

        Can be inherited to add custom versions.  Using this method
        to add a version from an ``_inherit`` does not constrain
        to redefine the ``version`` field in the ``_inherit`` model.
        """
        return [('2.0', '2.0'), ('3.0', '3.0')]

    version = fields.Selection(selection='select_versions', required=True)
    location = fields.Char(
        string='Location',
        required=True,
        help="Url to Lengow application",
    )
    access_token = fields.Char(
        string='Access Token',
        help="WebService Access Token",
    )
    secret = fields.Char(
        string='Secret',
        help="Webservice password",
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda x: x._get_default_company(),
        required=True
    )
    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic account',
        help='If specified, this analytic account will be used to fill the '
        'field  on the sale order created by the connector. The value can '
        'also be specified on the marketplace.'
    )
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Fiscal position',
        help='If specified, this fiscal position will be used to fill the '
        'field fiscal position on the sale order created by the connector.'
        'The value can also be specified on the marketplace.'
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        required=True,
        help='If specified, this warehouse will be used to fill the '
        'field warehouse on the sale order created by the connector.'
        'The value can also be specified on the marketplace.',
    )
    catalogue_ids = fields.One2many(string='Catalogue',
                                    comodel_name='lengow.catalogue',
                                    inverse_name='backend_id')
    binded_products_count = fields.Float(compute='_count_binded_products')
    id_client = fields.Char('Lengow Id Client')

    def _count_binded_products(self):
        for catalogue in self.catalogue_ids:
            self.binded_products_count += catalogue.binded_products_count

    def _get_default_company(self):
        return self.env.user.company_id

    @api.multi
    def synchronize_metadata(self):
        try:
            session = ConnectorSession.from_env(self.env)
            for backend in self:
                for model in ['lengow.market.place', ]:
                    import_batch(session, model, backend.id)
            return True
        except Exception as e:
            _logger.error(e.message, exc_info=True)
            raise Warning(
                _(u"Check your configuration, we can't get the data. "
                  u"Here is the error:\n%s") %
                str(e).decode('utf-8', 'ignore'))


class LengowCatalogue(models.Model):
    _name = 'lengow.catalogue'
    _description = 'Lengow Catalogue'

    backend_id = fields.Many2one(string='Lengow Backend',
                                 comodel_name='lengow.backend',
                                 required=True)

    name = fields.Char(string='Name')

    default_lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Default Language',
        help="This the default language used to export products, if nothing"
             "is specified, the language of the user responsible fo the export"
             "will be used",
    )
    product_ftp = fields.Boolean('Send By FTP')
    product_ftp_host = fields.Char(
        string='Host',
        help="FTP server used to send products file.")
    product_ftp_port = fields.Char(
        string='Port')
    product_ftp_user = fields.Char(
        string='User')
    product_ftp_password = fields.Char(
        string='Password')
    product_ftp_directory = fields.Char(
        string='Upload Directory')
    product_filename = fields.Char(
        string='Products File Name',
        required=True)
    last_export_date = fields.Datetime('Last Export on')
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        required=True,
        help='Warehouse used to compute the '
             'stock quantities.',
    )
    product_stock_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Stock Field',
        default=lambda x: x._get_stock_field_id(),
        domain="[('model', 'in', ['product.product', 'product.template']),"
               " ('ttype', '=', 'float')]",
        help="Choose the field of the product which will be used for "
             "stock inventory updates.\nIf empty, Quantity Available "
             "is used.",
        required=True
    )
    product_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Sale Price List',
        help='If specified, this price list will be used to determine the '
        'price exported to Lengow'
    )
    binded_product_ids = fields.One2many(string="Binded Products",
                                         comodel_name='lengow.product.product',
                                         inverse_name='catalogue_id')
    binded_products_count = fields.Float(string='Binded Products',
                                         compute='_count_binded_products')

    @api.model
    def _get_stock_field_id(self):
        field = self.env['ir.model.fields'].search(
            [('model', '=', 'product.product'),
             ('name', '=', 'virtual_available')],
            limit=1)
        return field

    def _count_binded_products(self):
        for backend in self:
            backend.binded_products_count = len(backend.binded_product_ids)

    @api.multi
    def export_binded_products(self):
        self.env['lengow.product.product']._scheduler_export_binded_products(
            domain=[('id', 'in', self.ids)])

    @api.multi
    def name_get(self):
        result = []
        for catalogue in self:
            result.append((catalogue.id, "%s (%s)" %
                           (catalogue.name, catalogue.backend_id.name)))
        return result

    @api.multi
    def write(self, vals):
        if 'backend_id' in vals:
            raise ValidationError(_('You are not allowed to update the backend'
                                    ' reference !'))
        return super(LengowCatalogue, self).write(vals)


class LengowMarketPlace(models.Model):
    _name = 'lengow.market.place'
    _inherit = ['lengow.binding']
    _description = 'Lengow Market Place'
    _parent_name = 'backend_id'

    name = fields.Char(string='Name',
                       required=True)
    homepage = fields.Char(string='Home Page')
    description = fields.Text(string='Text')
    specific_account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Specific analytic account',
    )
    specific_fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Specific fiscal position',
    )
    specific_warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Specific warehouse',
    )
    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic account',
        compute='_get_account_analytic_id',
    )
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Fiscal position',
        compute='_get_fiscal_position_id',
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='warehouse',
        compute='_get_warehouse_id')
    backend_version = fields.Selection(related='backend_id.version')

    @api.multi
    def _get_account_analytic_id(self):
        for mp in self:
            mp.account_analytic_id = (
                mp.specific_account_analytic_id or
                mp.backend_id.account_analytic_id)

    @api.multi
    def _get_fiscal_position_id(self):
        for mp in self:
            mp.fiscal_position_id = (
                mp.specific_fiscal_position_id or
                mp.backend_id.fiscal_position_id)

    @api.multi
    def _get_warehouse_id(self):
        for mp in self:
            mp.warehouse_id = (
                mp.specific_warehouse_id or
                mp.backend_id.warehouse_id)


@lengow30
class LengowMarketPlaceAdapter(GenericAdapter):
    _model_name = 'lengow.market.place'
    _api = "v3.0/marketplaces/"

    def search(self, params, with_account=False):
        return super(LengowMarketPlaceAdapter, self).search(params,
                                                            with_account=True)


@lengow
class LengowMarketPlaceBatchImporter(DirectBatchImporter):
    _model_name = 'lengow.market.place'


@lengow
class LengowMarketPlaceMapper(ImportMapper):
    _model_name = 'lengow.market.place'

    direct = [('homepage', 'homepage'),
              ('description', 'description')]

    @mapping
    def name(self, record):
        name = record['name']
        if name is None:
            name = _('Undefined')
        return {'name': name}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}


@lengow
class LengowMarketPlaceImporter(LengowImporter):
    _model_name = 'lengow.market.place'

    _base_mapper = LengowMarketPlaceMapper
