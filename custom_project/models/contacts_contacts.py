from odoo import models, fields, api
from odoo.tools import formataddr
from datetime import datetime


class ContactsContacts(models.Model):

    _name = 'contacts.contacts'

    contact_details = fields.Many2one('res.partner', string='Customer',ondelete='cascade')
    project_no = fields.Many2one('project.site', string='Project',ondelete='cascade')
    apart_no = fields.Many2many('project.product', string='Apartment',ondelete='cascade')
    interest_client = fields.Text('Summary')
    date_time = fields.Datetime('Date & Time', default=lambda self: fields.Datetime.now())
    responsible_person_id = fields.Many2one('res.users',default=lambda self: self.env.user, string='Responsible Person')

    @api.onchange('project_no')
    def status_project(self):
        for rec in self:
            return {'domain': {'apart_no': [('project_no', '=', rec.project_no.id)]}}


    @api.model
    def create(self, vals):
        res = super(ContactsContacts, self).create(vals)
        contact_vals = vals.get('contact_details')
        proj_no = vals.get('project_no')
        # apart_nos = vals.get('apart_no')
        mail = self.env['mail.mail']

        res_part_obj = self.env['res.partner'].search([('id', '=', contact_vals)])
        proj_part_obj = self.env['project.site'].search([('id', '=', proj_no)])
        # apart_part_obj = self.env['project.product'].search([('id', '=', apart_nos)])

        if vals['interest_client'] and proj_part_obj:
            # body = 'Thank You for visiting.'
            body1 = 'Meeting Summary:' + ' ' + vals['interest_client']
            body2 = 'visited Project:' + ' ' + str(proj_part_obj.name)

            message = self.env['mail.message'].create({
                'model': 'res.partner',
                'res_id': int(res_part_obj.id),
                'message_type': 'email',
                'body': [body2 , body1,('Visitor Date & Time: %s') % (
                        datetime.now())],
                'author_id': res_part_obj.id,
                'email_from': formataddr((res_part_obj.name, res_part_obj.email)),
                'subtype_id': self.env['mail.message.subtype'].search([('name', '=', 'note')]).id
            })
            crm_obj = self.env['crm.lead'].search([('partner_id', '=', res_part_obj.id)])

            crm_message = self.env['mail.message'].create({
                'model': 'crm.lead',
                'res_id': int(crm_obj.id),
                'message_type': 'email',
                # 'body': body1,
                'body': [body2,body1,('Visitor Date & Time: %s') % (
                 datetime.now())],


            # 'author_id': crm_obj.id,
            #  'email_from': formataddr((crm_obj.partner_id, crm_obj.email_from)),
            # 'subtype_id': self.env['mail.message.subtype'].search([('name', '=', 'note')]).id
            })
        thank_you_message = """Hello """+res.contact_details.name+""",<br/><p>   Thank you for visiting and showing
         interest in """ +res.project_no.name+""" ,keep visiting."""
        attachment_ids =[]
        for apartment in res.apart_no:
            if apartment.document:
                attachment = self.env['ir.attachment'].create({
                    'name': str(apartment.name),
                    'datas': apartment.document,
                    'res_model': 'contacts.contacts',
                    'type':'binary'
                })
                attachment_ids.append(attachment.id)

        values = {
            'subject': "visit Again",
            'body_html': thank_you_message,
            'email_to': res.contact_details.email,
            'attachment_ids': [(6, 0, attachment_ids)] or False,
        }
        mail.create(values).send()
        # return message
        # res = super(ContactsContacts, self).create(vals)
        return res


