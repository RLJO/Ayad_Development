from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import xlwt
import base64
import io

class ApartmentSales(models.TransientModel):

    _name = 'apartment.sales.wizard'

    project = fields.Many2one('project.site',string="Project",required=True)

    def print_apartment_sales_report(self):
        invoice_lines = self.env['account.invoice.line'].search([('project_id.id','=',self.project.id),('apart_id','!=',False),('invoice_id.type','=','out_invoice')])
        apartment_sales=[]
        for line in invoice_lines:
            # invoices_list = []
            # partners =''
            # if line.apart_id.status != 'unsold':
            #     apartment_invoices = self.env['account.invoice'].search([('origin','=',line.order_id.name)])
            #     for invoice in apartment_invoices:
            #         invoice_dict={
            #             'name':invoice.name,
            #             'amount_paid':invoice.amount_total - invoice.residual,
            #             'amount_unpaid':invoice.residual
            #         }
            #         invoices_list.append(invoice_dict)
            partners = line.invoice_id.partner_id.name
            if line.invoice_id.second_partner_id:
                partners = partners+', '+line.invoice_id.second_partner_id.name
            invoice_dict={
                'apartment':line.apart_id.name,
                'customers':partners,
                'status': str(line.apart_id.status).capitalize(),
                'invoice': line.invoice_id.display_name,
                'desc': line.name if 'Down payment' in str(line.name) else '-',
                'amount_paid': line.invoice_id.amount_total - line.invoice_id.residual ,
                'amount_unpaid': line.invoice_id.residual,
                'total': line.invoice_id.amount_total,
            }
            apartment_sales.append(invoice_dict)
        apartments = self.env['project.product'].search([('status','=','unsold'),('project_no.id','=',self.project.id)])
        for apartment in apartments:
            invoice_dict = {
                'apartment': apartment.name,
                'customers': '-',
                'status': str(apartment.status).capitalize(),
                'invoice': 'Not Invoiced',
                'desc': '-',
                'amount_paid': '-',
                'amount_unpaid': '-',
                'total': '-',
            }
            apartment_sales.append(invoice_dict)

        if apartment_sales:
            # data_dict = {
            #     'name'  : self.project.name,
            #     'orders': apartment_sales
            # }

            filename = self.project.name + "_report"
            filename += '.xls'
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Sheet 1')
            style_header = xlwt.easyxf(
                "font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center, vert center")
            style_subheader = xlwt.easyxf(
                "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
            style_line = xlwt.easyxf("align: horiz center")

            worksheet.write_merge(0,1,0,6,self.project.name +' Sales Report',style=style_header)

            worksheet.write(2, 0, 'Apartment', style = style_subheader)
            worksheet.write(2, 1, 'Status', style = style_subheader)
            worksheet.write(2, 2, 'Customers', style = style_subheader)
            worksheet.write(2,3, 'Invoice',style = style_subheader)
            worksheet.write(2,4, 'Description',style = style_subheader)
            worksheet.write(2, 5, 'Amount Paid', style = style_subheader)
            worksheet.write(2, 6, 'Amount Unpaid', style = style_subheader)
            worksheet.write(2, 7, 'Total', style = style_subheader)

            row = 3
            for apartment in apartment_sales:
                worksheet.write(row,0, apartment['apartment'],style = style_line)
                worksheet.write(row,1, apartment['status'],style = style_line)
                worksheet.write(row,2, apartment['customers'],style = style_line)
                worksheet.write(row,3, apartment['invoice'],style = style_line)
                worksheet.write(row,4, apartment['desc'],style = style_line)
                worksheet.write(row,5, apartment['amount_paid'],style = style_line)
                worksheet.write(row,6, apartment['amount_unpaid'],style = style_line)
                worksheet.write(row,7, apartment['total'],style = style_line)
                row+=1

            fp = io.BytesIO()
            workbook.save(fp)

            export_id = self.env['excel.report'].create(
                {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
            res = {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'excel.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
            return res

            # return self.env.ref('custom_project.apartment_sales_report').report_action(self, data=data_dict)
        else:
            raise UserError('No sales found for the project')






