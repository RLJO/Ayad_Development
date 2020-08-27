from odoo import models, fields, api

class AccountInvoiceLineInherit(models.Model):

    _inherit = 'account.invoice.line'

    project_id = fields.Many2one('project.site', string='Project')
    apart_id = fields.Many2one('project.product', string='Apartments')
