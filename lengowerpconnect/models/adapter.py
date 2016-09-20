# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import OrderedDict

from openerp.addons.connector.connector import ConnectorUnit

from .backend import lengow


class LengowAdapter():

    _data = ''

    def __init__(self, data=None):
        if data and data != '' and self._checkValid(data):
            self._data = data

    def _checkValid(self, data):
        return True

    def getCSVFromRecord(self, record):

        raise NotImplementedError('Not Implemented!')


@lengow
class ProductAdapter(ConnectorUnit):
    _model_name = 'lengow.product.product'

    _DataMap = {'ID_PRODUCT': 0,
                'NAME_PRODUCT': 1,
                'DESCRIPTION': 2,
                'PRICE_PRODUCT': 3,
                'CATEGORY': 4,
                'URL_PRODUCT': 5,
                'URL_IMAGE': 6,
                'EAN': 7,
                'SUPPLIER_CODE': 8,
                'BRAND': 9,
                'QUANTITY': 10}

    def getCSVFromRecord(self, record):
        values = []
        data = OrderedDict(sorted(self._DataMap.items(), key=lambda r: r[1]))
        for attr, _ in data.items():
            if attr in record:
                values.append(str(record[attr]))

        return values

    def getCSVHeader(self):
        header = OrderedDict(sorted(self._DataMap.items(), key=lambda r: r[1]))
        return header.keys()
