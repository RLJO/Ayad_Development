# -*- coding: utf-8 -*-
{
    'name': "Ayad CRM Custom",

    'summary': """
        Odoo CRM customization for Ayad Development""",

    'description': """
    """,

    'author': "Planet Odoo",
    'website': "http://www.planet-odoo.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    # 'category': 'Lead Automation',
    'version': '12.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm'],
    'images': [],
    # 'license': 'AGPL-3',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/activity_line.xml',
        'views/crm_view_inherit.xml',
    ]
}
