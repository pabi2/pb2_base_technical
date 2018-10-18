# -*- coding: utf-8 -*-

{
    'name': 'Account Invoice Hooks',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': '''

Add hook point in
- account_invoice.line_get_convert()
- account_invoice_line._anglo_saxon_sale_move_lines()
- account_invoice_line.move_line_get_item()

''',
    'author': "Ecosoft",
    'website': 'http://ecosoft.co.th',
    'depends': ['account_anglo_saxon', 'account'],
    'data': [],
    'installable': True,
}
