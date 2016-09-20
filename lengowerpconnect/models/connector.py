# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models
from openerp.addons.connector.connector import ConnectorEnvironment


def get_environment(session, model_name, backend_id):
    """ Create an environment to work with.  """
    backend_record = session.env['lengow.backend'].browse(backend_id)
    env = ConnectorEnvironment(backend_record, session, model_name)
    return env


class LengowBinding(models.AbstractModel):
    """ Abstract Model for the Bindigs.

    All the models used as bindings between Lengow and OpenERP
    (``lengow.product.product``, ...) should
    ``_inherit`` it.
    """
    _name = 'lengow.binding'
    _inherit = 'external.binding'
    _description = 'Lengow Binding (abstract)'

    # odoo_id = odoo-side id must be declared in concrete model
    backend_id = fields.Many2one(
        comodel_name='lengow.backend',
        string='Lengow Backend',
        required=True,
        ondelete='restrict',
    )
    lengow_id = fields.Char(string='ID on Lengow')

    _sql_constraints = [
        ('lengow_uniq', 'unique(backend_id, lengow_id)',
         'A binding already exists with the same Lengow ID.'),
    ]
