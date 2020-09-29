from odoo import api,fields,models,tools, _
import datetime
import pytz

import smtplib
import threading

from odoo import api, fields, models, tools, _
from odoo.exceptions import except_orm, UserError
from odoo.tools import ustr, pycompat, formataddr
from odoo import models, fields, api
import xlwt
import base64
import io

SMTP_TIMEOUT = 60

class EmailNotify(models.Model):
    _name = 'email.notify'


    @api.multi
    def task_reminder_cron(self):
        mail = self.env['mail.mail']
        users = self.env['res.users'].search([])
        for user in users:
            values={}
            has_activity = False
            tz = user.tz or pytz.utc
            timezone = pytz.timezone(tz)
            now = datetime.datetime.now(timezone)
            today = datetime.datetime.strftime(datetime.datetime.today(), "%m/%d/%Y")
            tomorrow = datetime.datetime.strftime(datetime.datetime.today() + datetime.timedelta(days=1), "%m/%d/%Y")
            next_hour = int(now.strftime("%H"))
            next_min = int(now.strftime("%M"))
            activity_summary='''<p><b>Hello  '''+str(user.name)+''',</b></p></br>'''
            if (next_hour == 12 and next_min==0) or (next_hour < 12):
                activity_summary = activity_summary +'''<p><b>TODAY\'S ACTIVITIES </b></p>'''
                activity_rec = self.env['mail.activity'].search([('date_deadline','=',today)])
            else:
                activity_summary = activity_summary +'''<p><b>TOMORROW\'S ACTIVITIES  </b></p> </br>'''
                activity_rec = self.env['mail.activity'].search([('date_deadline','=',tomorrow)])

            for activity in activity_rec:
                # date_deadline = activity.date_deadline.strftime('%m/%d/%Y')
                if activity.activity_category=='meeting' and user.partner_id.id in activity.calendar_event_id.partner_ids.ids:
                    has_activity = True
                    activity_summary = activity_summary + ''' <p><b>* ''' + str(activity.activity_type_id.name) + ''' </b>: ''' + str(activity.summary) + '''  On <b>''' + activity.calendar_event_id.display_time + '''</b></p></br>'''

                elif activity.activity_category != 'meeting' and activity.user_id.id == user.id:
                    has_activity = True
                    activity_summary = activity_summary +  ''' <p><b>* '''+str(activity.activity_type_id.name)+ ''' </b>: ''' + str(activity.summary)+'''</p></br>'''


            if has_activity == True:
                values = {
                    'subject': "Activities TO-DO",
                    'body_html': activity_summary,
                    'email_to': user.login,
                }
                mail.create(values).send()

    def print_apartment_sales_report(self):
        mail = self.env['mail.mail']
        projects = self.env['project.site'].search([])
        if projects:
            filename = "Project Sales Report"
            filename += '.xls'
            workbook = xlwt.Workbook()
        for project in projects:
            invoice_lines = self.env['account.invoice.line'].search([('project_id.id','=',project.id),('apart_id','!=',False),('invoice_id.type','=','out_invoice')])
            apartment_sales=[]
            apartment_ids=[]
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
                order = self.env['sale.order'].search([('name','=',line.invoice_id.origin)],limit=1)
                sales_person = order.user_id.name
                confirmation_date = datetime.datetime.strftime(order.confirmation_date, "%m/%d/%Y")
                if line.invoice_id.date_invoice:
                    invoice_date = datetime.datetime.strftime(line.invoice_id.date_invoice, "%m/%d/%Y")
                else:
                    invoice_date = '-'


                partners = line.invoice_id.partner_id.name
                if line.invoice_id.second_partner_id:
                    partners = partners+', '+line.invoice_id.second_partner_id.name
                invoice_dict={
                    'apartment':line.apart_id.name,
                    'customers':partners,
                    'responsible':sales_person,
                    'order_confirmation':confirmation_date,
                    'payment_date':invoice_date,
                    'status': str(line.apart_id.status).capitalize(),
                    'invoice': line.invoice_id.display_name,
                    'desc': line.name if 'Down payment' in str(line.name) else '-',
                    'amount_paid': 0.0 if line.invoice_id.state == 'draft' else line.invoice_id.amount_total - line.invoice_id.residual ,
                    'amount_unpaid': line.invoice_id.amount_total if line.invoice_id.state == 'draft' else line.invoice_id.residual,
                    'total': line.invoice_id.amount_total,
                }
                apartment_ids.append(line.apart_id.id)
                apartment_sales.append(invoice_dict)
            apartments = self.env['project.product'].search([('id','not in',apartment_ids),('project_no.id','=',project.id)])
            for apartment in apartments:
                invoice_dict = {
                    'apartment': apartment.name,
                    'customers': '-',
                    'responsible': '-',
                    'order_confirmation': '-',
                    'payment_date': '-',
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

                worksheet = workbook.add_sheet(project.name)
                style_header = xlwt.easyxf(
                    "font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center, vert center")
                style_subheader = xlwt.easyxf(
                    "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
                style_line = xlwt.easyxf("align: horiz center")

                worksheet.write_merge(0,1,0,10,project.name +' Sales Report',style=style_header)

                worksheet.write(2, 0, 'Apartment', style = style_subheader)
                worksheet.write(2, 1, 'Status', style = style_subheader)
                worksheet.write(2, 2, 'Customers', style = style_subheader)
                worksheet.write(2, 3, 'Responsible', style = style_subheader)
                worksheet.write(2, 4, 'Order Confirmation Date', style = style_subheader)
                worksheet.write(2, 5, 'Invoice',style = style_subheader)
                worksheet.write(2, 6, 'Description',style = style_subheader)
                worksheet.write(2, 7, 'Amount Paid', style = style_subheader)
                worksheet.write(2, 8, 'Amount Unpaid', style = style_subheader)
                worksheet.write(2, 9, 'Total', style = style_subheader)
                worksheet.write(2, 10, 'Payment Date', style = style_subheader)
                worksheet.col(2).width = 256*40
                worksheet.col(4).width = 256*23
                worksheet.col(5).width = 256*22
                worksheet.col(6).width = 256*23
                worksheet.col(7).width = 256*18
                worksheet.col(8).width = 256*18
                worksheet.col(3).width = 256*18
                worksheet.col(10).width = 256*18
                row = 3
                for apartment in apartment_sales:
                    worksheet.write(row,0, apartment['apartment'],style = style_line)
                    worksheet.write(row,1, apartment['status'],style = style_line)
                    worksheet.write(row,2, apartment['customers'],style = style_line)
                    worksheet.write(row,3, apartment['responsible'],style = style_line)
                    worksheet.write(row,4, apartment['order_confirmation'],style = style_line)
                    worksheet.write(row,5, apartment['invoice'],style = style_line)
                    worksheet.write(row,6, apartment['desc'],style = style_line)
                    worksheet.write(row,7, apartment['amount_paid'],style = style_line)
                    worksheet.write(row,8, apartment['amount_unpaid'],style = style_line)
                    worksheet.write(row,9, apartment['total'],style = style_line)
                    worksheet.write(row,10, apartment['payment_date'],style = style_line)
                    row+=1
        if apartment_sales:
            fp = io.BytesIO()
            workbook.save(fp)
            excel_file =base64.encodestring(fp.getvalue())
            attachment = self.env['ir.attachment'].create({
                'name': 'Project Sales',
                'datas': excel_file,
                'datas_fname': filename,
                'res_model': 'email.notify',
                'type': 'binary'
            })
            message = "Hello Mr. Othman,<br><p>  Project wise apartment sales report is attached to the mail</p>"
            values = {
                'subject': "Project Sales",
                'body_html': message,
                'email_to': 'nitin.planetodoo@gmail.com',
                'attachment_ids': [(6,0, [attachment.id])] or False,
            }
            mail.create(values).send()

        else:
            raise UserError('No sales found for the project')


class IrServer(models.Model):
    _inherit='ir.mail_server'

    def connect(self, host=None, port=None, user=None, password=None, encryption=None,
                smtp_debug=False, mail_server_id=None):

        """
        Override to send mail from logged users email instead of sending it from outgoing mail server configuration
        :param host: host or IP of SMTP server to connect to, if mail_server_id not passed
        :param port: SMTP port to connect to
        :param user: logged in user's username to authenticate with
        :param password: Password of logged in users mail id to authenticate with
        :param encryption: optional, ``'ssl'`` | ``'starttls'``
        :param smtp_debug: toggle debugging of SMTP sessions (all i/o
                              will be output in logs)
        :param mail_server_id: ID of specific mail server to use (overrides other parameters)
        :return:
        """
        """Returns a new SMTP connection to the given SMTP server.
           When running in test mode, this method does nothing and returns `None`.

           :param host: host or IP of SMTP server to connect to, if mail_server_id not passed
           :param int port: SMTP port to connect to
           :param user: optional username to authenticate with
           :param password: optional password to authenticate with
           :param string encryption: optional, ``'ssl'`` | ``'starttls'``
           :param bool smtp_debug: toggle debugging of SMTP sessions (all i/o
                              will be output in logs)
           :param mail_server_id: ID of specific mail server to use (overrides other parameters)
        """
        # Do not actually connect while running in test mode

        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)

        if getattr(threading.currentThread(), 'testing', False):
            return None

        mail_server = smtp_encryption = None
        if mail_server_id:
            mail_server = self.sudo().browse(mail_server_id)
        elif not host:
            mail_server = self.sudo().search([], order='sequence', limit=1)

        if mail_server:
            smtp_server = mail_server.smtp_host
            smtp_port = mail_server.smtp_port
            # smtp_user = mail_server.smtp_user
            smtp_user = user.email if user.email and user.email_pass else mail_server.smtp_user
            # smtp_password = mail_server.smtp_pass
            smtp_password = str(user.email_pass) if user.email and user.email_pass else mail_server.smtp_pass
            smtp_encryption = mail_server.smtp_encryption
            smtp_debug = smtp_debug or mail_server.smtp_debug
        else:
            # we were passed individual smtp parameters or nothing and there is no default server
            smtp_server = host or tools.config.get('smtp_server')
            smtp_port = tools.config.get('smtp_port', 25) if port is None else port
            smtp_user = user if user.email and user.email_pass else tools.config.get('smtp_user')
            smtp_password = password if user.email and user.email_pass else tools.config.get('smtp_password')
            smtp_encryption = encryption
            if smtp_encryption is None and tools.config.get('smtp_ssl'):
                smtp_encryption = 'starttls' # smtp_ssl => STARTTLS as of v7

        if not smtp_server:
            raise UserError(
                (_("Missing SMTP Server") + "\n" +
                 _("Please define at least one SMTP server, "
                   "or provide the SMTP parameters explicitly.")))

        if smtp_encryption == 'ssl':
            if 'SMTP_SSL' not in smtplib.__all__:
                raise UserError(
                    _("Your Odoo Server does not support SMTP-over-SSL. "
                      "You could use STARTTLS instead. "
                       "If SSL is needed, an upgrade to Python 2.6 on the server-side "
                       "should do the trick."))
            connection = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=SMTP_TIMEOUT)
        else:
            connection = smtplib.SMTP(smtp_server, smtp_port, timeout=SMTP_TIMEOUT)
        connection.set_debuglevel(smtp_debug)
        if smtp_encryption == 'starttls':
            # starttls() will perform ehlo() if needed first
            # and will discard the previous list of services
            # after successfully performing STARTTLS command,
            # (as per RFC 3207) so for example any AUTH
            # capability that appears only on encrypted channels
            # will be correctly detected for next step
            connection.starttls()

        if smtp_user:
            # Attempt authentication - will raise if AUTH service not supported
            # The user/password must be converted to bytestrings in order to be usable for
            # certain hashing schemes, like HMAC.
            # See also bug #597143 and python issue #5285
            smtp_user = pycompat.to_native(ustr(smtp_user))
            smtp_password = pycompat.to_native(ustr(smtp_password))
            connection.login(smtp_user, smtp_password)

        # Some methods of SMTP don't check whether EHLO/HELO was sent.
        # Anyway, as it may have been sent by login(), all subsequent usages should consider this command as sent.
        connection.ehlo_or_helo_if_needed()

        return connection


class ResUser(models.Model):
    _inherit='res.users'

    email_pass = fields.Char("Email Password",required=True)
