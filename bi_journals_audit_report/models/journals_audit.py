# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


import base64
import io

import xlwt
from odoo import api, fields, models


class BiJournalsAudit(models.TransientModel):
    _name = "bi.journals.audit"

    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    sort_selection = fields.Selection([('date', 'Date'), ('move_name', 'Journal Entry Number'), ], 'Entries Sorted by',
                                      required=True, default='move_name')
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
                                   default=lambda self: self.env['account.journal'].search(
                                       [('type', 'in', ['sale', 'purchase'])]))
    amount_currency = fields.Boolean('With Currency',
                                     help="Print Report with the currency column if the currency differs from the company currency.")

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result

    @api.multi
    def print_journals_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(
            ['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id', 'sort_selection', 'amount_currency'])[
            0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        if self._context.get('report_type') != 'excel':
            return self.env.ref('bi_journals_audit_report.bi_journals_audit_action').with_context(
                landscape=True).report_action(self, data=data)
        else:
            move_lines = \
            self.env['report.bi_journals_audit_report.report_journals_audit']._get_report_values(self, data=data)[
                'lines']
            filename = 'Journals Audit.xls'
            workbook = xlwt.Workbook()
            for journal in self.env['account.journal'].browse(data['form']['journal_ids']):
                worksheet = workbook.add_sheet(journal.name)
                date_format = xlwt.XFStyle()
                date_format.num_format_str = 'dd/mm/yyyy'
                style_header = xlwt.easyxf(
                    "font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
                style_line = xlwt.easyxf(
                    "font:bold on;")
                worksheet.row(0).height_mismatch = True
                worksheet.row(0).height = 500
                worksheet.write_merge(0, 0, 0, 5, "Journals Audit Report", style=style_header)
                worksheet.write(2, 0, 'Company', style_line)
                worksheet.write(2, 1, 'journals', style_line)
                worksheet.write(2, 2, 'Entries Sorted By', style_line)
                worksheet.write(2, 3, 'Target Moves', style_line)
                if self.date_from:
                    worksheet.write(2, 4, 'Date From', style_line)
                if self.date_to:
                    worksheet.write(2, 5, 'Date To', style_line)

                worksheet.write(3, 0, self.company_id.name)
                worksheet.write(3, 1, journal.name)
                worksheet.write(3, 2, self.sort_selection)
                worksheet.write(3, 3, 'All Posted Entries' if self.target_move == 'posted' else 'All Entries')
                if self.date_from:
                    worksheet.write(3, 4, self.date_from,date_format)
                if self.date_to:
                    worksheet.write(3, 5, self.date_to,date_format)
                worksheet.write(5, 0, 'Move', style_line)
                worksheet.write(5, 1, 'Date', style_line)
                worksheet.write(5, 2, 'Account', style_line)
                worksheet.write(5, 3, 'Partner', style_line)
                worksheet.write(5, 4, 'Label', style_line)
                worksheet.write(5, 5, 'Debit', style_line)
                worksheet.write(5, 6, 'Credit', style_line)
                row = 6
                col = 0
                for aml in move_lines.get(journal.id):
                    worksheet.write(row, col,
                                    aml.move_id.name != '/' and aml.move_id.name or ('*' + str(aml.move_id.id)))
                    worksheet.write(row, col + 1, aml.date)
                    worksheet.write(row, col + 2, aml.account_id.code)
                    worksheet.write(row, col + 3,
                                    aml.sudo().partner_id and aml.sudo().partner_id.name and aml.sudo().partner_id.name[
                                                                                             :23] or '')
                    worksheet.write(row, col + 4, aml.name)
                    worksheet.write(row, col + 5, aml.debit)
                    worksheet.write(row, col + 6, aml.credit)
                    row += 1
                row += 1
                worksheet.write(row, col + 4, 'Total', style_line)
                worksheet.write(row, col + 5,
                                self.env['report.bi_journals_audit_report.report_journals_audit']._sum_debit(data,
                                                                                                             journal),
                                style_line)
                worksheet.write(row, col + 6,
                                self.env['report.bi_journals_audit_report.report_journals_audit']._sum_credit(data,
                                                                                                              journal),
                                style_line)

                row += 3
                worksheet.write(row, col, 'Name', style_line)
                worksheet.write(row, col + 1, 'Base Amount', style_line)
                worksheet.write(row, col + 2, 'Tax Amount', style_line)
                row += 1
                taxes = self.env['report.bi_journals_audit_report.report_journals_audit']._get_taxes(data, journal)
                for tax in taxes:
                    worksheet.write(row, col, tax.name)
                    worksheet.write(row, col + 1, taxes[tax]['base_amount'])
                    worksheet.write(row, col + 2, taxes[tax]['tax_amount'])
                    row += 1
            fp = io.BytesIO()
            workbook.save(fp)

            export_id = self.env['journals.excel.report'].create(
                {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
            res = {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'journals.excel.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
            return res
