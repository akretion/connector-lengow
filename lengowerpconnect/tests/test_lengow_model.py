# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock

from . import common
from openerp.exceptions import ValidationError
from openerp.addons.connector.session import ConnectorSession

from ..models.connector import get_environment
from ..models.lengow_model import LengowMarketPlaceAdapter
from openerp.osv.expression import TRUE_LEAF


class TestUpdateBackendCatalogue(common.SetUpLengowBase):

    def setUp(self):
        super(TestUpdateBackendCatalogue, self).setUp()

    def test_update_catalogue_backend_id(self):
        '''
            Try to update backend_id on catalogue which must be forbidden
        '''
        warehouse = self.env.ref('stock.warehouse0')
        backend = self.backend_model.create(
            {'name': 'Test Lengow Backend',
             'version': '2.0',
             'location': 'http://backend.com',
             'access_token': '71529bf5fe6ae6d50d3995ad5db63720',
             'secret': 'd65d8f60af57f568b9bfa9de2f24ee4c',
             'warehouse_id': warehouse.id}
        )
        with self.assertRaises(ValidationError):
            self.catalogue.write({'backend_id': backend.id})


class TestToken(common.SetUpLengowBase):
    '''
        Each request made to Lengow need a authentification token
    '''

    def setUp(self):
        super(TestToken, self).setUp()

    def test_get_token_fail(self):
        with mock.patch(self.post_method) as mock_post:
            env = get_environment(ConnectorSession.from_env(self.env),
                                  'lengow.market.place', self.backend30.id)
            # mock post request for token
            mock_post = self._configure_mock_request('token_fail', mock_post)
            a = LengowMarketPlaceAdapter(env)
            message = '403 - Forbidden'
            try:
                a._get_token()
                self.assertFail()
            except Exception as exc:
                self.assertEqual(exc.message, message)

    def test_get_token(self):
        with mock.patch(self.post_method) as mock_post:
            env = get_environment(ConnectorSession.from_env(self.env),
                                  'lengow.market.place', self.backend30.id)
            # mock post request for token
            mock_post = self._configure_mock_request('token', mock_post)
            a = LengowMarketPlaceAdapter(env)
            token, user, account = a._get_token()
            mock_post.assert_called_with(
                'http://anyurl/access/get_token',
                params={},
                data={'access_token': 'a4a506440102b8d06a0f63fdd1eadd5f',
                      'secret': '66eb2d56a4e930b0e12193b954d6b2e4'},
                headers={})
            self.assertEqual(token, self.expected_token)
            self.assertEqual(user, self.expected_user)
            self.assertEqual(account, self.expected_account)


class TestBackendSynchronize(common.SetUpLengowBase):
    '''
        Test the synchronisation of Marketplaces between Odoo and Lengow
    '''

    def setUp(self):
        super(TestBackendSynchronize, self).setUp()

    def test_backend_synchronise(self):
        with mock.patch(self.post_method) as mock_post,\
                mock.patch(self.get_method) as mock_get:
            # mock post request for token
            mock_post = self._configure_mock_request('token', mock_post)
            # mock get request for marketplace data
            mock_get = self._configure_mock_request('marketplace', mock_get)
            # ---------------------------------
            # Test MarketPlace Creation
            # ---------------------------------
            self.backend30.synchronize_metadata()
            mock_get.assert_called_with(
                'http://anyurl/v3.0/marketplaces/',
                params={'account_id': self.expected_account},
                headers={'Authorization': self.expected_token},
                data={})
            places = self.marketplace_model.search([TRUE_LEAF])
            self.assertEqual(len(places), 2)

            binding_ids = [place.lengow_id for place in places]

            self.assertTrue('amazon_fr' in binding_ids)
            self.assertTrue('admarkt' in binding_ids)

            # ---------------------------------
            # Test MarketPlace Update
            # ---------------------------------
            fake_homepage = 'www.homepage.com'
            places.write({'homepage': fake_homepage})
            self.assertTrue((all(place.homepage == fake_homepage
                                 for place in places)))
            self.backend30.synchronize_metadata()
            self.assertFalse((all(place.homepage == fake_homepage
                                  for place in places)))
