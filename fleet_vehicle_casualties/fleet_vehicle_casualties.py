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

class crm_claim(osv.osv):
    
    _inherit = 'crm.claim'
    _columns = {
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle', required=False),   
        'type':fields.selection([
            ('accident','Accident'),
            ('incident','Incident'),
            
        ],'Type', select=True, readonly=False),
    }
crm_claim()

class fleet_vehicle_casualties(osv.osv):
    _name = 'crm.clai'
    _columns = {
        'name':fields.char('Casualty', size=64, required=False, readonly=False),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle', required=False),   
        'date': fields.date('Date'),
        'state':fields.selection([
            ('closed','Closed'),    
            ('executed','Done'),
            ('inprogress','In Progress'),
            ('reprogrammed','Reprogrammed'),
            
        ],'State', select=True, readonly=False),
        'type':fields.selection([
            ('accident','Accident'),
            ('incident','Incident'),
            
        ],'Type', select=True, readonly=False),
    }
fleet_vehicle_casualties()

class fleet_vehicle(osv.osv):    
    _inherit = 'fleet.vehicle'
    _columns = {
        'casualties_ids':fields.one2many('fleet.vehicle.casualties', 'vehicle_id', 'Casualties', required=False),
    }
fleet_vehicle()
