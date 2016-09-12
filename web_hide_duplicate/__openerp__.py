###
#
#   This file is part of odoo-addons.
#
#   odoo-addons is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   odoo-addons is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##

{
    'name': 'Hide duplicate',
    'author': 'Aristobulo Meneses',
    'version': '0.2',
    'description': '''
Allows to hide duplicate button under <More> section
================================================================================

HOW-TO:

Go to desired form view definition and duplicate="false" attribute.

Example:

<form string="Users" version="7.0" duplicate="false">
    ''',
    'category': 'web',
    'depends': ['web', ],
    'data': ['views/hide_duplicate.xml', ],
    'installable': True,
    'auto_install': False,
    'web': True,
}
