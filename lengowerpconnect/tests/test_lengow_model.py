# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from . import common
from openerp.exceptions import ValidationError


class TestLengowProductBinding(common.SetUpLengowBase):

    def setUp(self):
        super(TestLengowProductBinding, self).setUp()

    def test_update_catalogue_backend_id(self):
        '''
            Try to update backend_id on catalogue
        '''
        backend = self.backend_model.create(
            {'name': 'Test Lengow Backend',
             'version': '2.0',
             'location': 'http://backend.com',
             'username': 'acsone123',
             'password': '23'}
        )
        with self.assertRaises(ValidationError):
            self.catalogue.write({'backend_id': backend.id})
