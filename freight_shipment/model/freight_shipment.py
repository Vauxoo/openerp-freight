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

def get_delivery_states(self, cr, uid, context=None):
    """
    This method create the dictionary of tuples used to set the selection
    options in pos.order and stock.piking delivery_state selection field.
    """
    return [
        ('undelivered', 'Undelivered'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('expcetion', 'Unsuccefully Delivery'),
        ('returned', 'Returned')]


class stock_picking(osv.Model):

    _inherit = "stock.picking"
    _columns = {
        'freight_shipment_id': fields.many2one(
            'freight.shipment',
            string='Freight Shipment',
            help='Freight Shipment Order'
        ),
        'delivery_state': fields.selection(
            get_delivery_states,
            'Delivery State',
            help='Indicates the delivery state of the order'),
    }

    _defaults = {
        'delivery_state': 'undelivered',
    }


class freight_shipment(osv.Model):

    _name = 'freight.shipment'
    _description = _('Freight Shipment')
    _inherit = ['mail.thread']

    '''
    Freight Shipment
    '''

    def _get_sale_order_ids(self, cr, uid, ids, field_name, arg, context=None):
        """
        Returns a dictonary { freight shipment id : [ sale order ids ] } to
        reload the really shipped orders (that sale oders how pickings are
        really into the freight shipment).
        """
        context = context or {}
        res = {}.fromkeys(ids, [])
        for fs_brw in self.browse(cr, uid, ids, context=context):
            for picking_brw in fs_brw.picking_ids:
                res[fs_brw.id] += [picking_brw.sale_id.id]
            res[fs_brw.id] = list(set(res[fs_brw.id]))

        return res

    def _get_vehicle_weight(self, cr, uid, ids, field_name, arg, context=None):
        """
        Update automaticly the max weight for the freight shipment taking into
        account the max weight capacity of the vehicle associated.
        """
        context = context or {}
        res = {}.fromkeys(ids, 0.0)
        for fs_brw in self.browse(cr, uid, ids, context=context):
            if fs_brw.vehicle_id.id:
                res[fs_brw.id] = fs_brw.vehicle_id.physical_capacity
        return res

    def _get_vehicle_vol_weight(self, cr, uid, ids, field_name, arg,
                                context=None):
        """
        Update automaticly the max volumetric weight for the freight shipment
        taking into account the max volumetric weight capacity of the vehicle
        associated.
        """
        context = context or {}
        res = {}.fromkeys(ids, 0.0)
        for fs_brw in self.browse(cr, uid, ids, context=context):
            if fs_brw.vehicle_id.id:
                res[fs_brw.id] = fs_brw.vehicle_id.volumetric_capacity
        return res

    _columns = {
        'name': fields.char(
            string='Number Reference',
            size=256,
            required=True,
            help='Number Reference'),
        'vehicle_id': fields.many2one(
            'fleet.vehicle',
            string='Transport Unit',
            required=True,
            help='Transport Unit'),
        'pos_order_ids': fields.one2many(
            'pos.order', 'freight_shipment_id',
            string='POS Orders',
            help='POS Orders'),
        'state': fields.selection(
            [('draft','Draft'),
             ('awaiting','Waiting for Assignment'),
             ('exception','Exception'),
             ('confirm','Confirmed'),
             ('loaded','Loaded'),
             ('shipped','Shipped'),
             ('shipment_exception', 'Shipment Exception'),
             ('delivered', 'Delivered')],
            string='State',
            required=True,
            help=('Indicate Freight Shipment Order State. The possible states'
                  ' are:\n'
                  '\t- Draft: A rough copy of the document, just a draft.\n'
                  '\t- Waiting for Assignment: A freight.shipment order proposal'
                  ' that need to be corroborated\n'
                  '\t- Exception: The freight.shipment order is totally set.\n'
                  '\t- Confirmed: The delivery have been cheked and assigned.\n'
                  '\t- Loaded: The orders are already in the vehicle and is'
                  ' waiting for be delivery.\n'
                  '\t- Shipped: Is already send to destination. The shipment'
                  ' is in transit.\n'
                  '\t- Shipment Exception: there was a problem in the'
                  ' shipment.\n'
                  '\t- Delivered: The shipment arrived to the destination\n'
            )),
        'weight': fields.float(
            string='Weight',
            help='Weight'
        ),
        'volumetric_weight': fields.float(
            string='Volumetric Weight',
            help='Volumetric Weight'
        ),
        'max_weight': fields.function(
            _get_vehicle_weight,
            string='Max Weight',
            type='float',
            help=('The Weight Capacity of the vehicle associated to the freight'
                  ' Shipment')
        ),
        'max_volumetric_weight': fields.function(
            _get_vehicle_vol_weight,
            string='Max Volumetric Weight',
            type='float',
            help=('The Volumetric Weight Capacity of the vehicle associated to'
                  ' the freight Shipment')
        ),
        'date_shipped': fields.datetime(
            string='Shipped Date',
            help='The date and time where the freight was send'),
        'date_delivered': fields.datetime(
            string='Delivery Date',
            help='The date and time that the customer receives the freight'),
        'date_delivery': fields.datetime(
            string='Estimated Delivery Date',
            help='The date and time that the freight is supposed to be delivered'),
        'work_shift': fields.selection(
            [('morning', 'Morning'),
             ('afternoon', 'Afternoon'),
             ('night', 'Night')],
            string='Work Shift',
            required=True,
            help='Work Shift'),
        'zone_id': fields.many2one(
            'freight.zone',
            string='Zone',
            required=True,
            help='Zone'),
        'type': fields.selection(
            [('delivery', 'Delivery'),
             ('freight', 'Freight')],
            required=True,
            string='Type',
            help='Freight Type',
        ),
        'prefered_sale_order_ids': fields.one2many(
            'sale.order', 'prefered_freight_shipment_id',
            string='Prefered Sale Orders',
            help=('The Sale Orders who its prefered freight shipment was set'
                  ' with the current order.')
        ),
        'picking_ids': fields.one2many(
            'stock.picking', 'freight_shipment_id',
            string='Delivery Orders (Pickings)',
            help='Delivery Orders (Pickings)'
        ),
        'sale_order_ids': fields.function(
            fnct=_get_sale_order_ids,
            type='many2many',
            relation='sale.order',
            string='Processed Sale Orders',
            help=('Sale Orders real send')
        ),
        'message_exceptions': fields.text(
            'Exceptions history messages',
            help=('This field holds de the history of exceptions for the'
                  ' current freight.')
        ),
        'is_overdue': fields.boolean(
            'Overdue',
            help=('This field set if the freight shipment have any overdue')),

        # Note: This field is only a dummy, and it does not show in any place, 
        # Openerp _track attribute make some notifications (mail.messages)
        # when one of the models fields changes. But we are trying to create
        # notifications when a date is compared and no model field change only
        # this notification need to be raise. For that we craete this dummy
        # boolean field 'is_overdue' to let us make a brigde to create the
        # _track notifications. This 'is_overdue' field will be set when runing
        # a wizard that check the state of the freight shipments.
    }

    _defaults = {
        'state': 'draft',
        'work_shift': 'morning',
    }

    _track = {
        'state': {
            'freight_shipment.mt_fs_new':
                lambda self, cr, uid, obj, ctx=None: obj['state'] in ['draft'],
            'freight_shipment.mt_fs_waiting':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['awaiting'],
            'freight_shipment.mt_fs_exception':
                lambda self, cr, uid, obj, ctx=None: obj['state'] in ['exception'],
            'freight_shipment.mt_fs_vw_exception':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    not self.check_volumetric_weight(
                        cr, uid, obj['id'], context=ctx),
            'freight_shipment.mt_fs_w_exception':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    not self.check_weight(cr, uid, obj['id'], context=ctx),
            'freight_shipment.mt_fs_confirm':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['confirm'],
            'freight_shipment.mt_fs_to_load':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['confirm'],
            'freight_shipment.mt_fs_loaded':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['loaded'],
            'freight_shipment.mt_fs_shipped':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['shipped'],
        },
        'is_overdue': {
            'freight_shipment.mt_fs_shipment_overdue':
                lambda self, cr, uid, obj, ctx=None:
                    obj['is_overdue'] == True and self._check_shipment_overdue(
                        cr, uid, obj['id'], context=ctx),
            'freight_shipment.mt_fs_prepare_overdue':
                lambda self, cr, uid, obj, ctx=None:
                   obj['is_overdue'] == True and self._check_prepare_overdue(
                        cr, uid, obj['id'], context=ctx)
        },
    }

    def action_prepare(self, cr, uid, ids, context=None):
        """
        Change the state of a freight.shipment order from 'draft' to 'awaiting'
        state (assigned order).
        @return: True
        """
        context = context or {}
        self.write(cr, uid, ids, {'state': 'awaiting'}, context=context)
        return True

    def action_assign(self, cr, uid, ids, context=None):
        """
        Change the state of a freight.shipment order from 'awaiting' to
        'exception' (if there is a problem with the freight.shipment order) or
        'confirm' is all the values were successfully valuated. 

        In the process it verify some conditions:

          - that the accumulated volumetrict weight capacity of the freight is
            less or equal to max volumetrict weight capacity for this freight.
          - that the accumulated  weight capacity of the freight is less or
            equal to max weight capacity for this freight.

        @return: True
        """
        #~ Note: here there is manage the exception message that have not been
        #~ used or displayed anywhere
        context = context or {}
        exceptions = list()
        exception_msg = str()

        for fso_brw in self.browse(cr, uid, ids, context=context):

            exceptions.append(
                not self.check_volumetric_weight(
                    cr, uid, fso_brw.id, context=context))
            if exceptions[-1]:
                exception_msg += _('The volumetric weight of youre orders is'
                    ' greater than the volumetric capacity of youre transport'
                    ' unit (%s > %s).\n' % (fso_brw.volumetric_weight,
                        fso_brw.max_volumetric_weight))

            exceptions.append(
                not self.check_weight(cr, uid, fso_brw.id, context=context))
            if exceptions[-1]:
                exception_msg += _('The weight of youre orders is greater than'
                    ' the weight capacity of youre transport unit'
                    ' (%s > %s).\n' % (fso_brw.weight, fso_brw.max_weight))

        self.write(
            cr, uid, ids,
            {'state': any(exceptions) and 'exception' or 'confirm'},
            context=context)

        return True

    def action_force(self, cr, uid, ids, context=None):
        """
        This method force the freight.shipment to be confirm even if the
        valuation conditions of zone and burden are not fulfilled.
        """
        context = context or {}
        raise osv.except_osv(
            _('Warning'),
            _('This functionality is still in development'))
        return True


    def check_volumetric_weight(self, cr, uid, ids, context=None):
        """
        Check if the freight accumulated volumetric weight value is less or
        equal to the max volumetric weight capacity.
        @return: True if the condition is satisfied or False if is not.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = []
        for freight_brw in self.browse(cr, uid, ids, context=context):
            res.append(freight_brw.volumetric_weight
                <= freight_brw.max_volumetric_weight)
        if len(ids) == 1:
            return res[0]
        else:
            return res

    def check_weight(self, cr, uid, ids, context=None):
        """
        Check if the freight accumulated weight value is less or equal to the
        max weight capacity.
        @return: True if the condition is satisfied or False if is not.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = []
        for freight_brw in self.browse(cr, uid, ids, context=context):
            res.append(freight_brw.weight
                <= freight_brw.max_weight)
        if len(ids) == 1:
            return res[0]
        else:
            return res

    def action_back_to_awaiting(self, cr, uid, ids, context=None):
        """
        Return the freight shipment to the awaiting state to make the user the
        posibility of resolve the expcetions.
        """
        context = context or {}
        self.write(cr, uid, ids, {'state': 'awaiting'}, context=context)
        return True

    # Note: this method is only a dummy method for now.
    def action_loaded(self, cr, uid, ids, context=None):
        """
        This method is used by the xxx button to pass the freight shipment
        from Confirmed state to Loaded state.
        """
        context = context or {}
        self.write(cr, uid, ids, {'state': 'loaded'}, context=context)
        return True

    def action_shipped(self, cr, uid, ids, context=None):
        """
        This method will chage the freight shipment from Loaded estate to
        Shipped state. It represent the order to make the unit go out and do
        the shipment.
        """
        context = context or {}
        self.write(
            cr, uid, ids,
            {'state': 'shipped',
             'date_shipped': time.strftime('%Y-%m-%d %H:%M:%S')},
            context=context)
        return True

    def action_delivered(self, cr, uid, ids, context=None):
        """
        This method will change the freight shipment from Shipped state to
        Delivered state.
        """
        context = context or {}
        self.write(
            cr, uid, ids, {
                'state': 'delivered',
                'date_delivered': time.strftime('%Y-%m-%d %H:%M:%S')
            }, context=context)
        return True

    def _check_shipment_overdue(self, cr, uid, ids, context=None):
        """
        When an freight shipment have already been shipped but its late to be
        delivered. This method compare the Estimated Delivery Date
        (date_delivery) with the current date. If the current date and time is
        greater than the estimated delivery date then it means that there is a
        shipment overdue.
        @return: True if there is overdue, False if its not.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = {}.fromkeys(ids)
        for fs_brw in self.browse(cr, uid, ids, context=context):
            res[fs_brw.id] = \
                time.strftime('%Y-%m-%d %H:%M:%S') > fs_brw.date_delivery \
                and True or False
            #print 'FS(%s|%s) Shipped overdue is %s' % (
            #    fs_brw.id, fs_brw.name, res[fs_brw.id])
        if len(res.keys()) == 1:
            return res.values()[0]
        else:
            return res

    def _check_prepare_overdue(self, cr, uid, ids, context=None): 
        """
        When an freight shipment have been planned to be shipped in a specific
        day but the current day is is greater than that date is tell that is
        a prepare overdue because needs to be send and it have not yet.
        This method compare the current date and time with the Shipped Date
        (date_shipped). If the 'date_shipeed' is greater than the current date
        and timw then we have a prepare overdue.
        @return: True if there is overdue, False if its not.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = {}.fromkeys(ids)
        for fs_brw in self.browse(cr, uid, ids, context=context):
            res[fs_brw.id] = (fs_brw.date_shipped and 
                time.strftime('%Y-%m-%d %H:%M:%S') > fs_brw.date_shipped ) \
                and True or False
            #print 'FS(%s|%s) Prepare overdue is %s' % (
            #    fs_brw.id, fs_brw.name, res[fs_brw.id])
        if len(res.keys()) == 1:
            return res.values()[0]
        else:
            return res


class sale_order(osv.Model):

    _inherit = "sale.order"
    _columns = {
        'prefered_freight_shipment_id': fields.many2one(
            'freight.shipment',
            string='Prefered Freight Shipment',
            help=('Prefered Freight Shipment Order the users set when creating'
                  ' the Sale Order. This is the prefered Freight Shipment' 
                  ' where the sale order products will be send. Is not always'
                  'the real final destination')
        ),
        'freight_shipment_ids': fields.many2many(
            'freight.shipment',
            'sale_orders_freight_shipment_rel',
            'sale_order_id', 'fs_id',
            string='Final Freight Shipments',
            help=('It represent the real final destination Freight Shipment'
                  ' orders where this sale order was send.')
        ),
    }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """
        Overwrite the _prepare_order_picking method to add the prefered fregiht
        shipment order sete din the sale order to the pickings generating in
        the confirm sale order process.
        """
        context = context or {}
        res = super(sale_order, self)._prepare_order_picking(
            cr, uid, order, context=context)
        res.update(
            {'freight_shipment_id': order.prefered_freight_shipment_id.id})
        return res


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _prepare_chained_picking(self, cr, uid, picking_name, picking,
                                 picking_type, moves_todo, context=None):
        """
        Overwrithe method to add set the freight_shipment_id initial value
        when creating the dictionary to create the nre chained pickings.
        """
        context = context or {}
        res = super(stock_move, self)._prepare_chained_picking(
            cr, uid, picking_name, picking, picking_type, moves_todo,
            context=context)
        res.update({'freight_shipment_id': picking.freight_shipment_id.id})
        return res


class pos_order(osv.Model):

    _inherit = "pos.order"

    _columns = {
        'freight_shipment_id': fields.many2one(
            'freight.shipment',
            string='Freight Shipment',
            help='Freight Shipment'),
        'delivery': fields.boolean(
            string='Is Delivery?',
            help=('If this checkbox is checked then current order it or it'
                  ' will be delivery.')),
        'delivery_address': fields.many2one(
            'res.partner',
            'Delivery Address',
            help=('Delivery Address selected in the POS to make the delivery'
                  ' of the customer')),
        'delivery_state': fields.selection(
            get_delivery_states,
            'Delivery State',
            help='Indicates the delivery state of the order'),
    }

    _defaults = {
        'delivery_state': 'undelivered',
    }

    def action_pos_delivered(self, cr, uid, ids, context=None):
        """
        Button method. It set a pos order delivery state field to the
        'delivered' state.
        """
        context = context or {}
        self.write(cr, uid, ids, {'delivery_state': 'delivered'},
                   context=context)
        return True


class vehicle(osv.Model):

    _inherit = 'fleet.vehicle'

    _columns = {
        'is_freight': fields.boolean(
            'Freight',
            help=('If this checkbox is set then the vehicle can be use like a'
                  ' freight transport unit')
        ),
        'is_delivery': fields.boolean(
            'Delivery',
            help=('If this checkbox is set then the vehicle can be use like a'
                  ' delivery transport unit')
        ),
        'is_automobile': fields.boolean(
            'Automobile',
            help=('If this checkbox is set then the vehicle can be use like a'
                  ' automobile transport unit')
        ),
    }

