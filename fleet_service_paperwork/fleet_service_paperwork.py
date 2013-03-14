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
        'partner_id':fields.many2one('res.partner', 'Supplier', required=False),
        'date': fields.date('Expiration Date'),
        'status': fields.selection([('pending', 'Pending'), ('valid', 'Valid'), ('expired', 'Expired')], 'Status', required=True, help='The state of the paperwork'),
    }

    def _get_expired_paperworks(self, cr, uid, ids, context=None):
        vehicle_obj = self.pool.get('fleet.vehicle')
        service_obj = self.pool.get('fleet.service.type')
        message_expired = "<p><b>Paperworks expired this week : </b></p>"
        now = datetime.datetime.now()
        paperwork_ids = self.search(cr, uid, [])
        for paperwork in self.browse(cr,uid, paperwork_ids):
            
            if paperwork.date:
                date_dt = datetime.datetime.strptime(paperwork.date, "%Y-%m-%d")
                if now > date_dt and paperwork.status == 'valid':
                    message_expired += " <li><b>Document: </b> "+service_obj.browse(cr,uid,[paperwork.service_id.id])[0].name+" <b>Vehicle:</b> "+vehicle_obj.browse(cr, uid,[paperwork.vehicle_paperwork_id.id])[0].name+" <b>on</b> "+paperwork.date+"</li> " 
                    
        return message_expired

    def send_expiration_message(self, cr, uid,ids, context=None):
        (model, mail_group_id) = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_employee_driver_license', 'mail_group_1')
        msg = self._get_expired_paperworks(cr, uid, ids)
        self.pool.get('mail.group').message_post(cr, uid, [mail_group_id],body = msg, subtype='mail.mt_comment', context=context)
        return 

fleet_service_paperwork_line()

class fleet_vehicle(osv.osv):
    
    _inherit = 'fleet.vehicle'
    _columns = {
        'service_type_paperwork_ids':fields.one2many('fleet.service.paperwork.line', 'vehicle_paperwork_id', 'Paperworks', required=False),
    }
fleet_vehicle()
