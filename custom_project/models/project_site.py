from odoo import models, fields, api

class ProjectSite(models.Model):

    _name = 'project.site'

    name = fields.Char('Name')
    project_type = fields.Selection([('under_const','Under Construction'),('developed','Developed')],string='Type:')
    status = fields.Selection([('partial', '10%'), ('half', '50%'),('full','100%')])
    payment_terms = fields.Selection([('partial', '10%'), ('half', '50%'),('full','100%')],string='Payment Terms')
    part = fields.Many2many('project.part', string='Part')

# A function to change the payment_terms by selecting status field.

    @api.onchange('status')
    def status_change(self):
        for rec in self:
            if rec.status:
                rec.payment_terms = rec.status


class SalesOrderInherit(models.Model):

    _inherit = 'sale.order'

    ref_no = fields.Many2one('res.partner',string='Reference No:')


class ProjectType(models.Model):
    _name = 'project.type'

    name = fields.Char('Name')
    project_status = fields.Char('Status')


class ProjectStatus(models.Model):
    _name = 'project.status'

    name = fields.Char('Name')


class ProjectPart(models.Model):
    _name = 'project.part'

    name = fields.Char('Name')