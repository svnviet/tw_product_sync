{
    'name': 'TwinBru Connection',
    'version': '1.0.0',
    'category': 'Sale',
    'summary': 'Twinbru Product in Odoo',

    'author': 'Vietnt',
    'depends': ['website_sale','sh_message_wizard','queue_job'],
    'data': ['views/bru_connection.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'active': False,
}
