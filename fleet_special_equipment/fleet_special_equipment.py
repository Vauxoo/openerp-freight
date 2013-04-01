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

class fleet_special_equipment(osv.osv):
    _name = 'fleet.special.equipment'
    _columns = {
        'name':fields.char('Name', size=64, required=False, readonly=False),
        'serial':fields.char('Serial No.', size=64, required=False, readonly=False),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle', required=False),
        'company_id':fields.many2one('res.company', 'Company', required=False),
    }
    _sql_constraints = [('serial_uniq','unique(serial)', 'This serial number vehicle must be unique!')]
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'fleet.special.equipment', context=c),
    }


class fleet_vehicle(osv.osv):
    _inherit = 'fleet.vehicle'
    _columns = {
        'equipment_ids':fields.one2many('fleet.special.equipment', 'vehicle_id', 'Equipment', required=False),
    }

