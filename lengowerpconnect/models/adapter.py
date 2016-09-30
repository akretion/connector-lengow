# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests

from openerp.addons.connector.unit.backend_adapter import CRUDAdapter


class LengowLocation(object):

    def __init__(self, location, access_token, secret):
        self.location = location
        self.access_token = access_token
        self.secret = secret


class LengowCRUDAdapter(CRUDAdapter):
    """ External Records Adapter for Lengow """

    def __init__(self, connector_env):
        """
        :param connector_env: current environment (backend, session, ...)
        :type connector_env: :class:`connector.connector.ConnectorEnvironment`
        """
        super(LengowCRUDAdapter, self).__init__(connector_env)
        backend = self.backend_record
        lengow = LengowLocation(
            backend.location,
            backend.access_token,
            backend.secret)
        self.lengow = lengow

    def process_request(self, http_request, url, headers={}, params={},
                        data={}):
        response = http_request(url, headers=headers, params=params, data=data)
        if response.status_code != 200:
            error = response.json()
            message = '%s - %s' % (error['error']['code'],
                                   error['error']['message'])
            raise Exception(message)
        return response.json()

    def _get_token(self):
        url = '%s/access/get_token' % self.lengow.location
        data = {'access_token': str(self.lengow.access_token),
                'secret': str(self.lengow.secret)}
        response = self.process_request(requests.post, url, data=data)
        return response['token'], response['user_id'], response['account_id']

    def _call(self, url, params, with_account=False):
        token, _, account_id = self._get_token()
        url = '%s/%s' % (self.lengow.location, url)
        if with_account:
            params.update({'account_id': account_id})
        return self.process_request(requests.get,
                                    url,
                                    headers={'Authorization': token},
                                    params=params)


class GenericAdapter(LengowCRUDAdapter):

    _model_name = None
    _api = None

    def search(self, params, with_account=False):
        return self._call(self._api, params if params else {},
                          with_account=with_account)
