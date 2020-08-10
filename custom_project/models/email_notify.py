from odoo import api,fields,models,_
import datetime
import pytz


class EmailNotify(models.Model):
    _name = 'email.notify'

    today = fields.Datetime(default=lambda self: fields.datetime.now())
    has_activity = fields.Boolean()

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