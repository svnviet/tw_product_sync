{
    'name': 'TwinBru Connection',
    'version': '1.0.0',
    'category': 'Sale',
    'summary': 'Twinbru Product in Odoo',

    'author': '',
    'depends': ['website_sale', 'sh_message_wizard', 'queue_job', 'website_attach_pdf', 'website_extended', 'website_sale'],
    'data': ['views/bru_connection.xml',
             'views/product_template_views.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,
}
