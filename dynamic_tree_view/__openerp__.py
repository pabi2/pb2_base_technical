
{
    'name': 'Dynamic Tree View',
    'version': '2.0', #fixed bug: 1. Now showing if no buttons exist on tree view, 2. Can select columns after changing tree view columns
    'author': 'Geo Technosoft',
    'category': 'Dynamic Tree View',
    'website': 'https://www.geotechnosoft.com',
    'summary': 'Dynamic Tree View',
    'description': """
    This module allow users to select fields that will show in tree view. Tree fields can hide and show on user's selection.
    """,
    'depends': ['web'],
    'data': ['views/tree_button.xml',],
    'qweb': ['static/src/xml/tree_view_button_view.xml'],
    'test': [],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
