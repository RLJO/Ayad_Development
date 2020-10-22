from odoo import models, fields, api


class ResPartnerInherit(models.Model):

    _inherit = 'res.partner'

    passport_no = fields.Char('Id/ Passport No.')

    visited_ids = fields.One2many('contact.visitor.line', 'partner_id', string='Previous Visits')




class PartnerContactVisitorLine(models.Model):

    _name= 'contact.visitor.line'

    project_id = fields.Many2one('project.site', string='Visited Project')
    apartment_id = fields.Many2many('project.product', string='Visited Apartment')

    partner_id = fields.Many2one('res.partner')