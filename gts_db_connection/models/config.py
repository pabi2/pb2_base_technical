# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning

import psycopg2
import logging
_logger = logging.getLogger('DB Connection')


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
         _('Database for this server IP already exists!'))
    ]

    @api.multi
    def test_connection(self):
        ''' Function to test connection '''
        for conn in self:
            try:
                dsn = 'host=%s port=%s user=%s password=%s dbname=%s' \
                       % (str(conn.host).strip(), str(conn.port).strip(),
                          str(conn.user).strip(), str(conn.password).strip(),
                          str(conn.database).strip())
                psycopg2.connect(dsn=dsn)
                _logger.info(
                    'Connection to the database %s is successful'
                    % (conn.database,))
                raise Warning(
                    _('Connection to the database %s is successful!')
                    % (conn.database,))
            except psycopg2.Error:
                _logger.exception(
                    'Connection to the database %s is unsuccessful'
                    % (conn.database,))
                raise Warning(
                    _('Connection to the database %s is unsuccessful!')
                    % (conn.database,))
