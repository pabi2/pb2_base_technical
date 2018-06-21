# -*- coding: utf-8 -*-
##############################################################################

##############################################################################


from openerp import models, fields, api, _


class DBConnection(models.Model):
    _name = 'db.connection'
    _description = 'Database Connection Configuration'

    name = fields.Char('Connection Name', required=True)
    host = fields.Char('Server IP', help='Enter Host Address', required=True)
    database = fields.Char('Database', required=True)
    user = fields.Char('Database User')
    password = fields.Char('Database User Password')
    active = fields.Boolean('Active?', default=True)
    description = fields.Text('Description', help='Enter Comments')

    _sql_constraints = [
        ('host_database_uniq', 'unique (host, database)',
         'Database for this server IP already exists!')
    ]

    # @api.multi
    # def name_get(self):
    #     '''Method to display database and host'''
    #     return [(rec.id, ' [' + rec.database + '] ' + rec.host) for rec in self]
