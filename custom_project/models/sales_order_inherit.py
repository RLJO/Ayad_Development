from odoo import models, fields, api

class SalesOrderInherit(models.Model):

    _inherit = 'sale.order'

    ref_no = fields.Many2one('res.partner',string='Reference No:')

class SalesOrderLineInherit(models.Model):

    _inherit = 'sale.order.line'

    project_id = fields.Many2one('project.site', string='Project')
    apart_id = fields.Many2one('project.product', string='Apartments')

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SalesOrderLineInherit, self)._prepare_invoice_line(qty)
        res.update({'project_id': self.project_id.id, 'apart_id': self.apart_id.id})
        return res



    @api.onchange('project_id')
    def status_apart(self):
        for rec in self:
            return {'domain': {'apart_id': [('project_no', '=', rec.project_id.id)]}}


    @api.onchange('apart_id')
    def status_change(self):
        for rec in self:
            if rec.apart_id:
                rec.price_unit = rec.apart_id.total_price



