/** @odoo-module **/
/* Copyright 2026 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0) */

import publicWidget from "web.public.widget";
import {qweb} from "web.core";

export const Widget = publicWidget.Widget.extend({
    assetLibs: ["website_altcha.assets"],
    selector: ".o_widget_altcha",

    async start() {
        const widget_html = qweb.render("widget.altcha", {
            widgetAttributes: this.widgetAttributes(),
        });
        this.$el.append(widget_html);
    },
    widgetAttributes() {
        return {
            challenge: "/website_altcha/challenge",
            name: "website_altcha",
        };
    },
});

publicWidget.registry.widget_altcha = Widget;
