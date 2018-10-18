# -*- coding: utf-8 -*-
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def line_get_convert(self, line, part, date):
        """ Overwrite just to ensure name length """
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': part,
            'name': line['name'],
            'date': date,
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_lines': line.get('analytic_lines', []),
            'amount_currency': line['price'] > 0 and
            abs(line.get('amount_currency', False)) or
            -abs(line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'tax_code_id': line.get('tax_code_id', False),
            'tax_amount': line.get('tax_amount', False),
            'ref': line.get('ref', False),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uos_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
        }


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def _anglo_saxon_sale_move_lines(self, i_line, res):
        """ Overwrite method, simpley to ensure that name is > 64 char """
        inv = i_line.invoice_id
        fiscal_pool = self.env['account.fiscal.position']
        fpos = inv.fiscal_position or False
        company_currency = inv.company_id.currency_id.id

        if i_line.product_id.type != 'service' and \
                i_line.product_id.valuation == 'real_time':
            # debit account dacc will be the output account
            # first check the product, if empty check the category
            dacc = i_line.product_id.property_stock_account_output and \
                i_line.product_id.property_stock_account_output.id
            if not dacc:
                dacc = i_line.product_id.categ_id.\
                    property_stock_account_output_categ and \
                    i_line.product_id.categ_id.\
                    property_stock_account_output_categ.id
            # in both cases the credit account cacc will be the expense account
            # first check the product, if empty check the category
            cacc = i_line.product_id.property_account_expense and \
                i_line.product_id.property_account_expense.id
            if not cacc:
                cacc = i_line.product_id.categ_id.\
                    property_account_expense_categ and i_line.product_id.\
                    categ_id.property_account_expense_categ.id
            if dacc and cacc:
                if i_line.move_id:
                    price_unit = i_line.move_id.price_unit
                else:
                    price_unit = i_line.product_id.standard_price
                from_unit = i_line.product_id.uom_id.id
                to_unit = i_line.uos_id.id
                price_unit = self.env['product.uom']._compute_price(
                    from_unit, price_unit, to_uom_id=to_unit)
                return [
                    {
                        'type': 'src',
                        'name': i_line.name,
                        'price_unit': price_unit,
                        'quantity': i_line.quantity,
                        'price': self._get_price(inv, company_currency,
                                                 i_line, price_unit),
                        'account_id': dacc,
                        'product_id': i_line.product_id.id,
                        'uos_id': i_line.uos_id.id,
                        'account_analytic_id': False,
                        'taxes': i_line.invoice_line_tax_id,
                    },
                    {
                        'type': 'src',
                        'name': i_line.name,
                        'price_unit': price_unit,
                        'quantity': i_line.quantity,
                        'price': -1 * self._get_price(inv, company_currency,
                                                      i_line, price_unit),
                        'account_id': fiscal_pool.map_account(fpos, cacc),
                        'product_id': i_line.product_id.id,
                        'uos_id': i_line.uos_id.id,
                        'account_analytic_id': i_line.account_analytic_id.id,
                        'taxes': i_line.invoice_line_tax_id,
                    },
                ]
        return []

    @api.model
    def move_line_get_item(self, line):
        """ Overwrite just to ensure name length """
        return {
            'type': 'src',
            'name': line.name.split('\n')[0],
            'price_unit': line.price_unit,
            'quantity': line.quantity,
            'price': line.price_subtotal,
            'account_id': line.account_id.id,
            'product_id': line.product_id.id,
            'uos_id': line.uos_id.id,
            'account_analytic_id': line.account_analytic_id.id,
            'taxes': line.invoice_line_tax_id,
        }
