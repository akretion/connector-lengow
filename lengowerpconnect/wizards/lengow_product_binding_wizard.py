# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class LengowProductBindingWizard(models.TransientModel):
    _name = 'lengow.product.binding.wizard'
    _description = "Wizard to bind products to a Lengow backend"

    lengow_backend_id = fields.Many2one(string='Lengow Backend',
                                        comodel_name='lengow.backend',
                                        required=True,
                                        ondelete='cascade')
    product_ids = fields.Many2many(string='Products',
                                   comodel_name='product.product')

    @api.model
    def default_get(self, fields_list):
        res = super(LengowProductBindingWizard, self).default_get(fields_list)
        lengow_backend_id = self.env.context.get('active_id', False)
        if lengow_backend_id:
            res['lengow_backend_id'] = lengow_backend_id
        return res

    @api.multi
    def bind_products(self):
        for wizard in self:
            binding = self.env['lengow.product.product']
            for product in self.product_ids:
                data = {'lengow_id': product.default_code,
                        'odoo_id': product.id,
                        'backend_id': wizard.lengow_backend_id.id}
                bind_record = binding.with_context(active_test=False).search(
                    [('odoo_id', '=', product.id),
                     ('backend_id', '=', wizard.lengow_backend_id.id)])
                if not bind_record:
                    binding.create(data)
                elif not bind_record.active:
                    bind_record.write({'active': True})
