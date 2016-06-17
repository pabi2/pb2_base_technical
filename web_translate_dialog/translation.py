from openerp.tools import translate
from openerp import api, models, _

class IRTranslation(models.Model):
    _inherit = "ir.translation"

    @api.model
    def to_do_translate(self, model, res_id, field_list, context):
        for field_name in field_list:
            self.with_context(context).translate_fields(model, res_id, field_name)
        return True
    
#     @api.model
#     def set_translation(self, model, res_id, field_list, data, lang_code, context):
#         print "model__________",model
#         print "res_id_________",res_id
#         print "field_list_____",field_list
#         print "data___________",data
#         print "context________",context
#         print "lang_code______",lang_code
#         
#         for field_name in field_list:
#             name = model + "," + field_name
#             print "name................",name
#             trans_search = self.search([('lang','=',context['lang']),
#                                         ('name','=',name),
#                                         ('type','=','model'),
#                                         ('res_id', '=', res_id)])
#             print "trans_search...................",trans_search
#             if trans_search and lang_code == 'en_US':
#                 trans_search.write({'source': data[field_name]})
#                 print "=========trans_search.src====",trans_search, trans_search.src, trans_search.value
#                 trans_val = translate(self._cr, name, 'model', context['lang'], data[field_name])
#                 res_data = self.env[model].browse(res_id)
#                 print "res_data.......",res_data
# #                 res_data.write({field_name : trans_val })
#                 print "trans_val.....................",trans_val
#         return