from odoo import models, fields, api

class ResPartnerInherit(models.Model):

    _name = 'res.partner.inherit'
    _inherit = 'res.partner'

    # cin_no = fields.Char('CIN Number:')
    visited = fields.Boolean('Visited')

    res_project = fields.Many2one('project.site', string='Projects', ondelete='cascade')

    res_site = fields.Many2one('project.product', string='Site', ondelete='cascade')