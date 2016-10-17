# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class PaymentMethod(models.Model):
    _inherit = 'payment.method'

    marketplace_id = fields.Many2one(string='Lengow MarketPlace',
                                     comodel_name='lengow.market.place')
