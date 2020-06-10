# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CrmInherit(models.Model):
    _inherit = 'crm.lead'

    visited = fields.Boolean('Visited')

    select_project = fields.Selection([('site1', 'Site 1'), ('site2', 'Site 2')], string= 'Projects')