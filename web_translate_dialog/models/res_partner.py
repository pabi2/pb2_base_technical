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
                                            ('res_id', '=', l.id)], limit=1)
                if trans_search:
                    lang = self._context.get('lang', False)
                    trans_src = trans_search.src.replace(" ", "")
                    trans_value = trans_search.value.replace(" ", "")
                    pattern = re.compile(r"[a-zA-Z]")
                    char_name = re.findall(pattern, vals['name'].replace(" ", ""))
                    char_src = re.findall(pattern, trans_src)
                    char_value = re.findall(pattern, trans_value)
                    
                    # Case Thai All
                    if not char_src and not char_value and not char_name:
                        trans_search.write({
                            'value': vals['name'],
                            'src': vals['name']
                        })
                    else:
                        # Case en_US update 'src' away
                        if lang == 'en_US':
                            trans_search.write({
                                'src': vals['name']
                            })
                            # name thai and value(old) thai >> update new value 
                            if not char_name and not char_value:
                                trans_search.write({
                                'value': vals['name']
                            })
        return res