# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp

from openerp.addons.connector.connector import Binder

from .backend import lengow


class LengowBinder(Binder):
    """ Generic Binder for Lengow """


@lengow
class LengowModelBinder(LengowBinder):
    _model_name = [
        'lengow.market.place',
        'lengow.sale.order',
        'lengow.sale.order.line',
        'lengow.res.partner',
        'lengow.product.product'
    ]

    def to_openerp(self, external_id, unwrap=False, browse=False):
        """ Give the Odoo ID for an external ID

        :param external_id: external ID for which we want the Odoo ID
        :param unwrap: if True, returns the normal record (the one
                       inherits'ed), else return the binding record
        :param browse: if True, returns a recordset
        :return: a recordset of one record, depending on the value of unwrap,
                 or an empty recordset if no binding is found
        :rtype: recordset
        """
        bindings = self.model.with_context(active_test=False).search(
            [('lengow_id', '=', str(external_id)),
             ('backend_id', '=', self.backend_record.id)]
        )
        if not bindings:
            return self.model.browse() if browse else None

        if len(bindings) > 1:
            # can be the case for lengow.product.product because the same
            # product can be binded to several catalogue
            assert len(set([binding.openerp_id.id
                            for binding in bindings])) == 1, (
                "Multiple value for same id %s" % external_id)
            bindings = bindings[0]

        if unwrap:
            return bindings.openerp_id if browse else bindings.openerp_id.id
        else:
            return bindings if browse else bindings.id

    def to_backend(self, record_id, wrap=False):
        """ Give the external ID for an Odoo ID

        :param record_id: Odoo ID for which we want the external id
                          or a recordset with one record
        :param wrap: if False, record_id is the ID of the binding,
            if True, record_id is the ID of the normal record, the
            method will search the corresponding binding and returns
            the backend id of the binding
        :return: backend identifier of the record
        """
        record = self.model.browse()
        if isinstance(record_id, openerp.models.BaseModel):
            record_id.ensure_one()
            record = record_id
            record_id = record_id.id
        if wrap:
            binding = self.model.with_context(active_test=False).search(
                [('openerp_id', '=', record_id),
                 ('backend_id', '=', self.backend_record.id),
                 ]
            )
            if binding:
                binding.ensure_one()
                return binding.lengow_id
            else:
                return None
        if not record:
            record = self.model.browse(record_id)
        assert record
        return record.lengow_id

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an Odoo ID

        :param external_id: External ID to bind
        :param binding_id: Odoo ID to bind
        :type binding_id: int
        """
        if not isinstance(binding_id, openerp.models.BaseModel):
            binding_id = self.model.browse(binding_id)
        binding_id.write(
            {'lengow_id': str(external_id)})
