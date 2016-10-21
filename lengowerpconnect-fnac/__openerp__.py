# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Lengow Connector Fnac",
    "summary": "Module used to manage specification for Fnac marketplace",
    "version": "8.0.1.0.0",
    "category": "Connector",
    "website": "https://odoo-community.org/",
    "author": "Cédric Pigeon, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "lengowerpconnect",
    ],
    "data": [
        'data/lengowerpconnect_data.xml'
    ]
}
