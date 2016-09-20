# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from cStringIO import StringIO
import base64
import csv
import ftputil.session

from openerp import api, fields, models
from openerp.addons.connector.unit.mapper import ExportMapper
from openerp.addons.connector.unit.synchronizer import Exporter
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession

from .backend import lengow
from .adapter import ProductAdapter
from .connector import get_environment


class LengowProductProduct(models.Model):
    _name = 'lengow.product.product'
    _inherit = 'lengow.binding'
    _inherits = {'product.product': 'odoo_id'}
    _description = 'Lengow Product'

    odoo_id = fields.Many2one(comodel_name='product.product',
                              string='Product',
                              required=True,
                              ondelete='restrict')
    lengow_qty = fields.Float(string='Computed Stock Quantity',
                              help="Last computed quantity to send "
                                   "on Lengow.")
    active = fields.Boolean('Active', default=True)

    @api.multi
    def compute_lengow_qty(self):
        for product in self:
            if product.backend_id.product_stock_field_id:
                stock_field = product.backend_id.product_stock_field_id.name
            else:
                stock_field = 'virtual_available'

            location = self.env['stock.location']
            if self.env.context.get('location'):
                location = location.browse(self.env.context['location'])
            else:
                location = product.backend_id.warehouse_id.lot_stock_id

            product.write({'lengow_qty':
                           product.with_context(location=location.id)
                           [stock_field]})

    @api.model
    def _scheduler_export_binded_products(self, domain=None):
        if domain is None:
            domain = []
        backends = self.env['lengow.backend'].search(domain)
        for backend in backends:
            session = ConnectorSession(self.env.cr, self.env.uid,
                                       context=self.env.context)
            export_binded_products_batch.delay(
                session,
                'lengow.product.product',
                backend.id,
                description="Export Products To Lengow Backend: %s" %
                backend.name)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    lengow_bind_ids = fields.One2many(
        comodel_name='lengow.product.product',
        inverse_name='odoo_id',
        string='Lengow Bindings',
    )

    product_url = fields.Char('Product Url')
    image_url = fields.Char('Image Url')

    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if 'active' in vals and not vals.get('active'):
            bind_records = self.env['lengow.product.product'].search(
                [('odoo_id', 'in', self.ids)])
            if bind_records:
                bind_records.write({'active': vals.get('active')})
        return res


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
        return {'DESCRIPTION': record.description_sale or ''}

    @mapping
    def PRICE_PRODUCT(self, record):
        product_pricelist_id = record.backend_id.product_pricelist_id.id
        if product_pricelist_id:
            price = record.with_context(pricelist=product_pricelist_id).price
        else:
            price = record.lst_price
        return {'PRICE_PRODUCT': price}

    @mapping
    def CATEGORY(self, record):
        return {'CATEGORY': record.categ_id.display_name or ''}

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

    def uploadFTP(self, backend, ir_attachment):
        port_session_factory = ftputil.session.session_factory(
            port=int(backend.product_ftp_port))
        with ftputil.FTPHost(backend.product_ftp_host, backend.product_ftp_user,
                             backend.product_ftp_password,
                             session_factory=port_session_factory) as ftp_conn:
            target_name = backend.product_ftp_directory\
                + '/' + ir_attachment.datas_fname
            if ftp_conn.path.isfile(target_name):
                raise Exception("%s already exists" % target_name)
            else:
                with ftp_conn.open(target_name, mode='wb') as fileobj:
                    fileobj.write(base64.b64decode(ir_attachment.datas))

    def run(self, backend=None, products=None, FTPTransfert=True):
        data = None
        adapter = self.unit_for(ProductAdapter)
        csvFile = StringIO()
        csvRows = [adapter.getCSVHeader()]
        products.compute_lengow_qty()
        if backend.default_lang_id:
            lang = backend.default_lang_id.code
        else:
            lang = self.env.user.lang or 'en_US'
        for product in products.with_context(lang=lang):
            self._lengow_record = product
            map_record = self._map_data()
            vals = self.export(map_record)
            csvRows.append(adapter.getCSVFromRecord(vals))

        wr = csv.writer(csvFile, quoting=csv.QUOTE_ALL, delimiter=';')
        wr.writerows(csvRows)

        ir_attachment = self.session.env['ir.attachment'].create(
            {'name': backend.product_ftp_filename,
             'datas': base64.encodestring(csvFile.getvalue()),
             'datas_fname': backend.product_ftp_filename})

        if FTPTransfert:
            self.uploadFTP(backend, ir_attachment)

        return data


@job(default_channel='root.lengow')
def export_binded_products_batch(session, model_name, backend_id, fields=None):
    """ Export products binded to given backend """
    backend = session.env['lengow.backend'].browse(backend_id)
    env = get_environment(session, model_name, backend.id)
    products_exporter = env.get_connector_unit(ProductExporter)
    return products_exporter.run(backend=backend,
                                 products=backend.binded_product_ids)
