from odoo import models, fields, api

class ProjectSite(models.Model):
    _name = 'project.site'

    name = fields.Char('Name')
    type = fields.Many2many('project.type', string = 'Type')
    status = fields.Many2one('project.status', string = 'Status')
    payment_terms = fields.Many2one('project.status', string = 'Payment Terms')
    part = fields.Many2many('project.part', string = 'Part')







class ProjectType(models.Model):
    _name = 'project.type'

    name = fields.Char('Name')


class ProjectStatus(models.Model):
    _name = 'project.status'

    name = fields.Char('Name')


class ProjectPart(models.Model):
    _name = 'project.part'

    name = fields.Char('Name')