from odoo import api,fields,models,tools, _
import datetime
import pytz

import smtplib
import threading

from odoo import api, fields, models, tools, _
from odoo.exceptions import except_orm, UserError
from odoo.tools import ustr, pycompat, formataddr

SMTP_TIMEOUT = 60

class EmailNotify(models.Model):
    _name = 'email.notify'

    today = fields.Datetime(default=lambda self: fields.datetime.now())
    has_activity = fields.Boolean()

    @api.multi
    def task_reminder_cron(self):
        mail = self.env['mail.mail']
        users = self.env['res.users'].search([])
        for user in users:
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
                    self.has_activity = True
                    activity_summary = activity_summary + ''' <p><b>* ''' + str(activity.activity_type_id.name) + ''' </b>: ''' + str(activity.summary) + '''  On <b>''' + activity.calendar_event_id.display_time + '''</b></p></br>'''

                elif activity.activity_category != 'meeting' and activity.user_id.id == user.id:
                    self.has_activity = True
                    activity_summary = activity_summary +  ''' <p><b>* '''+str(activity.activity_type_id.name)+ ''' </b>: ''' + str(activity.summary)+'''</p></br>'''


            if self.has_activity == True:
                values = {
                    'subject': "Activities TO-DO",
                    'body_html': activity_summary,
                    'email_to': user.login,
                }
                mail.create(values).send()

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
            smtp_user = user.email or mail_server.smtp_user
            # smtp_password = mail_server.smtp_pass
            smtp_password = str(user.email_pass) or mail_server.smtp_pass
            smtp_encryption = mail_server.smtp_encryption
            smtp_debug = smtp_debug or mail_server.smtp_debug
        else:
            # we were passed individual smtp parameters or nothing and there is no default server
            smtp_server = host or tools.config.get('smtp_server')
            smtp_port = tools.config.get('smtp_port', 25) if port is None else port
            smtp_user = user or tools.config.get('smtp_user')
            smtp_password = password or tools.config.get('smtp_password')
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
