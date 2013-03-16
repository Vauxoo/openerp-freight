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

class fleet_vehicle_log_services(osv.osv):    
    _inherit = 'fleet.vehicle.log.services'

    def _get_services_created(self, cr, uid, ids, context=None):
        message_service = "<p><b>A Failure/Service has been reported : </b></p>"
        service = self.browse(cr, uid, ids)[0]
        message_service += "<li> <b>Vehicle</b> "+service.vehicle_id.name+" <b>Service:</b> "+service.cost_subtype_id.name+" <b>Description</b> "+service.notes+"</li> " 
                    
        return message_service

    def send_service_message(self, cr, uid,ids, context=None):
        (model, mail_group_id) = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_employee_driver_license', 'mail_group_1')
        msg = self._get_services_created(cr, uid, ids)
        self.pool.get('mail.group').message_post(cr, uid, [mail_group_id],body = msg, subtype='mail.mt_comment', context=context)
        return

    def create(self, cr, uid, vals, context={}):
        res_id = super(fleet_vehicle_log_services, self).create(cr, uid, vals, context)
        print res_id
        self.send_service_message(cr,uid,[res_id])
        return res_id

 

    
fleet_vehicle_log_services()
