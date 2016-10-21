# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.addons.connector.connector import get_openerp_module,\
    is_module_installed
from openerp.exceptions import ValidationError


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
        For Lengow API 2.0, each market place as its own way to update
        orders. This class should be inherited and specified for each
        marketplace
    '''
    marketplace = None
    _param_tracking_code_name = None
    _param_tracking_carrier_name = None
    _tracking_mandatory = False
    _restricted_carrier_code = {}

    __metaclass__ = MetaMarketPlaceConfigurator

    def get_configurator(self, env, marketplace):
        configurator = self.__class__.by_marketplace.get(marketplace, None)
        if configurator:
            if is_module_installed(env, get_openerp_module(configurator)):
                return configurator
        return None

    def get_export_picking_api(self, id_flux, order_id):
        return None

    def get_export_picking_tracking_params(self):
        return {}

    def check_carrier_code(self, carrier_code):
        if self._restricted_carrier_code:
            if carrier_code not in self._restricted_carrier_code:
                raise ValidationError('Carrier code %s is not allowed for'
                                      ' marketplace %s' %
                                      (carrier_code, self.marketplace))
