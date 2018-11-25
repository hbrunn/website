# -*- coding: utf-8 -*-
# Copyright 2015-2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Address in contact page",
    "version": "10.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Website",
    "summary": "Lets visitors fill in their address in the contact form",
    "depends": [
        'website_crm',
    ],
    "data": [
        "data/ir_model_fields.xml",
        "views/contactus_form.xml",
    ],
    "installable": True,
}
