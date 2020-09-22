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
        apart_nos = vals.get('apart_no')

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

            crm_message = self.env['mail.message'].create({
                'model': 'crm.lead',
                'res_id': int(crm_obj.id),
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



        # return message
        # res = super(ContactsContacts, self).create(vals)
        return res


