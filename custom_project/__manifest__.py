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
        'security/ir.model.access.csv',
        'views/project_site.xml',
        'views/project_part.xml',
        'views/project_status.xml',
        'views/project_type.xml',
        'views/inventory_inherit_view.xml',

        'views/email_notify.xml',

        'views/sales_order_view_inherit.xml',
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
