from odoo import models,api

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    def update_family_color(self):
        return
