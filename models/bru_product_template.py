from odoo import models, fields, _, api
from odoo.addons.queue_job.job import job
import json
import requests
import base64


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_tw_id = fields.Integer()
    bru_image_info = fields.One2many('bru.product.image', 'odoo_product_id')
    bru_collection_id = fields.Many2one('bru.collection')

    def sync_product_bru(self):
        for page in range(0, 30):
            if page == 0:
                self.with_delay(description=f'batch count for sync').sync_product_batch(1, 11)
            else:
                self.with_delay(description=f'batch count for sync').sync_product_batch(page * 10, page * 10 + 11)

    @api.multi
    @job
    def sync_product_batch(self, from_page, to_page):
        for page in range(from_page, to_page):
            self.with_delay(description=f'Page sync product {page}').sync_product_bru_url(page, 50)

    @api.multi
    @job
    def sync_product_bru_url(self, page, size):
        url = f"https://api.twinbru.com/products?page={page}&pageSize={size}"
        payload = {}
        headers = {
            'Cache-Control': 'no-cache',
            'Api-Version': 'v1',
            'Ocp-Apim-Subscription-Key': 'd91ae39b7808439585bc82a7aaba1a8f',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiJicnV0ZXgiLCJhY2Nlc3NvciI6ImFwaU1hbmFnZW1lbnQiLCJhY2NvdW50SWQiOiJCUlUtMjUxMC0xMDA0NDIiLCJpYXQiOjE1MTYyMzkwMjIsImV4cCI6MTk0MDY4NTg4Nn0.pZ4yeHfU7nt0eiOFaAaI-qfusW1VAiRrPMEiyqi3UGs'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
        else:
            raise UserWarning('Please check connection')
        for product_data in data.get('results'):
            bru_product_id = product_data.get('item').get('id')
            # check duplicate product sync from twinbru
            is_duplicate_product = self.check_duplicate_product_tw(bru_product_id)
            if is_duplicate_product:
                continue
            exits_product = self.env['product.template'].search([('product_tw_id', '=', bru_product_id)])
            if exits_product:
                for product in exits_product:
                    product.bru_image_info.unlink()
                    product.public_categ_ids.unlink()
                    product.product_image_ids.unlink()
                    product.unlink()
                # continue
                # update_product here

            self.with_delay(description=f'Sync product {bru_product_id}').create_product_tw(product_data.get('item'))

    @api.multi
    @job
    def purpose_bru_image(self, tw_sale_id, odoo_product):
        # create bru product image info and update sequence
        image_obj = self.env['bru.product.image']
        bru = self.env['bru.connection'].search([('name', '=', 'TEST')], limit=1)
        url = f"https://api.twinbru.com/ods/item-read/v1/api/Search/Asset?filter=salesId.eq.{tw_sale_id}"
        response = requests.request("GET", url, headers=bru.get_header('asset'))
        if response.status_code == 200:
            data = response.json()
        else:
            return
        total_page = data.get('totalPageCount')
        page = data.get('page')
        for page_number in range(page, total_page + 1):
            data_image = self.get_data_product_image(tw_sale_id, page_number)
            for image in data_image.get('results'):
                bru_id = image.get('item').get('itemId')
                render_scene = image.get('item').get('renderScene')
                asset_type = image.get('item').get('assetType')
                image_obj.create({
                    'bru_id': bru_id,
                    'key': image.get('item').get('renditions')[0].get('key') if image.get('item').get('renditions') else '',
                    'bru_product_id': tw_sale_id,
                    'odoo_product_id': odoo_product.id or '',
                    'name': image.get('assetName') or '',
                    'asset_type': asset_type or '',
                    'render_scene': render_scene or '',
                })
        odoo_product.bru_image_info.update_image_sequence()
        odoo_product.with_delay(description=f'Sync image for product {tw_sale_id}').get_image_by_product()

    @api.multi
    @job
    def get_image_by_product(self):
        image_obj = self.env['product.image']
        sequence = 0
        for i in self.bru_image_info:
            image_bru_id = self.bru_image_info.filtered(lambda r: r.sequence == sequence)
            if not image_bru_id:
                continue
            image_endpoint = image_bru_id.key
            image_data = self.get_image_from_bru(image_endpoint)
            if sequence == 0:
                if self.image:
                    self.image = False
                self.image = image_data
            image_obj.create({
                'image': image_data,
                'product_tmpl_id': self.id,
                'name': self.name,
                'sequence': sequence,
                'already_resized': True
            })
            sequence += 1
            if not image_data:
                continue

    def get_image_from_bru(self, key):
        bru = self.env['bru.connection'].search([('name', '=', 'TEST')], limit=1)
        url = f"https://api.twinbru.com/ods/asset-read/v1/api/Assets/Asset/{key}"
        response = requests.request("GET", url, headers=bru.get_header('asset'))
        if response.status_code == 200:
            data = base64.b64encode(response.content)
            return data

    def get_data_product_image(self, tw_sale_id, page):
        bru = self.env['bru.connection'].search([('name', '=', 'TEST')], limit=1)
        url = f"https://api.twinbru.com/ods/item-read/v1/api/Search/Asset?filter=salesId.eq.{tw_sale_id}&page={page}"
        response = requests.request("GET", url, headers=bru.get_header('asset'))
        if response.status_code == 200:
            return response.json()
        else:
            return

    def get_product_collection_image(self, bru_id):
        bru = self.env['bru.connection'].search([('name', '=', 'TEST')], limit=1)
        url = f"https://api.twinbru.com/ods/item-read/v1/api/Search/Asset?filter=assetType.eq.RoomShot/collection.eq.{bru_id}"
        response = requests.request("GET", url, headers=bru.get_header('asset'))
        if response.status_code == 200:
            return response.json()
        else:
            return

    @api.multi
    @job
    def get_or_create_bru_collection(self, product, odoo_product):
        # image data for collection without image
        image_obj = self.env['bru.product.image']
        collection = self.env['bru.collection']
        collection_exist = self.env['bru.collection'].search([('bru_id', '=', product.get('collectionId'))])
        if collection_exist:
            odoo_product.write({
                'bru_collection_id': collection_exist.id,
            })
            return True
        data_image = self.get_product_collection_image(product.get('collectionId'))
        collection_id = collection.create({
            'bru_id': product.get('collectionId'),
            'name': product.get('collectionName')
        })
        for image in data_image.get('results'):
            bru_id = image.get('item').get('itemId')
            asset_type = image.get('item').get('assetType')
            image_obj.create({
                'bru_id': bru_id,
                'key': image.get('item').get('renditions')[0].get('key'),
                'name': image.get('item').get('assetName'),
                'asset_type': asset_type,
                'bru_collection_id': collection_id.id
            })
        odoo_product.write({
            'bru_collection_id': collection_id.id,
        })
        return True

    @api.multi
    @job
    def create_product_tw(self, product):
        list_categ = self.get_category_product_tw(product)
        bru_collection = product.get('collectionId')
        name = product.get('designName') + ' ' + product.get('productName')
        odoo_product = self.create({
            'public_categ_ids': [(6, 0, list_categ)],
            'product_brand_id': self.get_brand_tw(),
            'name': name,
            'product_tw_id': product.get('id'),
            'type': 'product',
            'barcode': 'BRU00' + product.get('id')
        })
        self.set_product_attribute_line_tw(odoo_product, product)
        self.with_delay(description=f'Get or Create Bru Collection bru id{bru_collection}').get_or_create_bru_collection(product, odoo_product)
        self.with_delay(description='Purpose bru image for sync').purpose_bru_image(product.get('id'), odoo_product)
        return odoo_product

    def get_brand_tw(self):
        brand = self.env['product.brand'].search([('name', '=', 'Bru')])
        if brand:
            return brand.id
        brand = self.env['product.brand'].create({
            'name': 'Bru'
        })
        return brand.id

    def get_category_product_tw(self, data):
        categ_obj = self.env['product.public.category']
        cate_els_name = data.get('collectionName')
        telas = categ_obj.search([('name', '=', 'Telas')], limit=1)
        if not telas:
            telas = categ_obj.create({
                'name': 'Telas',
                'sequence': 0
            })
        if cate_els_name == 'Telas' or not cate_els_name:
            return [telas.id]
        cate_els = categ_obj.search([('name', '=', cate_els_name)], limit=1)
        if not cate_els:
            cate_els = categ_obj.create({
                'name': cate_els_name,
                'sequence': 1
            })
        return [telas.id, cate_els.id]

    def set_product_attribute_line_tw(self, odoo_product, data):
        line_obj = self.env['product.attribute_desc.lines']
        line_ids = []
        attribute_list = self.df_attribute_from_data(data)
        for attribute in attribute_list:
            if not attribute[0] or not attribute[1]:
                continue
            att, value = attribute[0], [attribute[1]] if type(attribute[1]) != list else attribute[1]
            for value_id in value:
                att_id, value_ids = self.get_attribute_tw(attribute[0], str(value_id))
                tmpline = line_obj.search([('product_tmpl_id', '=', odoo_product.id), ('attribute_id', '=', att_id)], limit=1)
                if value_ids[0] in tmpline.value_ids.ids:
                    continue
                line_ids.append(line_obj.create({
                    'product_tmpl_id': odoo_product.id,
                    'attribute_id': att_id,
                    'value_ids': [(6, 0, value_ids)]
                }).id)
        return line_ids

    def get_attribute_tw(self, att_name, att_value):
        att_obj = self.env['product.attribute']
        att_value_obj = self.env['product.attribute.value']
        att = att_obj.search([('name', '=', att_name)])
        if not att:
            att = att_obj.create({
                'name': att_name,
                'type': 'select' if att_name not in ['Color', 'Family Color'] else 'color'
            })
        value = att_value_obj.search([('name', '=', att_value), ('attribute_id', '=', att.id)])
        if not value:
            value = att_value_obj.create({
                'name': att_value,
                'attribute_id': att.id
            })

        return att.id, value.ids

    @staticmethod
    def df_attribute_from_data(data):
        return [
            ('Brand', data.get('brand')),
            ('Filament or Staple', data.get('filament_or_staple')),
            ('Width (cm)', data.get('selvedge_full_width_cm')),
            ('Width (inches)', data.get('selvedge_full_width_inch')),
            ('Useable Width (cm)', data.get('selvedge_useable_width_cm')),
            ('Useable Width (inch)', data.get('selvedge_useable_width_inch')),
            ('Wizenbeek', data.get('wyzenbeek_cotton_duck')),
            ('Weight (m2)', data.get('weight_g_per_m_squared')),
            ('Contents', data.get('total_composition')),
            ('Repeat Direction', data.get('repeats')),
            ('Quality', data.get('quality')),
            ('Fabric Design', data.get('design_type')),
            ('Finish Treatment', data.get('finish')),
            ('Bleach', data.get('care_code_bleach')),
            ('Iron', data.get('care_code_iron')),
            ('Tumble Dry', data.get('care_code_tumble_dry')),
            ('Washable', data.get('care_code_washable_celsius')),
            ('Fabric Type', data.get('composition_type')),
            ('Application', data.get('end_use')),
            ('Color', data.get('main_colour_type_description')),
            ('Family Color', 'other')
        ]

    def check_duplicate_product_tw(self, product_tw_id):
        product_obj = self.env['product.template']
        product_tmpl_ids = product_obj.search([('product_tw_id', '=', product_tw_id)])
        if len(product_tmpl_ids) > 1:
            return True
        return False
