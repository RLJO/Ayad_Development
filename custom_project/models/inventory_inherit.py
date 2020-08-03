from odoo import models, fields, api

class InventoryFields(models.Model):

    _inherit = 'product.template'

    project_no = fields.Many2one('project.site',string='Project:')
    ref_no = fields.Char('Reference No:', compute='refer_no')
    part = fields.Selection([('o','Start'),('b','stop')],string='Part:')
    building_no = fields.Integer('Building No:')
    floor_no = fields.Integer('Floor No:')
    type_id = fields.Selection([('o','Under Construction'),('b','Developed')],string='Type:')
    price = fields.Float("Price:")
    status = fields.Selection([('s','Sold'),('u','Unsold')],string='Status:')
    surface = fields.Char('Surface:')

# A function to generate reference number based on project no. and product no.

    @api.multi
    @api.depends('project_no')
    def refer_no(self):
        ref = []
        numbers = []
        for rec in self:
            if rec.project_no:
                var = rec.project_no.name
                for word in var.split(' '):
                    if word.isdigit():
                        numbers.append(int(word))
                        break
                    ref.append(word[0:1])
                ref.append('_')
                ref.append(numbers)
        for rec in self:
            if rec.name:
                var1 = rec.name
                for word1 in var1.split(' '):
                    if word1.isdigit():
                        numbers.append('_')
                        numbers.append(int(word1))


# A function used to remove sublist within a list .

        output = []
        def removenestinglist(ref):
            for i in ref:
                if type(i) == list:
                    removenestinglist(i)
                else:
                    output.append(i)
                    print('The original list: ', ref)
        removenestinglist(ref)
        print('The list after removing nesting: ', output)

# Converting List into a string.

        listToStr = ' '.join([str(elem) for elem in output])
        print(listToStr)
        for rec in self:
            rec.ref_no = listToStr















