# -*- coding: utf-8 -*-
from openerp import models, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.model
    def multiple_reconcile_get_hook(self, line_total,
                                    move_id, name,
                                    company_currency, current_currency):
        return 0.00, []

    @api.model
    def multiple_reconcile_ded_amount_hook(self, line_total,
                                           move_id, name,
                                           company_currency, current_currency):
        return []

    @api.multi
    def writeoff_move_line_get(self, line_total,
                               move_id, name,
                               company_currency, current_currency):
        voucher_brw = self
        current_currency_obj = voucher_brw.currency_id or \
            voucher_brw.journal_id.company_id.currency_id
        list_move_line = []
        ded_amount = 0.00
        if not current_currency_obj.is_zero(line_total):
            diff = line_total
            account_id = False
            write_off_name = ''
            if voucher_brw.payment_option == 'with_writeoff':
                account_id = voucher_brw.writeoff_acc_id.id
                write_off_name = voucher_brw.comment
            elif voucher_brw.type in ('sale', 'receipt'):
                account_id = voucher_brw.partner_id.\
                    property_account_receivable.id
            else:
                account_id = voucher_brw.partner_id.\
                    property_account_payable.id

            ded_amount, reconcile_move_lines = \
                self.multiple_reconcile_get_hook(line_total, move_id,
                                                 name, company_currency,
                                                 current_currency)
            list_move_line.extend(reconcile_move_lines)
            if not voucher_brw.multiple_reconcile_ids:
                sign = voucher_brw.type == 'payment' and -1 or 1
                move_line = {
                    'name': write_off_name or name,
                    'account_id': account_id,
                    'move_id': move_id,
                    'partner_id': voucher_brw.partner_id.id,
                    'date': voucher_brw.date,
                    'credit': diff > 0 and diff or 0.0,
                    'debit': diff < 0 and -diff or 0.0,
                    'amount_currency': company_currency != current_currency and
                    (sign * -1 * voucher_brw.writeoff_amount) or False,
                    'currency_id': company_currency != current_currency and
                    current_currency or False,
                }
                list_move_line.append(move_line)
            elif voucher_brw.multiple_reconcile_ids and diff != ded_amount:
                reconcile_lines = self.multiple_reconcile_ded_amount_hook(
                    line_total, move_id, name,
                    company_currency, current_currency)
                list_move_line.extend(reconcile_lines)
            return list_move_line

    @api.model
    def action_move_line_create_hook(self, rec_list_ids):
        return

    @api.model
    def action_move_line_writeoff_hook(self, ml_writeoff):
        return

    @api.multi
    def action_move_line_create(self):
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']
        for voucher in self:
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(voucher.id)
            current_currency = self._get_current_currency(voucher.id)

            context = self._sel_context(voucher.id)
            ctx = context.copy()
            ctx.update({'date': voucher.date})

            move_id = move_pool.create(self.account_move_get(voucher.id))
            name = move_id.name
            move_line_id = move_line_pool.create(
                self.first_move_line_get(voucher.id, move_id.id,
                                         company_currency, current_currency))
            move_line_brw = move_line_id
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - voucher.with_context(ctx).\
                    _convert_amount(voucher.tax_amount, voucher.id)
            elif voucher.type == 'purchase':
                line_total = line_total + self.with_context(ctx).\
                    _convert_amount(voucher.tax_amount, voucher.id)

            line_total, rec_list_ids = self.voucher_move_line_create(
                voucher.id, line_total, move_id.id,
                company_currency, current_currency)

            ml_writeoff = voucher.writeoff_move_line_get(
                line_total, move_id.id, name, company_currency,
                current_currency)

            if voucher.multiple_reconcile_ids:  # hook
                self.action_move_line_writeoff_hook(ml_writeoff)  # hook
            else:  # hook
                if ml_writeoff:
                    move_line_pool.create(ml_writeoff[0])

            voucher.write({
                'move_id': move_id.id,
                'state': 'posted',
                'number': name,
            })

            if voucher.journal_id.entry_posted:
                move_id.post()
            self.action_move_line_create_hook(rec_list_ids)
        return True
