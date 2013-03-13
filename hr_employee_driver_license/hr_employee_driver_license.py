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

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'driver_license':fields.char('Driver License No', size=64, required=False, readonly=False),
        'date': fields.date('Expiration Date'),
    }

    def _get_expired_licenses(self, cr, uid, ids, context=None):
        message = ""
        now = datetime.datetime.now()
        employee_ids = self.search(cr, uid, [])
        for employee in self.browse(cr,uid, employee_ids):
            if employee.date:
                date_dt = datetime.datetime.strptime(employee.date, "%Y-%m-%d")
                if now > date_dt:
                    message += " <li> <b>No.</b> "+employee.driver_license+" <b>Employee:</b> "+employee.name+" <b>on</b> "+employee.date+"</li> " 
        return message

    def send_expiration_message(self, cr, uid,ids, context=None):
        (model, mail_group_id) = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_employee_driver_license', 'mail_group_1')
        exp_msg = self._get_expired_licenses(cr, uid, ids)
        self.pool.get('mail.group').message_post(cr, uid, [mail_group_id],body='Licenses expired this week : '+exp_msg, subtype='mail.mt_comment', context=context)
        print self._get_expired_licenses(cr, uid, ids)

        return 

hr_employee()


