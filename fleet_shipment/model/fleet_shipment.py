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
            [('draft','Draft'),
             ('awaiting','Waiting for Assignment'),
             ('exception','Exception'),
             ('confirm','Confirmed'),
             ('pending','Pending Dispatch'),
             ('overdue','Overdue'),
             ('in_transit','In Transit'),
             ('return','Return')],
            string='State',
            required=True,
            help=('Indicate Fleet Shipment Order State. The possible states'
                  ' are:\n'
                  '\t- Draft: A rough copy of the document, just a draft.\n'
                  '\t- Waiting for Assignment: A fleet shipment order proposal'
                  ' that need to be corroborated\n'
                  '\t- Exception: The fleet shipment order is totally set.\n'
                  '\t- Confirmed: The delivery have been cheked and assigned.\n'
                  '\t- Pending Dispatch: Waiting for be delivery.\n'
                  '\t- Overdue: The fleet shipment is late.\n'
                  '\t- In Transit: Is already send to delivery.\n'
                  '\t- Return: The vehicle is return to the parking.\n'
            )),
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

    def action_prepare(self, cr, uid, ids, context=None):
        """
        Change the state of a fleet shipment order from 'draft' to 'awaiting'
        state (assigned order).
        @return: True
        """
        context = context or {}
        self.write(cr, uid, ids, {'state': 'awaiting'}, context=context)
        return True

    def action_assign(self, cr, uid, ids, context=None):
        """
        Change the state of a fleet shipment order from 'awaiting' to
        'exception' (if there is a problem with the fleet shipment order) or
        'confirm' is all the values were successfully valuated. 

        In the process it verify some conditions:

          - that the current burden of the fleet shipment is less or equal to
            the fleet vehicle volumetric capacity.
          - that the pos order records included in the fleet shipment order
            belongs to the fleet shipment order urban zone.

        @return: True
        """
        context = context or {}
        error_msj = str()

        raise osv.except_osv(
            _('Warning'),
            _('This Functionality is still in development'))

        for fso_brw in self.browse(cr, uid, ids, context=context):
            if not self.check_volumetric_weight(
                cr, uid, fso_brw.transport_unit_id.id, fso_brw.current_burden,
                context=context)
                error_msj += _( 'The current burden volume you are entering is'
                    ' greater than the volumetric capacity of youre transport'
                    ' unit (%s > %s).\n' %
                    (fso_brw.current_burden,
                     fso_brw.transport_unit_id.volumetric_capacity))

            #~ self._check_urban_zone(
                #~ cr, uid, fso_brw.id, fso_brw.pos_order_ids, context=context)

        #~ self.write(cr, uid, ids, {'state': 'exception'}, context=context)
        #~ self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

        if error_msj:
            raise osv.except_osv(_('Error!!'), error_msj)
        return True


    def check_volumetric_weight(self, cr, uid, vehicle_id, current_burden,
                                context=None):
        """
        Check if the fleet shipment order current burden value is less than th
        vehicle volumetric capacity.
        @param vehicle_id: fleet vehicle id
        @param current_burden: fleet shipment order float value.
        @return: True if the current burdern is less than the vehicle
            volumetric weight. False if the current burdern is greater than the
            vehicle volumetric weight
        """
        context = context or {}
        fv_obj = self.pool.get('fleet.vehicle')
        fv_brw = fv_obj.browse(cr, uid, vehicle_id, context=context)
        return current_burden <= fv_brw.volumetric_capacity and True or False


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
