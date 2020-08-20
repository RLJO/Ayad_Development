from odoo import models, fields, api

class ResPartnerInherit(models.Model):

    _name = 'res.partner.inherit'
    _inherit = 'res.partner'

    cin_no = fields.Char('CIN Number:')