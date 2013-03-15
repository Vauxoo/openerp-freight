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

class fleet_vehicle_claim(osv.osv):
    _name = 'fleet.vehicle.claim'
    _description = 'Fleet Vehicle Claim'
    _inherits = {'crm.claim': "crm_claim_id",}
    _inherit = ['mail.thread']
    _columns = {
        'vehicle_claim_id':fields.many2one('fleet.vehicle', 'Vehicle', required=False),
        'is_vehicle':fields.boolean('Vehicle Claim', required=False, help="This field adds the capability to filter claims by type"),
        'driver_id':fields.many2one('hr.employee', 'Driver', required=True, help="Here goes the name of the person guilty/causant of the complain"),
    }

    def onchange_partner_id(self, cr, uid, ids, part, email=False):
        """This function returns value of partner address based on partner
           :param part: Partner's id
           :param email: ignored
        """
        if not part:
            return {'value': {'email_from': False,
                              'partner_phone': False
                            }
                   }
        address = self.pool.get('res.partner').browse(cr, uid, part)
        return {'value': {'email_from': address.email, 'partner_phone': address.phone}}

    def set_is_vehicle(self,cr,uid,ids,vehicle_id):
        v={}
        v['is_vehicle']= True if vehicle_id else False
        return {'value':v}
fleet_vehicle_claim()

class fleet_vehicle(osv.osv):
    """
    fleet_vehicle
    """
    
    _inherit = 'fleet.vehicle'
    _columns = {
        'claim_ids':fields.one2many('fleet.vehicle.claim', 'vehicle_claim_id', 'Vehicle Claims', required=False),
    }
fleet_vehicle()
