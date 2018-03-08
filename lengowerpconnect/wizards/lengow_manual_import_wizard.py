# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, fields, models
from openerp.addons.connector.session import ConnectorSession
from ..models.import_synchronizer import import_record
from ..models.adapter import GenericAdapter20
from ..models.connector import get_environment


class LengowManualImportWizard(models.TransientModel):
    _name = 'lengow.manual.import.wizard'

    id_flux = fields.Char(required=True)
    id_order = fields.Char(required=True)

    @api.multi
    def run(self):
        backend_id = self._context['active_id']
        session = ConnectorSession.from_env(self.env)
        env = get_environment(session, 'lengow.sale.order', backend_id)
        adapter = env.get_connector_unit(GenericAdapter20)
        order = adapter.get(self.id_flux, self.id_order)
        description = (
            'Import Manually the sale order %s from the flow %s from'
            'Lengow Backend %s' % (
                self.order_id, self.flux_id, self.backend_id.name))
        import_record(session,
                      'sale.order',
                      backend_id,
                      order_id,
                      order,
                      description=description,
                      **kwargs)
