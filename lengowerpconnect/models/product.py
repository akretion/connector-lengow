# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from cStringIO import StringIO
import csv
import ftputil.session
from collections import OrderedDict

from openerp import api, fields, models
from openerp.addons.connector.unit.mapper import ExportMapper
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.connector.unit.synchronizer import Exporter

from openerp.addons.connector.connector import ConnectorUnit

from .backend import lengow


class LengowProductProduct(models.Model):
    _name = 'lengow.product.product'
    _inherit = 'lengow.binding'
    _inherits = {'product.product': 'openerp_id'}
    _description = 'Lengow Product'

    catalogue_id = fields.Many2one(comodel_name='lengow.catalogue',
                                   string='Lengow Catalogue',
                                   required=True,
                                   ondelete='restrict')
    openerp_id = fields.Many2one(comodel_name='product.product',
                                 string='Product',
                                 required=True,
                                 ondelete='restrict')
    lengow_qty = fields.Float(string='Computed Stock Quantity',
                              help="Last computed quantity to send "
                                   "on Lengow.")
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('lengow_uniq_catalog', 'unique(backend_id, catalogue_id, lengow_id)',
         'This product is already binded to this catalogue'),
    ]

    @api.multi
    def compute_lengow_qty(self):
        for product in self:
            if product.catalogue_id.product_stock_field_id:
                stock_field = product.catalogue_id.product_stock_field_id.name
            else:
                stock_field = 'virtual_available'

            location = self.env['stock.location']
            if self.env.context.get('location'):
                location = location.browse(self.env.context['location'])
            else:
                location = product.catalogue_id.warehouse_id.lot_stock_id

            product.sudo().write({'lengow_qty':
                                  product.with_context(location=location.id)
                                  [stock_field]})


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _search_lengow_catalogue_ids(self, operator, value):
        lengow_prod_obj = self.env['lengow.product.product']
        bindings = lengow_prod_obj.search(
            [('catalogue_id.name', operator, value)])

        return [('id', 'in',
                 bindings.mapped('openerp_id').ids)]

    lengow_bind_ids = fields.One2many(
        comodel_name='lengow.product.product',
        inverse_name='openerp_id',
        string='Lengow Bindings',
    )
    lengow_catalogue_ids = fields.Many2many(string='Lengow Catalogues',
                                            comodel_name='lengow.catalogue',
                                            compute='_get_catalogue_ids',
                                            store=False,
                                            search=_search_lengow_catalogue_ids
                                            )

    product_url = fields.Char('Product Url')
    image_url = fields.Char('Image Url')

    @api.multi
    def _get_catalogue_ids(self):
        for product in self:
            product.lengow_catalogue_ids = [binding.catalogue_id.id for binding
                                            in product.lengow_bind_ids]

    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if 'active' in vals and not vals.get('active'):
            bind_records = self.env['lengow.product.product'].search(
                [('openerp_id', 'in', self.ids)])
            if bind_records:
                bind_records.write({'active': vals.get('active')})
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _search_lengow_catalogue_ids(self, operator, value):
        lengow_prod_obj = self.env['lengow.product.product']
        bindings = lengow_prod_obj.search(
            [('catalogue_id.name', operator, value)])

        return [('id', 'in',
                 bindings.mapped('openerp_id.product_tmpl_id').ids)]

    lengow_catalogue_ids = fields.Many2many(
        string='Lengow Catalogues',
        comodel_name='lengow.catalogue',
        related='product_variant_ids.lengow_catalogue_ids',
        store=False,
        search=_search_lengow_catalogue_ids)


