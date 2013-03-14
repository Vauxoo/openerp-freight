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

class fleet_service_type(osv.osv):
    
    _inherit = 'fleet.service.type'
    _columns = {
        'category': fields.selection([('contract', 'Contract'), ('service', 'Service'), ('both', 'Both'),('paperwork','Paperwork')], 'Category', required=True, help='Choose wheter the service refer to contracts, vehicle services or both'),
    }
fleet_service_type()

class fleet_service_paperwork_line(osv.osv):  
    _name = 'fleet.service.paperwork.line'
    _columns = {
        'vehicle_paperwork_id':fields.many2one('fleet.vehicle', 'Vehicle', required=False),     
        'service_id':fields.many2one('fleet.service.type', 'Service', required=False),   
        'date': fields.date('Expiration Date'),
        'status': fields.selection([('pending', 'Pending'), ('valid', 'Valid'), ('expired', 'Expired')], 'Status', required=True, help='The state of the paperwork'),
    }

fleet_service_paperwork_line()

class fleet_vehicle(osv.osv):
    
    _inherit = 'fleet.vehicle'
    _columns = {
        'service_type_paperwork_ids':fields.one2many('fleet.service.paperwork.line', 'vehicle_paperwork_id', 'Paperworks', required=False),
    }
fleet_vehicle()
