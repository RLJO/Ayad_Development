from odoo import models, fields, api

class SalesOrderInherit(models.Model):

    _inherit = 'sale.order'

    second_partner_id = fields.Many2one('res.partner',string='Customer',ondelete='cascade')

    @api.multi
    def _prepare_invoice(self):
        res = super(SalesOrderInherit,self)._prepare_invoice()
        res.update({
            'second_partner_id':self.second_partner_id.id
        })

        return res

    # @api.multi
    # def _action_confirm(self):
    #     result = super(SalesOrderInherit, self)._action_confirm()
    #     for line in self.order_line:
    #         line.apart_id.status = 'sold'
    #         # proj_apart_obj = self.env['project.product'].search([('id', '=', self.id)])
    #
    #         # if line.apart_id == proj_apart_obj.name:
    #         #     proj_apart_obj.name.status = self.status
    #     return result



class SalesOrderLineInherit(models.Model):

    _inherit = 'sale.order.line'

    project_id = fields.Many2one('project.site', string='Project',ondelete='cascade')
    apart_id = fields.Many2one('project.product', string='Apartments',ondelete='cascade')
    # status = fields.Selection([('sold','Sold'),('unsold','Unsold')],string='Status')

    # @api.multi
    # def _prepare_invoice_line(self, qty):
    #     res = super(SalesOrderLineInherit, self)._prepare_invoice_line(qty)
    #     # default_account_invoice = self.env['account.invoice'].account_get(self.project_id.id,self.apart_id.id,)
    #     # if default_account_invoice:
    #     # if self.advance_payment_method == 'percentage':
    #     res.update({'project_id': self.project_id.id, 'apart_id': self.apart_id.id})
    #     return res

    # @api.multi
    # def create_invoices(self):
    #     res = super(SalesOrderLineInherit, self).create_invoices()
    #     # if self.advance_payment_method == 'percentage':
    #     res.update({'project_id': self.project_id.id, 'apart_id': self.apart_id.id})
    #     return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SalesOrderLineInherit, self)._prepare_invoice_line(qty)
        # if self.advance_payment_method == 'percentage':
        res.update({'project_id': self.project_id.id, 'apart_id': self.apart_id.id,'invoice_id.second_partner_id':self.order_id.second_partner_id.id})
        return res








    # @api.multi
    # def _prepare_status_values(self, group_id=False):
    #     res = super(SalesOrderLineInherit, self)._prepare_status_values(group_id)
    #     res.update({'status': self.status})
    #     return res

    # @api.onchange('project_id')
    # def status_project(self):
    #     for rec in self:
    #         return {'domain': {'apart_id': [('project_no', '=', 'sold')]}}




    @api.onchange('project_id')
    def status_apart(self):
        for rec in self:
            apart_ids = self.env['project.product'].search([('project_no', '=', self.project_id.id),('status', '=', 'unsold')])
            if rec.project_id.id:
                return {'domain': {'apart_id':  [('id', 'in', apart_ids.ids)]}}


    @api.onchange('apart_id')
    def status_change(self):
        for rec in self:
            if rec.apart_id:
                rec.price_unit = rec.apart_id.total_price



