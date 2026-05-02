# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    website_form_website_altcha = fields.Boolean("Require captcha (ALTCHA)")
