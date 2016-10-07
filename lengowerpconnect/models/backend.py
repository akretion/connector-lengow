# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp.addons.connector.backend as backend


lengow = backend.Backend('lengow')
""" Generic Lengow Backend """

lengow20 = backend.Backend(parent=lengow, version='2.0')
""" Lengow Backend for version 2.0 """

lengow30 = backend.Backend(parent=lengow, version='3.0')
""" Lengow Backend for version 3.0 """
