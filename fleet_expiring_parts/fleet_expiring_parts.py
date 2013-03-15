#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    oszckar@gmail.com
#
#    Developed by Oscar Alcala <oszckar@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import pooler, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import datetime

class fleet_service_expiring_line(osv.osv):  
    _name = 'fleet.service.expiring.line'
    _columns = {
        'vehicle_expiring_id':fields.many2one('fleet.vehicle', 'Vehicle', required=False),     
        'product_id':fields.many2one('product.product', 'Spare Part', required=False),   
        'based':fields.selection([
            ('km','Kilometers'),
            ('date','Date'),            
        ],'Based on', select=True, readonly=False), 
        'date': fields.date('Expiration Date'),
        'kilometers': fields.integer('Kilometers'),
    }
    _defaults = {
        'based':'date',
    }



fleet_service_expiring_line()

class fleet_vehicle(osv.osv):
    
    _inherit = 'fleet.vehicle'
    _columns = {
        'service_expiring_ids':fields.one2many('fleet.service.expiring.line', 'vehicle_expiring_id', 'Expiring Spare Parts', required=False),
    }
fleet_vehicle()
