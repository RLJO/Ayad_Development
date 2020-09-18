from odoo import models, fields, api

class ProjectProduct(models.Model):

    _name = 'project.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Apartment ID')
    project_no = fields.Many2one('project.site',string='Project:',ondelete='cascade')
    ref_no = fields.Char('Reference No', compute='refer_no',store=True)
    part = fields.Char('Part')
    building_no = fields.Char('Building No')
    floor_no = fields.Char('Floor No')
    type_id = fields.Char('Type')
    land_title = fields.Char('Land Title')
    proj_price = fields.Float("Unit Price")
    total_price = fields.Float('Total Price',compute='compute_price')
    status = fields.Selection([('sold','Sold'),('unsold','Unsold')],string='Status')
    carpet_area_no = fields.Integer('Interior Area')
    terrace_area_no = fields.Integer('Exterior Area')
    ext_price = fields.Integer('Exterior Unit Price')
    interior_price = fields.Integer('Interior Unit Price')
    surface_area = fields.Integer('Total Surface Area:',compute='compute_area')
    document = fields.Binary("Document")
    # no_of_rooms = fields.Integer('Total Rooms')

    # document_name = fields.Char(string="File Name")

    # _sql_constraints = [
    #     ('unique_import_id', 'unique (ref_no)', "Apartment already exists !"),
    # ]

    # def _get_status_move_values(self,values):
    #     res = super(ProjectProduct, self)._get_status_move_values(values)
    #     res['status'] = values.get('status', False)
    #     return res


    @api.model
    @api.depends('surface_area', 'carpet_area_no', 'terrace_area_no')
    def compute_area(self):
        for record in self:
            record['surface_area'] = record.carpet_area_no + record.terrace_area_no



    @api.model
    @api.depends('proj_price','carpet_area_no','terrace_area_no','ext_price','interior_price')
    def compute_price(self):
        for record in self:
            if record.proj_price:
                record['total_price'] = (record.carpet_area_no + record.terrace_area_no)*record.proj_price
            else:
                record['total_price'] = record.carpet_area_no*record.interior_price + record.terrace_area_no*record.ext_price




    @api.model
    @api.depends('ext_price', 'interior_price','carpet_area_no','terrace_area_no')
    def compute_total_price(self):
        for record in self:
            record['total_price'] = record.carpet_area_no*record.interior_price + record.terrace_area_no*record.ext_price





    # @api.multi
    # def unlink(self):
    #     proj_line_obj = self.env['project.details.line'].search([('product_id', '=', self.id)])
    #     proj_line_obj.unlink()
    #     return super(ProjectProduct, self).unlink()




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
                        numbers.append(str(int(word)).zfill(2))
                        break
                    ref.append(word[0:1])
                ref.append('_')
                ref.append(numbers)
        for rec in self:
            if rec.name:
                var1 = rec.name
                # for word1 in var1.split(' '):
                #     if word1.isdigit():
                numbers.append('_')
                numbers.append(str(int(var1)).zfill(2))

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