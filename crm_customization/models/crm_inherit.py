# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CrmInherit(models.Model):
    _inherit = 'crm.lead'

    visited = fields.Boolean('Visited')

    select_project = fields.Selection([('project1', 'Project 1'), ('project2', 'projectt 2')], string= 'Projects')

    select_site = fields.Selection([('apat', 'Apartment'), ('house', 'House'), ('parcel', 'Parcelling')], string= 'Site')

    interest = fields.Char('Interest')