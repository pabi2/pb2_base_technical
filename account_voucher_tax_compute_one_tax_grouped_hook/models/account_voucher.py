# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import Warning as UserError


class AccountVoucherTax(models.Model):
    _inherit = "account.voucher.tax"

    @api.model
    def _get_one_tax_key(self, val, line_id):
        key = (val['invoice_id'],
               val['tax_code_id'],
               val['base_code_id'],
               val['account_id'])
        return val, key

    @api.model
    def _compute_one_tax_grouped(self, taxes, voucher, voucher_cur,
                                 invoice, invoice_cur, company_currency,
                                 journal, line_sign, payment_ratio,
                                 line, revised_price):
        tax_gp = {}
        tax_obj = self.env['account.tax']

        for tax in taxes:
            # For Normal
            val = {}
            val['voucher_id'] = voucher.id
            val['invoice_id'] = invoice.id
            val['tax_id'] = tax['id']
            val['name'] = tax['name']
            val['amount'] = self._to_voucher_currency(
                invoice, journal,
                (tax['amount'] *
                 payment_ratio *
                 line_sign))
            val['manual'] = False
            val['sequence'] = tax['sequence']
            val['base'] = self._to_voucher_currency(
                invoice, journal,
                voucher_cur.round(
                    tax['price_unit'] * line.quantity) *
                payment_ratio * line_sign)
            # For Undue
            vals = {}
            vals['voucher_id'] = voucher.id
            vals['invoice_id'] = invoice.id
            vals['tax_id'] = tax['id']
            vals['name'] = tax['name']
            vals['amount'] = self._to_invoice_currency(
                invoice, journal,
                (-tax['amount'] *
                 payment_ratio *
                 line_sign))
            vals['manual'] = False
            vals['sequence'] = tax['sequence']
            vals['base'] = self._to_invoice_currency(
                invoice, journal,
                voucher_cur.round(
                    -tax['price_unit'] * line.quantity) *
                payment_ratio * line_sign)

            # Register Currency Gain for Normal
            val['tax_currency_gain'] = -(val['amount'] + vals['amount'])
            vals['tax_currency_gain'] = 0.0

            # Check the if services, which has been using undue account
            # This time, it needs to cr: non-undue acct and dr: undue acct
            tax1 = tax_obj.browse(tax['id'])
            is_wht = tax1.is_wht
            # -------------------> Adding Tax for Posting
            if is_wht:
                # Check Threshold first
                base = invoice_cur.compute((revised_price * line.quantity),
                                           company_currency)
                t = tax_obj.browse(val['tax_id'])
                if abs(base) and abs(base) < t.threshold_wht:
                    continue
                # For WHT, change sign.
                val['base'] = -val['base']
                val['amount'] = -val['amount']
                # Case Withholding Tax Dr.
                if voucher.type in ('receipt', 'payment'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        tax['base_sign'],
                        company_currency) * payment_ratio
                    val['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        tax['tax_sign'],
                        company_currency) * payment_ratio
                    val['account_id'] = (tax['account_collected_id'] or
                                         line.account_id.id)
                    val['account_analytic_id'] = \
                        tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        tax['ref_base_sign'],
                        company_currency) * payment_ratio
                    val['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        tax['ref_tax_sign'],
                        company_currency) * payment_ratio
                    val['account_id'] = (tax['account_paid_id'] or
                                         line.account_id.id)
                    val['account_analytic_id'] = \
                        tax['account_analytic_paid_id']

                if not val.get('account_analytic_id', False) and \
                        line.account_analytic_id and \
                        val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id
                val, key = self._get_one_tax_key(val, line.id)  # hook
                if not (key in tax_gp):
                    tax_gp[key] = val
                    tax_gp[key]['amount'] = tax_gp[key]['amount']
                    tax_gp[key]['base'] = tax_gp[key]['base']
                    tax_gp[key]['base_amount'] = tax_gp[key]['base_amount']
                    tax_gp[key]['tax_amount'] = tax_gp[key]['tax_amount']
                    tax_gp[key]['tax_currency_gain'] = 0.0  # No gain for WHT
                else:
                    tax_gp[key]['amount'] += val['amount']
                    tax_gp[key]['base'] += val['base']
                    tax_gp[key]['base_amount'] += val['base_amount']
                    tax_gp[key]['tax_amount'] += val['tax_amount']
                    tax_gp[key]['tax_currency_gain'] += 0.0  # No gain for WHT

            # --> Adding Tax for Posting 1) Contra-Undue 2) Non-Undue
            elif tax1.is_undue_tax:
                # First: Do the Cr: with Non-Undue Account
                refer_tax = tax1.refer_tax_id
                if not refer_tax:
                    raise UserError(
                        _('Undue Tax require Counterpart Tax when setup'))
                # Change name to refer_tax_id
                val['name'] = refer_tax.name
                if voucher.type in ('receipt', 'payment'):
                    val['tax_id'] = refer_tax and refer_tax.id or val['tax_id']
                    val['base_code_id'] = refer_tax.base_code_id.id
                    val['tax_code_id'] = refer_tax.tax_code_id.id
                    val['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        refer_tax.base_sign,
                        company_currency) * payment_ratio
                    val['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        refer_tax.tax_sign,
                        company_currency) * payment_ratio
                    val['account_id'] = (refer_tax.account_collected_id.id or
                                         line.account_id.id)
                    val['account_analytic_id'] = \
                        refer_tax.account_analytic_collected_id.id
                else:
                    val['tax_id'] = refer_tax and refer_tax.id or val['tax_id']
                    val['base_code_id'] = refer_tax.ref_base_code_id.id
                    val['tax_code_id'] = refer_tax.ref_tax_code_id.id
                    val['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        refer_tax.ref_base_sign,
                        company_currency) * payment_ratio
                    val['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        refer_tax.ref_tax_sign,
                        company_currency) * payment_ratio
                    val['account_id'] = (refer_tax.account_paid_id.id or
                                         line.account_id.id)
                    val['account_analytic_id'] = \
                        refer_tax.account_analytic_paid_id.id

                if not val.get('account_analytic_id', False) and \
                        line.account_analytic_id and \
                        val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id
                val, key = self._get_one_tax_key(val, line.id)  # hook
                if not (key in tax_gp):
                    tax_gp[key] = val
                else:
                    tax_gp[key]['amount'] += val['amount']
                    tax_gp[key]['base'] += val['base']
                    tax_gp[key]['base_amount'] += val['base_amount']
                    tax_gp[key]['tax_amount'] += val['tax_amount']
                    tax_gp[key]['tax_currency_gain'] += \
                        val['tax_currency_gain']

                # Second: Do the Dr: with Undue Account
                if voucher.type in ('receipt', 'payment'):
                    vals['base_code_id'] = tax['base_code_id']
                    vals['tax_code_id'] = tax['tax_code_id']
                    vals['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        tax['base_sign'],
                        company_currency) * payment_ratio
                    vals['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        tax['tax_sign'],
                        company_currency) * payment_ratio
                    # USE UNDUE ACCOUNT HERE
                    vals['account_id'] = \
                        (tax1.account_collected_id.id or
                         line.account_id.id)
                    vals['account_analytic_id'] = \
                        tax['account_analytic_collected_id']
                else:
                    vals['base_code_id'] = tax['ref_base_code_id']
                    vals['tax_code_id'] = tax['ref_tax_code_id']
                    vals['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        tax['ref_base_sign'],
                        company_currency) * payment_ratio
                    vals['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        tax['ref_tax_sign'],
                        company_currency) * payment_ratio
                    # USE UNDUE ACCOUNT HERE
                    vals['account_id'] = \
                        (tax1.account_paid_id.id or
                         line.account_id.id)
                    vals['account_analytic_id'] = \
                        tax['account_analytic_paid_id']

                if not vals.get('account_analytic_id') and \
                        line.account_analytic_id and \
                        vals['account_id'] == line.account_id.id:
                    vals['account_analytic_id'] = line.account_analytic_id.id
                vals, key = self._get_one_tax_key(vals, line.id)  # hook
                if not (key in tax_gp):
                    tax_gp[key] = vals
                else:
                    tax_gp[key]['amount'] += vals['amount']
                    tax_gp[key]['base'] += vals['base']
                    tax_gp[key]['base_amount'] += vals['base_amount']
                    tax_gp[key]['tax_amount'] += vals['tax_amount']
                    tax_gp[key]['tax_currency_gain'] += \
                        vals['tax_currency_gain']
        return tax_gp
