# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import json

from altcha import create_challenge

from odoo import http


class AltchaController(http.Controller):
    @http.route("/website_altcha/challenge", auth="public")
    def challenge(self):
        # TODO: make it pass the csrf token?
        challenge = create_challenge(**self._create_challenge_args())
        return http.request.make_response(
            json.dumps(challenge.to_dict()),
            headers={
                "content-type": "application/json",
            },
        )

    def _create_challenge_args(self):
        secret = (
            http.request.env["ir.config_parameter"].sudo().get_param("database.secret")
        )
        return dict(algorithm="PBKDF2/SHA-256", cost=5000, hmac_secret=secret)


from odoo.addons.website.controllers.form import WebsiteForm as WebsiteFormWebsite


class WebsiteForm(WebsiteFormWebsite):
    @http.route()
    def website_form(self, model_name, **kwargs):
        import pdb

        pdb.set_trace()
        return super().website_form(model_name, **kwargs)
