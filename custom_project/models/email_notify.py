from odoo import api,fields,models,_
import datetime
import pytz


class EmailNotify(models.Model):
    _name = 'email.notify'

    today = fields.Datetime(default=lambda self: fields.datetime.now())

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
            activity_summary='''<p><b>Hello  '''+str(user.name)+''',</b></p></br>'''
            if next_hour <= 12:
                activity_summary = activity_summary +'''<p><b>TODAY\'S TASKS </b></p>'''
                activity_rec = self.env['mail.activity'].search([('user_id.id','=',user.id),('date_deadline','=',today)])
            else:
                activity_summary = activity_summary +'''<p><b>TOMORROW\'S TASKS  </b></p> </br>'''
                activity_rec = self.env['mail.activity'].search([('user_id.id','=',user.id),('date_deadline','=',tomorrow)])

            for activity in activity_rec:
                date_deadline = activity.date_deadline.strftime('%m/%d/%Y')
                activity_summary = activity_summary +  ''' <p><b>* '''+str(activity.activity_type_id.name)+ ''' </b>: ''' + str(activity.summary) +'''  On <b>'''+ date_deadline +'''</b></p></br>'''
            values = {
                'subject': "Tasks TO-DO",
                'body_html': activity_summary,
                'email_to': user.login,
            }
            mail.create(values).send()

