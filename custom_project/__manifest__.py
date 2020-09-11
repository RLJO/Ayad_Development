# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Site',
    'version': '1.1',
    'summary': 'Client Site',
    'sequence': 15,
    'description': """Client Site
    """,
    'category': 'Client',
    'website': 'https://www.odoo.com/page/billing',
    'images' : [],
    'depends' : ['base','stock','sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'wizards/product_price_wizards_view.xml',
        'views/apartments_import.xml',
        'views/project_product_view.xml',
        'views/project_site.xml',
        # 'views/project_part.xml',
        # 'views/project_status.xml',
        # 'views/project_type.xml',
        # 'views/inventory_inherit_view.xml',
        'views/account_invoice_inherit_view.xml',
        'views/email_notify.xml',
        'views/contacts_contacts_view.xml',
        # 'views/sales_order_view_inherit.xml',
        'views/res_users.xml',
        'views/sale_order_line_inherit.xml',
        # 'views/res_partner_view.xml',


    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
