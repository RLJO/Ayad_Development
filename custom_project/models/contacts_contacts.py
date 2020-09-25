from odoo import models, fields, api, _
from odoo.tools import formataddr
from datetime import datetime


class ContactsContacts(models.Model):

    _name = 'contacts.contacts'

    contact_details = fields.Many2one('res.partner', string='Customer',ondelete='cascade', required= True)
    project_no = fields.Many2one('project.site', string='Project',ondelete='cascade', required= True)
    apart_no = fields.Many2many('project.product', string='Apartment',ondelete='cascade')
    interest_client = fields.Text('Summary', required= True)
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

        apart_nos = vals.get('apart_no')

        # apart_nos = vals.get('apart_no')
        mail = self.env['mail.mail']


        res_partner_obj = self.env['res.partner'].search([('id', '=', contact_vals)])
        proj_site_obj = self.env['project.site'].search([('id', '=', proj_no)])


        if vals['interest_client'] and proj_site_obj:
            # body = 'Thank You for visiting.'
            log_msg = 'Visited Project: ' + str(proj_site_obj.name) + ' On  %s' % (datetime.now()) + ' Meeting Summary: ' + vals['interest_client']

            message = self.env['mail.message'].create({
                'model': 'res.partner',
                'res_id': int(res_partner_obj.id),
                'message_type': 'email',
                'body': log_msg,
                'author_id': res_partner_obj.id,
                'email_from': formataddr((res_partner_obj.name, res_partner_obj.email)),
                'subtype_id': self.env['mail.message.subtype'].search([('name', '=', 'note')]).id
            })
            
            crm_obj = self.env['crm.lead'].search([('partner_id', '=', res_partner_obj.id)])

            for crm in crm_obj:

                crm_message = self.env['mail.message'].create({
                    'model': 'crm.lead',
                    'res_id': int(crm.id),
                    'message_type': 'email',
                    'body': log_msg,

            # 'author_id': crm_obj.id,
            #  'email_from': formataddr((crm_obj.partner_id, crm_obj.email_from)),
            # 'subtype_id': self.env['mail.message.subtype'].search([('name', '=', 'note')]).id
            })


            apartment_many_lst= []
            for i in apart_nos[0][2]:
                apartment_many_lst.append(i)

            visitor_line_id = self.env['contact.visitor.line'].create({'project_id': proj_site_obj.id, 'apartment_id': [(6, 0, apartment_many_lst)], 'partner_id': res_partner_obj.id})

            res_partner_obj.write({'visited_ids': [(4, visitor_line_id.id)],})




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


        return res



    def next_meet(self):

        # active_id = self._context.get('active_id')
        # res_partner_obj = self.env['res.partner'].search([('')])

        res_partner_users_obj = self.env['res.partner'].search([('name', '=', self.responsible_person_id.name)])

        partner_lst= []

        partner_lst.append(self.contact_details.id)
        if res_partner_users_obj:
            partner_lst.append(res_partner_users_obj.id)

        ctx= {'default_partner_ids': [(6, 0, partner_lst)]}


        return {
            'name': _('Next Meeting'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'calendar.event',
            # 'res_id': return_wiz.id,
            'res_id': self._context.get('active_id'),
            'view_id': False,
            'target': 'new',
            'views': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }
