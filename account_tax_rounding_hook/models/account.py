# -*- coding: utf-8 -*-
from openerp import models, api


class account_tax(models.Model):
    """
    OverWrite Tax Account
    """
    _inherit = 'account.tax'

    @api.model
    def _get_tax_calculation_rounding_method(self, taxes):
        if taxes and taxes[0].company_id.tax_calculation_rounding_method:
            return taxes[0].company_id.tax_calculation_rounding_method
        else:
            return False

    @api.v7
    def compute_all(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, force_excluded=False, context=None):
        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        tax_compute_precision = precision
        rounding_method = self._get_tax_calculation_rounding_method(cr, uid, taxes, context)
        if taxes and rounding_method == 'round_globally':
            tax_compute_precision += 5
        totalin = totalex = round(price_unit * quantity, precision)
        tin = []
        tex = []
        for tax in taxes:
            if not tax.price_include or force_excluded:
                tex.append(tax)
            else:
                tin.append(tax)
        tin = self.compute_inv(cr, uid, tin, price_unit, quantity, product=product, partner=partner, precision=tax_compute_precision)
        for r in tin:
            totalex -= r.get('amount', 0.0)
        totlex_qty = 0.0
        try:
            totlex_qty = totalex/quantity
        except:
            pass
        tex = self._compute(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner, precision=tax_compute_precision)
        for r in tex:
            totalin += r.get('amount', 0.0)
        return {
            'total': totalex,
            'total_included': totalin,
            'taxes': tin + tex
        }

    # @api.v8
    # def compute_all(self, price_unit, quantity, product=None,
    #                 partner=None, force_excluded=False):
    #     return self._model.compute_all(
    #         self._cr, self._uid, self, price_unit, quantity,
    #         product=product, partner=partner, force_excluded=force_excluded,
    #         context=self._context)
