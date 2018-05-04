# -*- coding: utf-8 -*-
from openerp import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _create_invoice_line(self, cr, uid, inv_line_data,
                             inv_lines, po_line, context=None):
        inv_line_obj = self.pool.get('account.invoice.line')
        inv_line_id = inv_line_obj.create(cr, uid, inv_line_data,
                                          context=context)
        inv_lines.append(inv_line_id)
        po_line.write({'invoice_lines': [(4, inv_line_id)]})
        return inv_lines

    def action_invoice_create(self, cr, uid, ids, context=None):
        """Generates invoice for given ids of purchase orders and
        links that invoice ID to purchase order.
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """
        context = dict(context or {})

        inv_obj = self.pool.get('account.invoice')

        res = False
        uid_company_id =\
            self.pool.get('res.users').browse(cr, uid, uid,
                                              context=context).company_id.id
        for order in self.browse(cr, uid, ids, context=context):
            context.pop('force_company', None)
            if order.company_id.id != uid_company_id:
                # if the company of the document is different
                # than the current user company,
                # force the company in the context
                # then re-do a browse to read the property
                # fields for the good company.
                context['force_company'] = order.company_id.id
                order = self.browse(cr, uid, order.id, context=context)

            # generate invoice line correspond to PO line and
            # link that to created invoice (inv_id) and PO line
            inv_lines = []
            for po_line in order.order_line:
                acc_id = self._choose_account_from_po_line(cr, uid, po_line,
                                                           context=context)
                inv_line_data = self._prepare_inv_line(cr, uid,
                                                       acc_id,
                                                       po_line,
                                                       context=context)
                self._create_invoice_line(cr, uid,
                                          inv_line_data,
                                          inv_lines,
                                          po_line, context=context)  # Hook

            # get invoice data and create invoice
            inv_data = self._prepare_invoice(cr, uid, order, inv_lines,
                                             context=context)
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # compute the invoice
            inv_obj.button_compute(cr, uid, [inv_id],
                                   context=context,
                                   set_total=True)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)]})
            res = inv_id
        return res
