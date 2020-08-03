# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CrmInherit(models.Model):
    _inherit = 'crm.lead'

    visited = fields.Boolean('Visited')

    select_project = fields.Many2one('project.site', string='Projects')

    select_site = fields.Many2one('product.template', string= 'Site')

    interest = fields.Char('Interest')

    @api.onchange('select_project')
    def status_project(self):
        for rec in self:
            return {'domain': {'select_site': [('partner_id', '=', rec.select_project)]}}