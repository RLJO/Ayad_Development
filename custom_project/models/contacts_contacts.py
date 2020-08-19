from odoo import models, fields, api

class ContactsContacts(models.Model):

    _name = 'contacts.contacts'

    contact_details = fields.Many2one('res.partner', string='Customer:')
    project_no = fields.Many2one('project.site', string='Project:')
    apart_no = fields.Many2many('project.product', string='Apartment')
    interest_client = fields.Text('Interested:')