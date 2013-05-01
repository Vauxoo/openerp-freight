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
        'vehicle_expiring_id': fields.many2one('fleet.vehicle', 'Vehicle', required=False),
        'product_id': fields.many2one('product.product', 'Spare Part', required=False),
        'based': fields.selection([
            ('km', 'Kilometers'),
            ('date', 'Date'),
        ], 'Based on', select=True, readonly=False),
        'date': fields.date('Expiration Date'),
        'kilometers': fields.integer('Kilometers'),
        'last_odometer': fields.integer('Odometer on switch'),
        'state': fields.selection([
            ('using', 'Using'),
            ('dumped', 'Dumped'),

        ], 'State', select=True, readonly=False),
        'company_id':fields.many2one('res.company', 'Company', required=False),
    }
    _defaults = {
        'based': 'date',
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'fleet.service.expiring.line', context=c),
    }

    def _get_expired_parts(self, cr, uid, context=None):
        vehicle_obj = self.pool.get('fleet.vehicle')
        product_obj = self.pool.get('product.product')
        odo_obj = self.pool.get('fleet.vehicle.odometer')
        message_expired = "<p><b>Spare parts expired this week : </b></p>"
        now = datetime.datetime.now()
        spare_parts_ids = self.search(cr, uid, [])
        for spart in self.browse(cr, uid, spare_parts_ids):
            if spart.based == 'date' and spart.date and spart.state == 'using':
                date_dt = datetime.datetime.strptime(spart.date, "%Y-%m-%d")
                if now > date_dt:
                    message_expired += " <li><b>Part: </b> " + product_obj.browse(cr, uid, [spart.product_id.id])[
                        0].name + " <b>Vehicle:</b> <a href='#id="+str(spart.vehicle_expiring_id.id)+"&view_type=form&model=fleet.vehicle'>" + vehicle_obj.browse(cr, uid, [spart.vehicle_expiring_id.id])[0].name + " </a><b>on</b> " + spart.date + "</li> "
            if spart.based == 'km' and spart.kilometers and spart.state == 'using':
                max_id = odo_obj.search(cr, uid, [(
                    'vehicle_id', '=', spart.vehicle_expiring_id.id)], limit=1, order='value desc')
                actual_odo = odo_obj.browse(cr, uid, max_id)[0].value
                odo_diff = actual_odo - spart.last_odometer
                if odo_diff > spart.kilometers:
                    message_expired += " <li><b>Part: </b> " + product_obj.browse(cr, uid, [spart.product_id.id])[0].name + " <b>Vehicle:</b> <a href='#id="+str(spart.vehicle_expiring_id.id)+"&view_type=form&model=fleet.vehicle'>" + vehicle_obj.browse(
                        cr, uid, [spart.vehicle_expiring_id.id])[0].name + "</a> <b>over</b> " + str(odo_diff) + "<b> Kms after recommended</b></li> "
        return message_expired

    def send_expiration_message(self, cr, uid, context=None):
        (model, mail_group_id) = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'hr_employee_driver_license', 'mail_group_1')
        msg = self._get_expired_parts(cr, uid)
        self.pool.get('mail.group').message_post(cr, uid, [
                                                 mail_group_id], body=msg, subtype='mail.mt_comment', context=context)
        return

fleet_service_expiring_line()


class fleet_vehicle(osv.osv):

    _inherit = 'fleet.vehicle'
    _columns = {
        
        'service_expiring_ids': fields.one2many('fleet.service.expiring.line', 'vehicle_expiring_id', 'Expiring Spare Parts', required=False),
    }
fleet_vehicle()
