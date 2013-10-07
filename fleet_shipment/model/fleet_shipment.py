#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Yanina Aular <yani@vauxoo.com>, Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import tools
import time

class fleet_shipment(osv.Model):

    _name = 'fleet.shipment'
    _description = _('Fleet Shipment')
    _inherit = ['mail.thread']

    '''
    Fleet Shipment
    '''

    _columns = {
        'name': fields.char(
            string='Number Reference',
            size=256,
            required=True,
            help='Number Reference'),
        'transport_unit_id': fields.many2one(
            'fleet.vehicle',
            string='Transport Unit',
            required=True,
            help='Transport Unit'),
        'pos_order_ids': fields.one2many(
            'pos.order', 'fleet_shipment_id',
            string='POS Orders',
            required=True,
            help='POS Orders'),
        'state': fields.selection(
            [('draft','Waiting for Assignment'),
             ('new','Assigned'),
             ('pending','Dispatch Pending'),
             ('overdue','Overdue'),
             ('in_transit','In Transit'),
             ('return','Return')],
            string='State',
            required=True,
            help='Fleet Shipment Order State'),
        'current_burden': fields.float(
            string='Current Burden',
            help='Current Burden'),
        'date': fields.datetime(
            string='Shipment Date',
            required=True,
            help='Date of the delivery was send'),
        'work_shift': fields.selection(
            [('morning', 'Morning'),
             ('afternoon', 'Afternoon'),
             ('night', 'Night')],
            string='Work Shift',
            required=True,
            help='Work Shift'),
        'zone': fields.text(
            string='Urban Zone',
            size=256,
            required=True,
            help='Urban Zone'),
    }

    _defaults = {
        'state': 'draft',
        'work_shift': 'morning',
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'zone': 'NO DEFINED',
    }

    def assign_fleet_shipment(self, cr, uid, ids, context=None):
        """
        Change the state of a fleet shipment order from draft to new (assigned
        order).
        @return: True
        """
        context = context or {}
        self.write(cr, uid, ids, {'state': 'new'}, context=context)
        return True

    def onchange_current_burden(self, cr, uid, ids, transport_unit_id,
                                current_burden, context=None):
        """
        this method verify that the current burden is equal or less to the
        volumetric capacity of the fleet vehicle.
        @param transport_unit_id: fleet vehicle id.
        @param current_burden: volumetric weight in float enter by the user in
                                the fleet shipment order.
        @return: the current burden value.
        """
        context = context or {}
        res = {'value': {}}
        fv_obj = self.pool.get('fleet.vehicle')
        fv_brw = fv_obj.browse(cr, uid, transport_unit_id, context=context)
        self._check_vehicle_volumentric_capacity(
            cr, uid, transport_unit_id, current_burden, context=context)
        return res

    def _check_vehicle_volumentric_capacity(self, cr, uid, vehicle_id,
                                            current_burden, context=None):
        """
        Raise an exception when trying to set the fleet shipment current
        burden with a value greater that the vehicle volumetric capacity.
        @param vehicle_id: fleet vehicle id
        @param current_burden: fleet shipment order float value.
        @return True
        """
        context = context or {}
        fv_obj = self.pool.get('fleet.vehicle')
        fv_brw = fv_obj.browse(cr, uid, vehicle_id, context=context)
        if current_burden > fv_brw.volumetric_capacity:
            raise osv.except_osv(
                _('Error!!'),
                _('The Burden volume you are entering is greater than youre'
                  ' transport volumetric capacity.'))
        return True

    def write(self, cr, uid, ids, values, context=None):
        """
        Overwrite the ORM write method to check that the current burden of the
        fleet shipment.
        """
        context = context or {}
        for fd_brw in self.browse(cr, uid, ids, context=context):
            vehicle_id = values.get('transport_unit_id', False) \
                or fd_brw.transport_unit_id.id
            if values.get('current_burden', False):
                self._check_vehicle_volumentric_capacity(
                    cr, uid, vehicle_id, values.get('current_burden'),
                    context=context)
        res = super(fleet_shipment, self).write(
            cr, uid, ids, values, context=context)
        return res

class pos_order(osv.Model):

    _inherit = "pos.order"

    _columns = {
        'fleet_shipment_id': fields.many2one(
            'fleet.shipment',
            string='Fleet Shipment',
            help='Fleet Shipment'),
        'delivery': fields.boolean(
            string='Is Delivery?',
            help=('If this checkbox is checked then current order it or it'
                  ' will be delivery.')),
        'delivery_address': fields.many2one(
            'res.partner',
            'Delivery Address',
            help=('Delivery Address selected in the POS to make the delivery'
                  ' of the customer')),
    }
