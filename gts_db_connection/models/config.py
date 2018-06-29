# -*- coding: utf-8 -*-

from openerp import models, fields


class DBConnection(models.Model):
    _name = 'db.connection'
    _description = 'Database Connection Configuration'

    name = fields.Char('Connection Name', required=True, help='Small Description')
    host = fields.Char('Server IP', required=True,
                       help='Enter Host/IP Address, do not use localhost instead '
                            'find IP using ifconfig command and use it')
    database = fields.Char('Database Name', required=True)
    user = fields.Char('Database User', required=True)
    password = fields.Char('Database User Password', required=True)
    port = fields.Char('Database Port', required=True,
                       help='Enter port on which database is running')
    active = fields.Boolean('Active?', default=True)
    description = fields.Text('Description', help='Enter Comments, if any')

    _sql_constraints = [
        ('host_database_uniq', 'unique (host, database)',
         'Database for this server IP already exists!')
    ]
