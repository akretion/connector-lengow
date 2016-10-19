# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


class MetaMarketPlaceConfigurator(type):
    """ Metaclass for MarketPlaceConfigurator classes. """
    by_marketplace = {}

    def __init__(cls, name, bases, attrs):
        super(MetaMarketPlaceConfigurator, cls).__init__(name, bases, attrs)
        if cls.marketplace and cls.marketplace not in\
           MetaMarketPlaceConfigurator.by_marketplace:
            MetaMarketPlaceConfigurator.by_marketplace[cls.marketplace] = cls


class MarketPlaceConfigurator(object):
    '''
        For lLengow API 2.0, each market place as its own way to update
        orders. This class should be inherited and specified for each
        marketplace
    '''
    marketplace = None
    _param_tracking_code_name = None
    _param_tracking_carrier_name = None

    __metaclass__ = MetaMarketPlaceConfigurator

    def get_export_picking_api(self, id_flux, order_id):
        return None

    def get_export_picking_params(self):
        return {}
