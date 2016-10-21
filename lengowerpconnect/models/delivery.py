# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    lengow_code = fields.Char('Lengow Code')
    lengow_value = fields.Char('Value to Export to Lengow',
                               compute='_compute_lengow_value')

    def _compute_lengow_value(self):
        for carrier in self:
            carrier.lengow_value = self.lengow_code or self.name
