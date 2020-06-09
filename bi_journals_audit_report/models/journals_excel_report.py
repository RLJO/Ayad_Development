# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class JournalsExcelReport(models.TransientModel):
    _name = "journals.excel.report"

    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('Excel File', size=64)