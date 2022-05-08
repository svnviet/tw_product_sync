from odoo import fields, models, api, tools
from odoo.addons.queue_job.job import job
index = {'CloseUp': ['BL_20', 'BL_65', 'CU'],
         'FlatShot': ['FS', 'FS_ruler'],
         'Ball': ['BL_20', 'BL_65'],
         'Bed': ['Bed'],
         'Chair': ['Armchair', 'ButtonChair', 'DiningChair', 'ClassicChair', 'FramedChair', 'ParsonChair', 'WingbackChair'],
         'Curtain': ['DoublePleatOpenedRail', 'GrommetOpenedBar', 'PencilPleatOpenedBar', 'WavetrackOpenedRail'],
         'Pouf': ['Pouf'],
         'Sofa': ['SofaArcher', 'SofaChesterfield', 'SofaContemporary', 'SofaCurved', 'SofaDaybed', 'SofaLounge', 'SofaLoveseat']}


class BruImage(models.Model):
    _name = 'bru.product.image'

    name = fields.Char()
    bru_id = fields.Char()
    asset_type = fields.Char()
    render_scene = fields.Char()
    key = fields.Char(help='endpoint for get image from api')
    bru_product_id = fields.Integer()
    odoo_product_id = fields.Many2one('product.template')
    bru_collection_id = fields.Many2one('bru.collection')
    sequence = fields.Integer()
    is_update_sequence = fields.Boolean(default=False)

    def update_image_sequence(self):
        sequence = 0
        for asset_type in index.keys():
            for render_scene in index.get(asset_type):
                bru_image_ids = self.filtered(
                    lambda r: r.render_scene == render_scene and r.asset_type == asset_type and r.is_update_sequence is False)
                if bru_image_ids:
                    for bru_image in bru_image_ids:
                        bru_image.sequence = sequence
                        bru_image.is_update_sequence = True
                        sequence += 1
            # update for image not in list index
            image_ids = self.filtered(lambda r: r.asset_type == asset_type and r.is_update_sequence is False).sorted(
                key=lambda r: r.render_scene)
            if image_ids:
                for bru_image in image_ids:
                    bru_image.sequence = sequence
                    bru_image.is_update_sequence = True
                    sequence += 1
        # update for image not in list keys
        image_ids = self.filtered(lambda r: r.is_update_sequence is False)
        if image_ids:
            for bru_image in image_ids:
                bru_image.sequence = sequence
                bru_image.is_update_sequence = True
                sequence += 1


class BruCollection(models.Model):
    _name = 'bru.collection'

    bru_image_info = fields.One2many('bru.product.image', 'bru_collection_id')
    bru_id = fields.Integer()
    name = fields.Char()


class ProductImageInherit(models.Model):
    _inherit = 'product.image'

    already_resized = fields.Boolean()

    # @api.depends('already_resized')
    # def compute_resize_image(self):
    #     for rec in self:
    #         if not rec.already_resized and rec.image:
    #             rec.resize_image()
    #             rec.already_resized = True
    #
    # def resize_image(self):
    #     image = tools.image_resize_image_medium(self.image, size=(600, 400), avoid_if_small=True)
    #     self.image = image
