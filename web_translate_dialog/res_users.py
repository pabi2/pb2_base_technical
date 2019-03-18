# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp import models, fields, api


class res_users(models.Model):
    _inherit = "res.users"
    
    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = self.env['ir.translation'].search([['name','=','res.users,name'],['type','=','model'],['res_id','=',rec.partner_id.id]], limit=1)
            if name:
                res.append((rec.id, '%s' % (name.value)))
            else:
                res.append((rec.id, '%s' % (rec.partner_id.name)))
        return res
