import base64
import csv
from io import StringIO
from tempfile import TemporaryFile
import urllib.request as req
import base64
import shutil

import requests
from pathlib import Path

from odoo import api, fields, models
import codecs
import logging
_logger = logging.getLogger(__name__)

#
# class ImportCOA(models.Model):
#     _inherit = 'account.account'
#
#     imported = fields.Boolean('Imported')




class ImportPartners(models.TransientModel):
    _name = 'import.apartments.wizard'

    # pdf_binary = fields.Binary("Import PDF")
    upload_file = fields.Binary(string='File URL')
    upload_error = fields.Binary(string='Click To Download Error Log')
    upload_error_file_name = fields.Char("File name")


    def import_apartments(self):
        # filename = Path('/opt/metadata.pdf')
        # url = 'http://www.hrecos.org//images/Data/forweb/HRTVBSH.Metadata.pdf'
        # request = req.Request(url, headers={'User-Agent': "odoo"})
        # binary = req.urlopen(request)
        # pdf = base64.b64encode(binary.read())
        # project = self.env['project.product'].search([('id','=',522)])
        # project.write({'document' : pdf})
        csv_datas = self.upload_file
        fileobj = TemporaryFile('wb+')
        csv_datas = base64.decodebytes(csv_datas)
        fileobj.write(csv_datas)
        fileobj.seek(0)
        str_csv_data = fileobj.read().decode('utf-8')
        lis = csv.reader(StringIO(str_csv_data), delimiter=',')
        row_num = 0
        DATE_FORMAT = '%m/%d/%Y'
        error_list = []
        header_list = []
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header_list.append(value)
                else:
                    _logger.info('-----row number %s', key)
                    title = value[0].strip() or False
                    apartment_no = value[1].strip() or False
                    part = value[2].strip() or False
                    building = value[3].strip() or False
                    floor = value[4].strip() or False
                    type_no = value[5].strip() or False
                    status_apart = value[6].strip() or False
                    int_area = value[7].strip() or False
                    ext_area = value[8].strip() or False
                    base_price = value[9].strip() or False
                    project = value[10].strip() or False
                    pdf_url = value[11].strip() or False


                    project_obj = self.env['project.site'].search([('name', '=', project)])

                    apartment_obj = self.env['project.product'].search([('name', '=', apartment_no)])

                    if project_obj.id == apartment_obj.project_no.id:
                        print('Apartment already Exists with Project.')
                    elif not apartment_obj:
                        # url = 'http://www.hrecos.org//images/Data/forweb/HRTVBSH.Metadata.pdf'
                        if pdf_url:
                            request = req.Request(pdf_url, headers={'User-Agent': "odoo"})
                            binary = req.urlopen(request)
                            pdf = base64.b64encode(binary.read())
                        # project = self.env['project.product'].search([('id', '=', 522)])
                        # project.write({'document': pdf})
                            apartment_vals = {
                                'land_title': title,
                                'name': apartment_no,
                                'part': part,
                                'building_no' : building,
                                'floor_no' : floor,
                                'type_id' : type_no,
                                'status' : status_apart,
                                'carpet_area_no' : int_area,
                                'terrace_area_no' : ext_area,
                                'proj_price' : base_price,
                                'project_no' : project_obj.id,
                                'document' : pdf or False,
                                }
                        else:
                            apartment_vals = {
                                'land_title': title,
                                'name': apartment_no,
                                'part': part,
                                'building_no': building,
                                'floor_no': floor,
                                'type_id': type_no,
                                'status': status_apart,
                                'carpet_area_no': int_area,
                                'terrace_area_no': ext_area,
                                'proj_price': base_price,
                                'project_no': project_obj.id,
                            }
                    elif apartment_obj:
                        if pdf_url:
                            request = req.Request(pdf_url, headers={'User-Agent': "odoo"})
                            binary = req.urlopen(request)
                            pdf = base64.b64encode(binary.read())

                            apartment_vals = {
                                'land_title': title,
                                'name': apartment_no,
                                'part': part,
                                'building_no' : building,
                                'floor_no' : floor,
                                'type_id' : type_no,
                                'status' : status_apart,
                                'carpet_area_no' : int_area,
                                'terrace_area_no' : ext_area,
                                'proj_price' : base_price,
                                'project_no' : project_obj.id,
                                'document' : pdf or False,
                                }
                        else:
                            apartment_vals = {
                                'land_title': title,
                                'name': apartment_no,
                                'part': part,
                                'building_no': building,
                                'floor_no': floor,
                                'type_id': type_no,
                                'status': status_apart,
                                'carpet_area_no': int_area,
                                'terrace_area_no': ext_area,
                                'proj_price': base_price,
                                'project_no': project_obj.id,
                            }
                        # if account_type.id == 1 or account_type.id == 2:
                        #     acc_vals.update({'reconcile': True})
                    new_apartment_id = self.env['project.product'].sudo().create(apartment_vals)

                    _logger.info('-----row number %s already exists', key)

                    self._cr.commit()

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)
                error_list.append(value)

            csv.register_dialect('myDialect', quoting=csv.QUOTE_ALL, skipinitialspace=True)
            with open('/tmp/error_list_res_partner.csv', 'w') as csvFile:
                writer = csv.writer(csvFile, delimiter=',', dialect='myDialect')
                writer.writerows(header_list)
                writer.writerows(error_list)
            csvFile.close()
