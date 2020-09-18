from odoo import models, fields, api


class ResPartnerInherit(models.Model):

    _inherit = 'res.partner'

    passport_no = fields.Char('Id/ Passport No.')