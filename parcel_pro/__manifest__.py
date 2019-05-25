# -*- coding: utf-8 -*-
{
    'name': "Parcel Pro",
    'summary': """ This module is used to create shipment and quotes from Parcel Pro
       """,
    'description': """
        Parcel Pro
    """,
    'author': "Ruby Chauhan",
    'website': "http://www.iqminds.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','sale'],
    'data': [
        'views/parcel_configuration_view.xml',
        'views/res_partner_view.xml',
        'views/res_users_view.xml',
        'views/sale_order_view.xml',
        'wizard/parcel_pro_api_wizard_view.xml',
        'data/parcel_configuration_data.xml',
        'views/cron_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}