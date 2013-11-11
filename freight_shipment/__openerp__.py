#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Yanina Aular <yani@vauxoo.com>, Humberto Arocha <hbto@vauxoo.com>
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
    'name': 'Freight Shipment',
    'version': '1.0',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'category': '',
    'description': '''
Freight Shipment
================

This module add a new model for shipment process that manage the shipment of
the orders of delivery generate for the POS and relate it to the transport
units.

Minimal Configurations
----------------------

To use this module you need to configure youre OpenERP instance by:

- Set True the ``Manage multiple locations and warehouses`` option at
  ``Settings Menu > Configuring Sidebar Section > Warehouse Menu > Logistic &
  Warehouse Section``.
- Set youre Output Location with ``Manual Operation`` type. Go to ``Warehouse
  Menu > Configuration Sidebar Section > Locations Menu > Select the Output
  Location > Chained Location Section > Chaining Type Field``.
- Be sure that you have available quantity of the product you are selling. For
  this make a purchase for that product and then receive the corresponding
  products.
- You need to set to True the
  `Allow a different address for delivery and invoicing` option in the
  `Settings Menu > Configuration SideBar Title > Sales Menu >
  Quotations and Sales Orders Section > Customer Features Section`. This way
  you will capable of see the delivery address of the partner in the sale
  order.

.. note:: You can found the dependecies:
   
   - ``freight_zone`` and ``freight_weight`` modules at ``lp:openerp-freight``.
   - ``incoterm_ext`` and ``incoterm_delivery_type`` module at
     ``lp:addons-vauxoo/7.0``.
''',
    'depends': ['base', 'mail', 'fleet', 'point_of_sale', 'stock',
                'freight_weight', 'freight_zone_mapsgoogle', 'incoterm_ext',
                'incoterm_delivery_type'],
    'data': [
        'security/freight_shipment_security.xml',
        'security/ir.model.access.csv',
        'view/freight_shipment_view.xml',
        'data/freight_shipment_data.xml',
        'wizard/freight_shipment_overdue_view.xml',
    ],
    'demo': [],
    'test': [],
    'active': False,
    'installable': True,
}
