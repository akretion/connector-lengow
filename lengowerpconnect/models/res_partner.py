# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models
from openerp.addons.connector.unit.mapper import mapping

from .backend import lengow, lengow20
from .import_synchronizer import LengowImporter
from .import_synchronizer import LengowImportMapper


class LengowResPartner(models.Model):
    _name = 'lengow.res.partner'
    _inherit = 'lengow.binding'
    _inherits = {'res.partner': 'openerp_id'}
    _description = 'Lengow Partner'

    openerp_id = fields.Many2one(comodel_name='res.partner',
                                 string='Partner',
                                 required=True,
                                 ondelete='cascade')


@lengow20
class PartnerImportMapper(LengowImportMapper):
    _model_name = 'lengow.res.partner'

    direct = [('address', 'street'),
              ('address_2', 'street2'),
              ('zipcode', 'zip'),
              ('city', 'city'),
              ('phone_home', 'phone'),
              ('phone_mobile', 'mobile'),
              ('email', 'email'),
              ]

    @mapping
    def name(self, record):
        if record['firstname']:
            name = " ".join([record['lastname'],
                             record['firstname']])
        else:
            name = record['lastname']
        return {'name': name}

    @mapping
    def country_id(self, record):
        country = self.env['res.country'].search(
            [('code', '=', record['country_iso'])])
        return {'country_id': country.id if country else None}


@lengow
class PartnerImporter(LengowImporter):
    _model_name = ['lengow.res.partner']

    _base_mapper = PartnerImportMapper
    _discriminant_fields = ['city', 'email']
    _prefix = False

    def _clean_data_keys(self, data):
        '''
            From the lengow API we receive 2 kinds of data for partner:
            - delivery data
            - billing data
            As they have the same values but a different prefix in their data
            naming convention, the goal of this method is to remove the prefix
            in order to unify the partner import.
            Example:
                billing_name -> name
                delivery_name -> name
        '''
        prefix = data.keys()[0].split('_')[0]
        return self._remove_key_prefix(prefix, data)

    def _remove_key_prefix(self, prefix, data):
        prefix = '%s_' % prefix
        for key in data.keys():
            newkey = key.replace(prefix, '')
            data[newkey] = data.pop(key)
        return data

    def _generate_hash_key(self, record_data):
        record_data = self._clean_data_keys(record_data)
        return super(PartnerImporter, self)._generate_hash_key(record_data)

    def run(self, lengow_id, lengow_data):
        lengow_data = self._clean_data_keys(lengow_data)
        super(PartnerImporter, self).run(lengow_id, lengow_data)
