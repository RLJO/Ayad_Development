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
            # if rec1.order_line.product_id:
            if rec1.order_line:
                # product_obj = self.env['product.template'].search([('name','=', rec1.order_line.product_id.name)])
                for rec2 in rec1.order_line:
                    product_obj = self.env['product.template'].search([('name','=', rec2.product_id.name)])
                    if product_obj.project_no.project_type == 'under_const':
                        res['advance_payment_method'] = 'percentage'
        return res

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        sale_order_ids = self.env['sale.order'].browse(self._context.get('active_id'))
        if sale_order_ids:
            for order in sale_order_ids:
                if order.order_line:
                    for line in order.order_line:
                        product_obj = self.env['product.template'].search([('name', '=', line.product_id.name)])
                        if self.advance_payment_method == 'percentage' and product_obj.project_no.payment_terms == 'partial':
                            return {'value': {'amount': 10.00}}
                        if self.advance_payment_method == 'percentage' and product_obj.project_no.payment_terms == 'half':
                            return {'value': {'amount': 50.00}}
                        elif self.advance_payment_method == 'percentage':
                            return {'value': {'amount': 0}}
                        return {}
        else:
            if self.advance_payment_method == 'percentage':
                return {'value': {'amount': 0}}
            return {}