from odoo import models, fields, api

class AccountInvoiceLineInherit(models.Model):

    _inherit = 'account.invoice.line'

    project_id = fields.Many2one('project.site', string='Project')
    apart_id = fields.Many2one('project.product', string='Apartments')

    @api.onchange('project_id')
    def status_apart(self):
        for rec in self:
            return {'domain': {'apart_id': [('project_no', '=', rec.project_id.id)]}}

    @api.onchange('apart_id')
    def status_change(self):
        for rec in self:
            if rec.apart_id:
                rec.price_unit = rec.apart_id.total_price