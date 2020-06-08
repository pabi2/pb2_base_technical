# -*- coding: utf-8 -*-
{
    # ----------------------- Edit --------------
    'name': "NSTDA-WEB :: Report API",
    'summary': "Webservice Jaster Report API",
    'author': "Siam Nakaphong, Jakkrich Changgon",
    'description': """
==========
HOW TO USE
==========

# api_key='xxxxx'

# api_secret='xxxxx'

# m='nstda_gnc'

# odootesturl='o-test-28001.intra.nstda.or.th'

# dbport='29001'

https://o.nstda.or.th/app/nstdaweb_report_api/clone_jasper?api_key=None&api_secret=None&m=None&odootesturl=None&dbport=None
    """,
    'website': 'https://o.nstda.or.th',
    'depends': ['base','nstdaconf_report', 'nstdaweb_docker_monitor'],
    'data': [
    ],
    # ----------------------- NOT Edit --------------
    'category': 'NSTDA',
    'author': 'ICT Team',
    'installable': True,
    'auto_install': False,
}
