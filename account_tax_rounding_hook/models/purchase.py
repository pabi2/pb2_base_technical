# -*- coding: utf-8 -*-
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class purchase_order(models.Model):
    """
    OverWrite Tax Account
    """
    _inherit = 'purchase.order'

    amount_untaxed = fields.Float(
        string='Untaxed Amount',
        compute='_amount_all',
        digits_compute=dp.get_precision('Account'),
        help="The amount without tax",
        multi="sums",
        track_visibility='always',
        store=True,
    )
    amount_tax = fields.Float(
        string='Taxes',
        compute='_amount_all',
        digits_compute=dp.get_precision('Account'),
        help="The tax amount",
        multi="sums",
        store=True,
    )
    amount_total = fields.Float(
        string='Total',
        compute='_amount_all',
        digits_compute=dp.get_precision('Account'),
        help="The total amount",
        multi="sums",
        store=True,
    )

    @api.multi
    @api.depends('order_line', 'rounding_method')
    def _amount_all(self):
        Line = self.env["purchase.order.line"]
        for order in self:
            val = val1 = 0.0
            currency = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                line_price = Line._calc_line_base_price(line)
                line_qty = Line._calc_line_quantity(line)
                taxes = line.taxes_id.with_context(
                        method=order.rounding_method).compute_all(
                        line_price, line_qty, line.product_id,
                        order.partner_id)['taxes']
                for c in taxes:
                    val += c.get('amount', 0.0)
            order.amount_tax = currency.round(val)
            order.amount_untaxed = currency.round(val1)
            order.amount_total = order.amount_untaxed + order.amount_tax
