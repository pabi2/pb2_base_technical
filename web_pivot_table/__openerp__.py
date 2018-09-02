
{
    'name': 'Advanced Pivot Table',
    'version': '8.0.0.1',
    'author': 'Geo Technosoft',
    'sequence':'10',
    'category': 'Hidden',
    'website': 'https://www.geotechnosoft.com',
    'summary': 'Custom Pivot Table',
    'description': """
    This module will add new features pivot table like click on td.

Example to pass context in action
    {'ctx_module_name': 'account',
     'ctx_view_xml_id': 'view_move_line_tree',
     'ctx_view_form_xml_id': 'view_move_line_form'}

    """,
    'depends': ['web'],
    'data': ['views/webclient_templates.xml'],
    'qweb': ['static/src/xml/*.xml'],
    'test': [],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': True,

}
