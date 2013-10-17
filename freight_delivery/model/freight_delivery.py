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

from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _

class fleet_vehicle(osv.Model):
    _inherit = 'fleet.vehicle'
    _description = 'Information on a vehicle'

    _columns = {
            'physical_capacity' : fields.float('Physical Weight Capacity', help='Vehicle Physical Weight Capacity'), 
            'volumetric_capacity' : fields.float('Volumetric Weight Capacity', help='Vehicle Volumetric Weight Capacity'), 
            'type':fields.selection(
                [('automobile','Automobile'),('freight','Freight'),('delivery', 'Delivery')],string="Vehicle Type", 
                help='Vehicle Type'), 
     }

    _defaults = {
            'type': 'automobile',
            
            }

class product_product(osv.Model):
    _inherit = 'product.product'

    def _calculate_weight(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.volume / 5000
        return result
    def _set_volumetric_weight(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'volumetric_weight': value},
                context=context)

    _columns = {
            'volumetric_weight':fields.function(
            fnct=_calculate_weight,
            fnct_inv=_set_volumetric_weight,
            string='Volumetric Weight',
            type="float", 
            store={
                'product.product': (lambda self, cr, uid, ids, c={}: ids, ['volume'], 10),
            },
            help='Product Volumetric Weight',
            digits_compute=dp.get_precision('Volumetric Weight'),
            ), 

            #'divider' : fields.float('Divider', help='Product Volumetric Weight'), 
     }
