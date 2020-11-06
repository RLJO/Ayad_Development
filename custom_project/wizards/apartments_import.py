import base64
import csv
from io import StringIO
from tempfile import TemporaryFile
import urllib.request as req
import base64
import re
from odoo.exceptions import UserError
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

                    apartment_obj = self.env['project.product'].search([('name', '=', apartment_no),('project_no.id','=',project_obj.id)])
                    if not apartment_obj:
                        # url = 'http://www.hrecos.org//images/Data/forweb/HRTVBSH.Metadata.pdf'
                        # if pdf_url:
                        if pdf_url:
                            try:
                                if pdf_url.__contains__('drive.google.com'):
                                    pdf_url = re.sub("/file/d/", "/uc?export=download&id=", pdf_url)
                                    pdf_url = re.sub("/view\?usp=sharing", "", pdf_url)
                                # request = req.Request(pdf_url, headers={'User-Agent': "odoo"})
                                request = req.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11 odoo',
                               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                               'Accept-Encoding': 'none',
                               'Accept-Language': 'en-US,en;q=0.8',
                               'Connection': 'keep-alive'})
                                binary = req.urlopen(request)
                                pdf = base64.b64encode(binary.read())
                            except Exception as e:
                                raise UserError(e)
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
                            'document_name' : str(project_obj.name)+".pdf",
                            }
                        # else:
                        #     apartment_vals = {
                        #         'land_title': title,
                        #         'name': apartment_no,
                        #         'part': part,
                        #         'building_no': building,
                        #         'floor_no': floor,
                        #         'type_id': type_no,
                        #         'status': status_apart,
                        #         'carpet_area_no': int_area,
                        #         'terrace_area_no': ext_area,
                        #         'proj_price': base_price,
                        #         'project_no': project_obj.id,
                        #     }
                    if apartment_obj:
                        if pdf_url:
                            try:
                                if pdf_url.__contains__('drive.google.com'):
                                    pdf_url = re.sub("/file/d/", "/uc?export=download&id=", pdf_url)
                                    pdf_url = re.sub("/view\?usp=sharing", "", pdf_url)
                                request = req.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11 odoo',
                               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                               'Accept-Encoding': 'none',
                               'Accept-Language': 'en-US,en;q=0.8',
                               'Connection': 'keep-alive'})
                                binary = req.urlopen(request)
                                pdf = base64.b64encode(binary.read())
                            except Exception as e:
                                raise UserError(e)
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
                        # else:
                        #     apartment_vals = {
                        #         'land_title': title,
                        #         'name': apartment_no,
                        #         'part': part,
                        #         'building_no': building,
                        #         'floor_no': floor,
                        #         'type_id': type_no,
                        #         'status': status_apart,
                        #         'carpet_area_no': int_area,
                        #         'terrace_area_no': ext_area,
                        #         'proj_price': base_price,
                        #         'project_no': project_obj.id,
                        #     }
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
