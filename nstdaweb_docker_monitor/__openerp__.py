# -*- coding: utf-8 -*-
{
    # ----------------------- Edit --------------
    'name': "NSTDA-WEB :: Docker Monitor",
    'summary': "Webservice แสดงสถานะ Monitor",
    'author': "Siam Nakaphong, Jakkrich Changgon",
    'description': """
==========
HOW TO USE
==========
https://<Domain Name>/app/nstdaweb_docker_monitor_port/get_port?api_key=<api_key>&api_secret=<api_secret>&m=<module_name>
    """,
    'website': 'https://o.nstda.or.th/app/nstdaweb_docker_monitor_port/get_port?api_key=<api_key>&api_secret=<api_secret>&m=<module_name>',
    'depends': ['base', 'mail', 'base_concurrency'],
    'data': [
        'security/ir.model.access.csv',
        'views/nstdaweb_docker_monitor_source.xml',
        'views/nstdaweb_docker_monitor_port.xml',
        'views/nstdaweb_docker_monitor_menu.xml'
    ],
    # ----------------------- NOT Edit --------------
    'category': 'NSTDA',
    'author': 'ICT Team',
    'installable': True,
    'auto_install': False,
}
