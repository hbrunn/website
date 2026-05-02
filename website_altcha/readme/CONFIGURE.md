The module works out of the box, keep in mind however that the mechanism used only works with javascript enabled and when Odoo is served via HTTPS. Both are structural requirements and can't be circumvented.

If you want to add ALTCHA verification to other forms than the contact form, you need to set the flag `Require captcha (ALTCHA)` on the model in the `Website Forms` tab to enforce verification on the server side, and take care that there's an element with class `.o_widget_altcha` on the form(s) you use.
