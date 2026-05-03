/** @odoo-module **/
/* Copyright 2026 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0) */

import publicWidget from "web.public.widget";
import {qweb} from "web.core";

export const Widget = publicWidget.Widget.extend({
    assetLibs: ["website_altcha.assets"],
    selector: ".o_widget_altcha",
    disabledInEditableMode: false,
    events: {
        "load altcha-widget": "onLoadAltchaWidget",
    },

    async start() {
        const widget_html = qweb.render("widget.altcha", {
            widgetAttributes: this.widgetAttributes(),
        });
        this.$el.append(widget_html);
        this.$("altcha-widget").on("load", this.proxy("onLoadAltchaWidget"));
        this.$("altcha-widget").on("verified", this.proxy("onVerifiedAltchaWidget"));
    },
    widgetAttributes() {
        return {
            challenge: "/website_altcha/challenge",
            name: "website_altcha",
        };
    },
    onLoadAltchaWidget() {
        this.$("input[type=checkbox]").addClass("o_website_form_input");
    },
    onVerifiedAltchaWidget() {
        this.$el.parents(".o_has_error").removeClass("o_has_error");
    },
    destroy() {
        this.$el.empty();
        return this._super.apply(this, arguments);
    },
});

publicWidget.registry.widget_altcha = Widget;
