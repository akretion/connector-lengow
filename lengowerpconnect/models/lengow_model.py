# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


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
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        required=True,
        help='Warehouse used to compute the '
             'stock quantities.',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        related='warehouse_id.company_id',
        string='Company',
        readonly=True,
    )
    default_lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Default Language',
        help="This the default language used to export products, if nothing"
             "is specified, the language of the user responsible fo the export"
             "will be used",
    )
    product_ftp_host = fields.Char(
        string='Host',
        required=True,
        help="FTP server used to send products file.")
    product_ftp_port = fields.Char(
        string='Port',
        required=True)
    product_ftp_user = fields.Char(
        string='User',
        required=True)
    product_ftp_password = fields.Char(
        string='Password',
        required=True)
    product_ftp_directory = fields.Char(
        string='Upload Directory',
        required=True)
    product_ftp_filename = fields.Char(
        string='Products File Name',
        required=True)
    product_stock_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Stock Field',
        default=_get_stock_field_id,
        domain="[('model', 'in', ['product.product', 'product.template']),"
               " ('ttype', '=', 'float')]",
        help="Choose the field of the product which will be used for "
             "stock inventory updates.\nIf empty, Quantity Available "
             "is used.",
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
    product_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Sale Price List',
        help='If specified, this price list will be used to determine the '
        'price exported to Lengow'
    )
    binded_product_ids = fields.One2many(string="Binded Products",
                                         comodel_name='lengow.product.product',
                                         inverse_name='backend_id')
    binded_products_count = fields.Float(compute='_count_binded_products')

    @api.multi
    def export_binded_products(self):
        self.env['lengow.product.product']._scheduler_export_binded_products(
            domain=[('id', 'in', self.ids)])
