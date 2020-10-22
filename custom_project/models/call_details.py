from odoo import models, fields, api, _
from datetime import datetime


class CallDetails(models.Model):

    _name = 'call.details'

    contact_details = fields.Many2one('res.partner', string='Customer',ondelete='cascade', required= True)
    project_id = fields.Many2one('project.site', string='Project',ondelete='cascade')
    apart_id = fields.Many2many('project.product', string='Apartment',ondelete='cascade')
    interest_client = fields.Text('Summary')
    visit_date = fields.Datetime('Date & Time', default=lambda self: fields.Datetime.now())
    responsible_person_id = fields.Many2one('res.users',default=lambda self: self.env.user, string='Responsible Person')

    @api.onchange('project_no')
    def status_project(self):
        for rec in self:
            return {'domain': {'apart_id': [('project_id', '=', rec.project_id.id)]}}