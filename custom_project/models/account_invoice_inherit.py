from odoo import models, fields, api

class AccountInvoiceInherit(models.Model):

    _inherit = 'account.invoice'

    company = fields.Char('Company')
    notary_done = fields.Boolean("Notary Done")

    second_partner_id = fields.Many2one('res.partner', string='Customer', ondelete='cascade')


    # def action_invoice_sent(self):
    #     """ Overridden. Triggered by the 'send by mail' button.
    #     """
    #     rslt = super(AccountInvoiceInherit, self).action_invoice_sent()
    #     for line in self.invoice_line_ids:
    #         line.apart_id.status = 'sold'
    #     # if self.l10n_ch_isr_valid:
    #     #     rslt['context']['l10n_ch_mark_isr_as_sent'] = True
    #
    #     return rslt


    def action_invoice_open(self):

        res = super(AccountInvoiceInherit, self).action_invoice_open()
        for line in self.invoice_line_ids:
            line.apart_id.status = 'sold'
            # proj_apart_obj = self.env['project.product'].search([('id', '=', self.id)])

            # if line.apart_id == proj_apart_obj.name:
            #     proj_apart_obj.name.status = self.status
        return res


class AccountInvoiceLineInherit(models.Model):

    _inherit = 'account.invoice.line'

    project_id = fields.Many2one('project.site', string='Project')
    apart_id = fields.Many2one('project.product', string='Apartments')

    apart_status = fields.Selection([('sold', 'Sold'), ('unsold', 'Unsold'), ('reserved', 'Reserved'),('notary_done','Notary Done')], string='Status',
                                    compute='update_apartment_status')

    @api.depends('invoice_id.state')
    def update_apartment_status(self):
        # apartment = self.env['project.product'].search([('id','=',self.apart_id.id),('project_no.id', '=', self.project_id.id)])
        if (self.invoice_id.state == 'open' and self.invoice_id.residual < self.invoice_id.amount_total) \
                or (self.invoice_id.state == 'paid' and self.invoice_id.amount_total < self.apart_id.total_price):
            self.apart_status = 'reserved'
            self.apart_id.sudo().write({'status' : 'reserved'})
        if self.invoice_id.state == 'draft':
            self.apart_status = 'unsold'
            self.apart_id.sudo().write({'status' : 'unsold'})
        if self.invoice_id.state == 'paid':
            invoice_lines = self.env['account.invoice.line'].search([('apart_id.id','=',self.apart_id.id)])
            total_amount = 0.0
            for line in invoice_lines:
                if line.invoice_id.state =='paid':
                    total_amount += line.invoice_id.amount_total
            if total_amount == self.apart_id.total_price:
                self.apart_status = 'sold'
                self.apart_id.sudo().write({'status' : 'sold'})
            else:
                self.apart_status = 'reserved'
                self.apart_id.sudo().write({'status': 'reserved'})

        if self.invoice_id.notary_done == True:
            self.apart_status = 'notary_done'
            self.apart_id.sudo().write({'status': 'notary_done',
                                        'notary_done':'True'})


    @api.onchange('project_id')
    def status_apart(self):
        for rec in self:
            return {'domain': {'apart_id': [('project_no.id', '=', rec.project_id.id)]}}

    # @api.multi
    # def _prepare_invoice_line(self, qty):
    #     res = super(AccountInvoiceLineInherit, self)._prepare_invoice_line(qty)
    #     res.update({'project_id': self.project_id.id, 'apart_id': self.apart_id.id})
    #     return res

    @api.onchange('apart_id')
    def status_change(self):
        for rec in self:
            if rec.apart_id:
                rec.price_unit = rec.apart_id.total_price