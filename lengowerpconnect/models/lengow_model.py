# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.exceptions import ValidationError


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
        return [('2.0', '2.0+')]

    version = fields.Selection(selection='select_versions', required=True)
    location = fields.Char(
        string='Location',
        required=True,
        help="Url to Lengow application",
    )
    username = fields.Char(
        string='Username',
        help="Webservice user",
    )
    password = fields.Char(
        string='Password',
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
    catalogue_ids = fields.One2many(string='Catalogue',
                                    comodel_name='lengow.catalogue',
                                    inverse_name='backend_id')
    binded_products_count = fields.Float(compute='_count_binded_products')

    def _count_binded_products(self):
        for catalogue in self.catalogue_ids:
            self.binded_products_count += catalogue.binded_products_count

    def _get_default_company(self):
        return self.env.user.company_id


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
