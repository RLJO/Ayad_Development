from odoo import models, fields, api

class SalesInherit(models.TransientModel):

    _inherit = 'sale.advance.payment.inv'

# A function for selecting down payment(Percentage) if project selected is under Construction and also to set Amount.
    @api.model
    def default_get(self, vals):
        res = super(SalesInherit, self).default_get(vals)
        sale_order_ids = self.env['sale.order'].browse(self._context.get('active_id'))
        # sale_order_line = self.env['sale.order.line'].browse('product_id')
        for rec1 in sale_order_ids:
            if rec1.order_line.product_id:
                product_obj = self.env['product.template'].search([('name','=', rec1.order_line.product_id.name)])
                for rec2 in product_obj:
                    if rec2.project_no.project_type == 'under_const':
                        res['advance_payment_method'] = 'percentage'
                        print('Hello')
                    if rec2.project_no.payment_terms == 'partial':
                        res['amount'] = 10.00
                        print('Hello')
                        break
                    elif rec2.project_no.payment_terms == 'half':
                        res['amount'] = 50.00
                        print('Hello')
                        break
            break
        return res