#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Humberto Arocha<hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

{
    'name': 'Freight Weight',
    'version': '1.0',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'category': 'Freight',
    'description': '''
Freight Weight
==============

Main features
-------------
**Product**

Permission is needed to activate the "Allow to define several packaging method" to display
the fields of volume and volumetric weight in product.
Volumetric weight is calculated using the formula (volume / 5000)

**Vehicle**

Now you have two fields, volumetric weight capacity and physical weight capacity.

''',
    'depends': ['base', 'fleet', 'product'],
    'data': [
        "data/freight_data.xml",
        "view/freight_delivery_view.xml",
        ],
    'demo': [],
    'test': [],
    'active': False,
    'installable': True,
}
