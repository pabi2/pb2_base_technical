# -*- coding: utf-8 -*-
from openerp.models import BaseModel
from openerp import api, models, _
import re


@api.v7
def copy_translations(self, cr, uid, old_id, new_id, context=None):
    return

BaseModel.copy_translations = copy_translations


class IRTranslation(models.Model):
    _inherit = "ir.translation"

    @api.model
    def to_do_translate(self, model, res_id, field_list, context):
        for field_name in field_list:
            self.with_context(context).translate_fields(model,
                                                        res_id,
                                                        field_name)
        return True

    @api.model
    def set_translation(self, model, res_id, field_list,
                            data, lang_code, context):
        for field_name in field_list:
            name = model + "," + field_name
            trans_search = self.search([('lang','=',context['lang']),
                                        ('name','=',name),
                                        ('type','=','model'),
                                        ('res_id', '=', res_id)])
            
            if trans_search and lang_code == context['lang']:
                trans_search.with_context(context).\
                    write({'value': data[field_name]})
            elif trans_search and lang_code != context['lang']:
                trans_search.with_context(context).\
                    write({'src': data[field_name], 'source': data[field_name]})
            
            trans_search = self.search([('lang','=','th_TH'),
                                            ('name','=',name),
                                            ('type','=','model'),
                                            ('res_id', '=', res_id)])
            trans_src = trans_search.src.replace(" ", "")
            trans_value = trans_search.value.replace(" ", "")
            pattern = re.compile(r"[a-zA-Z]")
            char_name = re.findall(pattern, data[field_name].replace(" ", ""))
            char_src = re.findall(pattern, trans_src)
            char_value = re.findall(pattern, trans_value)
            
            if trans_search and context['lang'] == 'th_TH' and not char_name:
                trans_search.with_context(lang="th_TH").\
                    write({'value': data[field_name]})
            if trans_search and context['lang'] == 'th_TH' and not char_name and not char_src:
                trans_search.with_context(lang="en_US").\
                    write({'src': data[field_name], 'source': data[field_name]})
                s = self.env[model].search(['id','=',res_id])
                s.write({field_name: data[field_name]})

        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
