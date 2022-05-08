from odoo import models, fields, _
import requests
from odoo.exceptions import AccessError, UserError, ValidationError

name = 'TEST'
Token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiJicnV0ZXgiLCJhY2Nlc3NvciI6ImFwaU1hbmFnZW1lbnQiLCJhY2NvdW50SWQiOiJCUlUtMjUxMC0xMDA0NDIiLCJpYXQiOjE1MTYyMzkwMjIsImV4cCI6MTk0MDY4NTg4Nn0.pZ4yeHfU7nt0eiOFaAaI-qfusW1VAiRrPMEiyqi3UGs'
product_url = 'https://api.twinbru.com'
ods_asset_url = 'https://api.twinbru.com/ods/item-read/v1/api'
ods_asset = '970d991aeb77495fa7f289d28c7e350a'
product = 'd91ae39b7808439585bc82a7aaba1a8f'

class BruConnection(models.Model):
    _name = 'bru.connection'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    bearer_token = fields.Char(string='Token', required=True)
    subscription_key = fields.One2many('bru.subscription.key', 'bru_connection_id', string='subscription_key')
    url_product = fields.Char('Product Url')
    url_asset = fields.Char('ODS Asset Url')
    product_id = fields.Text()
    total_product = fields.Integer()

    def test_connection(self):
        url = "https://api.twinbru.com/products/68298"
        url_ods = "https://api.twinbru.com/ods/asset-read/v1/api/Assets/Asset/eb883017-c051-418b-b7af-ac37008515bb/Large"
        try:
            headers = self.get_header()
        except:
            raise ValidationError(_("Failed"))
        r = requests.request("GET", url, headers=headers)
        r_ods = requests.request("GET", url_ods, headers=self.get_header('asset'))
        if r.status_code == 200 and r_ods.status_code == 200:
            self.active_success = True
            self.total_product = r.json().get('totalItemCount')
        else:
            raise ValidationError(_("Connection Failed"))
        raise ValidationError(_("Connecting"))

    def get_header(self, type='product'):
        headers = {
            'Cache-Control': 'no-cache',
            'Api-Version': 'v1',
            'Ocp-Apim-Subscription-Key': '',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        if type == 'product':
            headers.update({
                "Ocp-Apim-Subscription-Key": self.subscription_key.filtered(lambda r: r.type_key == 'product')[0].subscription_key,
            })
        else:
            headers.update({
                "Ocp-Apim-Subscription-Key": self.subscription_key.filtered(lambda r: r.type_key == 'asset')[0].subscription_key,
            })
        return headers

    def sync_product_bru(self):
        self.env['product.template'].sync_product_bru()


class BruSubscriptionKey(models.Model):
    _name = 'bru.subscription.key'

    bru_connection_id = fields.Many2one('bru.connection', string='Bru Connection')
    subscription_key = fields.Char(string='subscription_key')
    type_key = fields.Selection(
        [('asset', 'ODS Bru Assets'),
         ('product', 'Bru Product')],
        string='Type'
    )
