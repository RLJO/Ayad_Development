from odoo import models, fields, api
from datetime import datetime


class ContactsContacts(models.Model):

    _name = 'contacts.contacts'

    contact_details = fields.Many2one('res.partner', string='Customer:')
    project_no = fields.Many2one('project.site', string='Project:')
    apart_no = fields.Many2many('project.product', string='Apartment')
    interest_client = fields.Text('Interested:')
    date_time = fields.Datetime('Date & Time:', default=lambda self: fields.Datetime.now())

    @api.onchange('project_no')
    def status_project(self):
        for rec in self:
            return {'domain': {'apart_no': [('project_no', '=', rec.project_no.id)]}}