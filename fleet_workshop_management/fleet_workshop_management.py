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

class fleet_service_stage(osv.osv):
    _name = 'fleet.service.stage'
    _columns = {
        'name':fields.char('Stage', size=64, required=False, readonly=False),
        'stage_default':fields.boolean('Default', required=False),
    }

fleet_service_stage()

class fleet_vehicle_log_services(osv.osv):
    _inherit = 'fleet.vehicle.log.services'

    def _get_default_stage_id(self, cr, uid, context=None):
        """ Gives default stage_id """
        stage_ids = self.pool.get('fleet.service.stage').search(cr,uid,[('name','=','New'),])
        return stage_ids[0]

    _columns = {
        'stage_id':fields.many2one('fleet.service.stage', 'Stage', track_visibility='onchange',required=False, domain="['|',('stage_default', '=', True),('stage_default', '=', False)]"),
    }
    _defaults = {
        'stage_id': _get_default_stage_id,
    }

fleet_vehicle_log_services()