@lengow
class ProductExportMapper(ExportMapper):
    _model_name = 'lengow.product.product'

    direct = []

    @mapping
    def ID_PRODUCT(self, record):
        return {'ID_PRODUCT': record.lengow_id}

    @mapping
    def NAME_PRODUCT(self, record):
        return {'NAME_PRODUCT': record.name}

    @mapping
    def DESCRIPTION(self, record):
        return {'DESCRIPTION': record.description_sale or record.name}

    @mapping
    def PRICE_PRODUCT(self, record):
        product_pricelist_id = record.catalogue_id.product_pricelist_id.id
        if product_pricelist_id:
            price = record.with_context(pricelist=product_pricelist_id).price
        else:
            price = record.lst_price
        return {'PRICE_PRODUCT': round(price, 2) if price else ''}

    @mapping
    def CATEGORY(self, record):
        cat = record.categ_id.display_name or ''
        cat = cat.replace('/', '>')
        return {'CATEGORY': cat}

    @mapping
    def URL_PRODUCT(self, record):
        return {'URL_PRODUCT': record.product_url or ''}

    @mapping
    def URL_IMAGE(self, record):
        return {'URL_IMAGE': record.image_url or ''}

    @mapping
    def EAN(self, record):
        return {'EAN': record.ean13 or ''}

    @mapping
    def SUPPLIER_CODE(self, record):
        return {'SUPPLIER_CODE': record.seller_ids[0].product_code or ''
                if record.seller_ids else ''}

    @mapping
    def BRAND(self, record):
        return {'BRAND': ''}

    @mapping
    def QUANTITY(self, record):
        return {'QUANTITY': record.lengow_qty}


@lengow
class ProductAdapter(ConnectorUnit):
    _model_name = 'lengow.product.product'

    _DataMap = {'ID_PRODUCT': 0,
                'NAME_PRODUCT': 1,
                'DESCRIPTION': 2,
                'PRICE_PRODUCT': 3,
                'CATEGORY': 4,
                'URL_PRODUCT': 5,
                'URL_IMAGE': 6,
                'EAN': 7,
                'SUPPLIER_CODE': 8,
                'BRAND': 9,
                'QUANTITY': 10}

    def getCSVFromRecord(self, record):
        values = []
        data = OrderedDict(sorted(self._DataMap.items(), key=lambda r: r[1]))
        for attr, _ in data.items():
            if attr in record:
                val = record[attr]
                if isinstance(val, unicode):
                    try:
                        val = val.encode('utf-8')
                    except UnicodeError:
                        pass
                values.append(val)

        return values

    def getCSVHeader(self):
        header = OrderedDict(sorted(self._DataMap.items(), key=lambda r: r[1]))
        return header.keys()


@lengow
class ProductExporter(Exporter):
    _base_mapper = ProductExportMapper
    _model_name = 'lengow.product.product'

    def __init__(self, connector_env):

        res = super(ProductExporter, self).__init__(connector_env)
        self._lengow_record = None

        return res

    def export(self, map_record):

        return map_record.values()

    def _map_data(self):

        return self.mapper.map_record(self._lengow_record)

    def uploadFTP(self, catalogue, ir_attachment):
        port_session_factory = ftputil.session.session_factory(
            port=int(catalogue.product_ftp_port))
        with ftputil.FTPHost(catalogue.product_ftp_host,
                             catalogue.product_ftp_user,
                             catalogue.product_ftp_password,
                             session_factory=port_session_factory) as ftp_conn:
            target_name = catalogue.product_ftp_directory\
                + '/' + ir_attachment.datas_fname
            with ftp_conn.open(target_name, mode='wb') as fileobj:
                fileobj.write(base64.b64decode(ir_attachment.datas))

    def run(self, catalogue=None, products=None):
        data = None
        adapter = self.unit_for(ProductAdapter)
        csvFile = StringIO()
        csvRows = [adapter.getCSVHeader()]
        products.compute_lengow_qty()
        if catalogue.default_lang_id:
            lang = catalogue.default_lang_id.code
        else:
            lang = self.env.user.lang or 'en_US'
        for product in products.with_context(lang=lang):
            self._lengow_record = product
            map_record = self._map_data()
            vals = self.export(map_record)
            csvRows.append(adapter.getCSVFromRecord(vals))

        wr = csv.writer(csvFile, quoting=csv.QUOTE_ALL, delimiter=';')
        wr.writerows(csvRows)

        job_uuid = self.env.context.get('job_uuid', False)
        job = self.env['queue.job'].sudo().search([('uuid', '=', job_uuid)],
                                                  limit=1)

        attach_data = {'name': catalogue.product_filename,
                       'datas': base64.encodestring(csvFile.getvalue()),
                       'datas_fname': catalogue.product_filename}
        if job:
            attach_data.update({'res_model': 'queue.job',
                                'res_id': job.id})

        ir_attachment = self.session.env['ir.attachment'].create(
            attach_data)

        if catalogue.product_ftp:
            self.uploadFTP(catalogue, ir_attachment)

        catalogue.sudo().write({'last_export_date': fields.Datetime.now()})
        return data
