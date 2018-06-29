# -*- coding: utf-8 -*-

from openerp import models, fields


class IRModel(models.Model):
    _inherit = 'ir.model'

    connection_id = fields.Many2one('db.connection', 'Connection',
                                    help='Select database connection to fetch from')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
