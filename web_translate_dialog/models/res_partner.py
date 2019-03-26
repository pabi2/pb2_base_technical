# -*- coding: utf-8 -*-
from openerp import models, fields, api
import re

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        
        trans = self.env['ir.translation']
        for l in self:
            if 'name' in vals:
                name = "res.partner,name"
                trans_search = trans.search([('lang','=','th_TH'),
                                            ('name','=',name),
                                            ('type','=','model'),
                                            ('res_id', '=', l.id),
                                            ('state','=','to_translate')], limit=1)
                if trans_search:
                    trans_src = trans_search.src.replace(" ", "")
                    trans_value = trans_search.value.replace(" ", "")
                    pattern = re.compile(r"[a-zA-Z]")
                    char_name = re.findall(pattern, vals['name'].replace(" ", ""))
                    char_src = re.findall(pattern, trans_src)
                    char_value = re.findall(pattern, trans_value)
                    
                    update_src = False
                    if not char_src and not char_value and not char_name:
                        update_src = True
                        trans_search.write({
                            'value': vals['name'],
                            'src': vals['name']
                        })
                    
                    lang = self._context.get('lang', False)
                    if lang == 'en_US' and not update_src:
                        trans_search.write({
                            'src': vals['name']
                        })
        return res