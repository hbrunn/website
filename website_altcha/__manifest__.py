# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "ALTCHA",
    "summary": "Use ALTCHA captchas in website forms",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Website/Website",
    "website": "https://github.com/OCA/website",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "external_dependencies": {
        "python": ["altcha"],
    },
    "depends": [
        "website",
    ],
    "data": [
        "templates/website.xml",
        "templates/widget_altcha.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_frontend": [
            "/website_altcha/static/src/*",
        ],
        "website_altcha.assets": [
            "/website_altcha/static/lib/*",
        ],
    },
}
