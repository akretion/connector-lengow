# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Lengow Connector",
    "summary": "Module used to connect Odoo to Lengow",
    "version": "8.0.1.0.0",
    "category": "Connector",
    "website": "https://odoo-community.org/",
    "author": "Cédric Pigeon, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "connector_ecommerce",
        "product",
        "product_sequence",
        "sale_stock",
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/lengow_product_binding_wizard_view.xml',
        'views/product_view.xml',
        'views/lengow_model_view.xml',
        'views/lengowerpconnect_menu.xml',
        'wizards/lengow_product_unbinding_wizard_view.xml',
    ],
    "demo": [
    ],
}
