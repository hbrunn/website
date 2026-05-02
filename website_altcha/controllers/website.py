# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


import werkzeug
from altcha import verify_solution

from odoo import http

from odoo.addons.website.controllers.form import WebsiteForm as WebsiteFormWebsite


class WebsiteForm(WebsiteFormWebsite):
    @http.route()
    def website_form(self, model_name, **kwargs):
        model = http.request.env["ir.model"]._get(model_name)
        if model.website_form_website_altcha:
            if not self._website_altcha_verify(kwargs):
                raise werkzeug.exceptions.BadRequest(
                    "Invalid challenge response (ALTCHA)"
                )
        return super().website_form(model_name, **kwargs)

    def _website_altcha_verify(self, kwargs):
        secret = (
            http.request.env["ir.config_parameter"].sudo().get_param("database.secret")
        )
        result = verify_solution(kwargs.pop("website_altcha"), secret)
        return result.verified
