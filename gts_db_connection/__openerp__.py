# -*- coding: utf-8 -*-
# Geo Technosoft Pvt Ltd.


{
    'name': 'GTS Database Connection',
    'version': '8.0.0.1',
    'author': 'Geo Technosoft',
    'sequence':'10',
    'category': 'Tools',
    'website': 'https://www.geotechnosoft.com',
    'summary': 'Database Load Balancing',
    'description': """
        This module will allow fetching reports from another databases.
    """,
    'depends': ['base'],
    'data': [
        'views/config_view.xml',
        'views/ir_model_view.xml',
        'security/ir.model.access.csv',
    ],
}
