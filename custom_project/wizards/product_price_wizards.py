from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductPrice(models.TransientModel):

    _name = 'product.price.wizards'

    def _default_prod(self):
        return self.env['project.product'].browse(self._context.get('active_ids'))

    building_no = fields.Text('Building No:')
    floor_no = fields.Text('Floor No:')
    type_id = fields.Char('Apartment Type:')
    prod_price = fields.Float("Unit Price:")
    proj_id = fields.Many2one('project.site',string='Project:')
    ext_unit_price = fields.Integer('Exterior Unit Price:')
    inter_unit_price = fields.Integer('Interior Unit Price:')
    unit_price = fields.Selection([('single','Unit Price'),('multiple','Multiple Unit Price')],string='Apartment Price:')


    def price_update(self):

        filter_list = []

        if self.proj_id:
            filter_list.append(('project_no', '=', self.proj_id.id))
        else:
            raise ValidationError(('Oops!!! Select the Project First!!'))
        if self.building_no:
            filter_list.append(('building_no', '=', self.building_no))
        if self.floor_no:
            filter_list.append(('floor_no', '=', self.floor_no))
        if self.type_id:
            filter_list.append(('type_id', '=', self.type_id))
        prod_obj = self.env['project.product'].search(filter_list)
        print('hello')
        for record in prod_obj:
            record.proj_price = self.prod_price
        for record in prod_obj:
            record.interior_price = self.inter_unit_price
            record.ext_price = self.ext_unit_price



    def cancel(self):
        """To close wizard"""
        return {'type': 'ir.actions.act_window_close'}