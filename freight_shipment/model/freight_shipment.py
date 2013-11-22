#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Yanina Aular <yani@vauxoo.com>,
#                  Katherine Zaoral <kathy@vauxoo.com>,
#                  Humberto Arocha <hbto@vauxoo.com>
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
        ('delivered', 'Delivered'),
        ('exception', 'Unsuccefully Delivery')]


class stock_picking(osv.Model):

    _inherit = "stock.picking"
    _columns = {
        'out_fs_id': fields.many2one(
            'freight.shipment',
            string='Outgoinh Freight Shipment',
            help='Outgoinh Freight Shipment Order'
        ),
        'in_fs_id': fields.many2one(
            'freight.shipment',
            string='Incoming Freight Shipment',
            help='Incoming Freigth Shipment Order'
        ),
        'delivery_state': fields.selection(
            get_delivery_states,
            'Delivery State',
            help='Indicates the delivery state of the order'),
        'pos_id': fields.many2one(
            'pos.order',
            string='POS Order',
            help='Point of Sale Order that generate this stock picking'),
    }

    _defaults = {
        'delivery_state': 'undelivered',
    }

    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
                context=None, count=False, access_rights_uid=None):
        """
        Overwrite the _search() method to filter the stock pikings items in
        the freight shipment form taking into account the shipment zone of the
        freight shipment with the shipment address zone
        (picking.sale_order.partnet_shipment_id) of the pickings.
        """
        context = context or {}
        partner_obj = self.pool.get('res.partner')
        picking_obj = self.pool.get('stock.picking')
        if context.has_key('filter_pickings_by_zone'):
            zone_id = context.get('filter_zone_id', False)
            if not zone_id:
                raise osv.except_osv(
                    _('Error!'),
                    _('Please you need to define the freight shipment zone'
                      ' first to filter the possible pickings to be add.'))
            else:
                context.pop('filter_pickings_by_zone')
                context.pop('filter_zone_id')
                picking_ids = picking_obj.search(
                    cr, uid, [], context=context)
                #print ' ---- picling_ids', picking_ids
                fs_zone_picking_ids = []
                for picking_brw in picking_obj.browse(
                        cr, uid, picking_ids, context=context):
                    # TODO: be carefull on how the pickings is search here,
                    # need to filter with a context the two pickings fields.
                    if (picking_brw.sale_id.partner_shipping_id and
                        zone_id in partner_obj.get_zone_ids(
                            cr, uid,
                            picking_brw.sale_id.partner_shipping_id.id,
                            context=context)):
                        fs_zone_picking_ids.append(picking_brw.id)
                fs_zone_picking_ids and args.append(
                    ('id', 'in', fs_zone_picking_ids))
                #print ' ---- fs_zone_picking_ids', fs_zone_picking_ids
        #print ' ---- args', args
        return super(stock_picking, self)._search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count, access_rights_uid=access_rights_uid)


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
            for picking_brw in fs_brw.out_picking_ids:
                res[fs_brw.id] += [picking_brw.sale_id.id]
            res[fs_brw.id] = list(set(res[fs_brw.id]))

        return res

    # TODO: this method could be merge with the above into one method.
    def _get_purchase_ids(self, cr, uid, ids, field_name, arg, context=None):
        """
        This a functional field method that verify the incoming pickings in the
        freigh shipment and return its associated purchase orders. This
        purchase orders are the one who really are into the shipment so there
        are linked to the freight shipment.
        @param field_name: 'purchase_order_ids'
        @return: a dictionary of the form
                 {freight shipment id: [purchase order ids]}
        """
        context = context or {}
        res = {}.fromkeys(ids, [])
        for fs_brw in self.browse(cr, uid, ids, context=context):
            for picking_brw in fs_brw.in_picking_ids:
                res[fs_brw.id] += [picking_brw.purchase_id.id]
            res[fs_brw.id] = list(set(res[fs_brw.id]))
        return res

    def _get_vehicle_weight_field(self, cr, uid, ids, field_name, arg,
                                  context=None):
        """
        This is a functional field method that extract from the vehicle of the
        freigh shipment the weight data. For this it use a dictonary of
        corresponding fields equals between freight shipment and fleet.vehicle.
        """
        context = context or {}
        res = {}.fromkeys(ids)
        vehicle_field = {
            'max_weight': 'physical_capacity',
            'max_volumetric_weight': 'volumetric_capacity',
            'recommended_weight': 'recommended_physical_capacity',
            'recommended_volumetric_weight': 'recommended_volumetric_capacity',
        }
        for fs_brw in self.browse(cr, uid, ids, context=context):
            res[fs_brw.id] = \
                getattr(fs_brw.vehicle_id, vehicle_field[field_name])
        return res

    # TODO: check this method behavior: is not taking into account the
    # product_uom in the stock.pickings and may needed
    def _get_freight_current_weight(self, cr, uid, ids, field_name, arg,
                                    context=None):
        """
        This a functional field method that returns the sumatory of all the
        pickings and pos order products weights to calculate the freight
        shipment weights by crossing the stock.move associated to this
        orders lines.
        @param field_name: ['out_weight', 'out_volumetric_weight'
                            'in_weight', 'in_volumetric_weight']
        @return: depending of what field_name is:
            - If is 'out_weight' returns the products gross weight sum of the
              outgoing orders.
            - If is 'out_volumetric_weight' returns the products volumetric
              weight sum of the outgoing orders.
            - If is 'in_weight' returns the products gross weight sum of the
              incoming orders.
            - If is 'in_volumetric_weight' returns the products volumetric
              weight sum of the incoming orders.

        Note: A Freight Shipment have two types of orders associated:
              Outgoing Order: the orders that need to be shipped by the
              freight shipment. If is a Freight type shipment then it refers
              to the sale orders. If is a Delivery type shipment then it
              refers to the pos orders.
              Incoming Order: the ordes that will be collected in the freight
              shipment when is in route. Are represented by the purchase
              orders and only applies when the shipment if of Freight type.
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids
        res = {}.fromkeys(ids, 0.0)

        out_weight_fields = ['out_weight', 'out_volumetric_weight']
        in_weight_fields = ['in_weight', 'in_volumetric_weight']
        weight_fields = ['out_weight','in_weight']
        volumetric_weight_fields = \
            ['out_volumetric_weight', 'in_volumetric_weight']

        match_product_field = \
            (field_name in weight_fields and 'product_tmpl_id.weight'
             or field_name in volumetric_weight_fields and 'volumetric_weight'
             or False)
        if not match_product_field:
            raise osv.except_osv(
                _('Programming Error'),
                _('The field name you are using in the'
                  ' _get_freight_current_weight method() is not valid.'
                  ' If you meant it then you need to over write this method.'))

        weight_field = 'move_brw.product_id.' + match_product_field
        for fs_brw in self.browse(cr, uid, ids, context=context):
            move_brws = []
            out_picking_move_brws = \
                [move_brw
                 for picking_brw in fs_brw.out_picking_ids
                 for move_brw in picking_brw.move_lines]
            pos_move_brws = \
                [move_brw
                 for pos_brw in fs_brw.pos_order_ids
                 for move_brw in pos_brw.picking_id.move_lines]
            in_picking_move_brws = \
                [move_brw
                 for picking_brw in fs_brw.in_picking_ids
                 for move_brw in picking_brw.move_lines]

            if field_name in out_weight_fields:
                move_brws = out_picking_move_brws + pos_move_brws
            elif field_name in in_weight_fields:
                move_brws = in_picking_move_brws

            for move_brw in move_brws:
                res[fs_brw.id] += (move_brw.product_qty * eval(weight_field))
        return res

    def _update_freight_shipment_name(self, cr, uid, ids, field_name, arg,
                                      context=None):
        """
        This is a functional field method that change the freight shipment name
        taking into account the shipped date, the zone and the vehicle name of
        the freight.
        @return: for avery given freight shipment id returns the new name of
                 the freight shipment baising on the last mentioned attributes.
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids
        res = {}.fromkeys(ids, '')
        for fs_brw in self.browse(cr, uid, ids, context=context):
            shipment_type = context.get('default_type', False) == 'freight' \
                and 'FREIGHT/' or \
                context.get('default_type', False) == 'delivery' \
                and 'DELIVERY/' or 'SHIPMENT/'
            res[fs_brw.id] = '%s -  %s - %s - %s' % (
                fs_brw.sequence == '/' and shipment_type or fs_brw.sequence,
                fs_brw.date_delivery or 'NO DELIVERY DATE',
                fs_brw.zone_id.name or 'NOT ZONE DEFINED',
                fs_brw.vehicle_id.name or 'NOT VEHICLE DEFINED')
        return res

    _columns = {
        'name': fields.function(
            _update_freight_shipment_name,
            string='Name',
            type='char',
            size=256,
            store={'freight.shipment': (lambda s, c, u, ids, cxt:
                ids, ['date_shipped', 'zone_id', 'vehicle_id', 'sequence'], 16)
            },
            help='Freight Shipment Reference Name'),
        'sequence': fields.char(
            string='Sequence',
            size=256),
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
                  '\t- Delivered: The shipment arrived to the destination\n')),
        'out_weight': fields.function(
            _get_freight_current_weight,
            type='float',
            string='Outgoing Weight',
            help=('The accumulated weight of the orders to be shipped. It'
                  ' is a calculated field that sums the gross weights of all'
                  ' products in the outgoing orders (sale and pos orders)'
                  ' belonging to this shipment. The user can not manually'
                  ' change this field is automatically calculated')),
        'in_weight': fields.function(
            _get_freight_current_weight,
            type='float',
            string='Incomming Weight',
            help=('The accumulated weight of the orders to be collected. It'
                  ' is a calculated field that sums the gross weights of all'
                  ' products in the incoming orders (purchase orders)'
                  ' belonging to this shipment. The user can not manually'
                  ' change this field is automatically calculated')),
        'initial_shipped_weight': fields.float(
            string='Shipped Weight',
            help=('This is the accumultad weight when the shipment is'
                  ' confirmed and therefore when is shipped. If the shipment'
                  ' is not complete delivered (Some shipment orders could not'
                  ' be delivered) then the value of this field will be'
                  ' different of the Weight field.')),
        'out_volumetric_weight': fields.function(
            _get_freight_current_weight,
            type='float',
            string='Outgoing Volumetric Weight',
            help=('The accumulated volumetric weight of the orders to be'
                  ' shipped. It is a calculated field that sums the volumetric'
                  ' weight of all the products in the outgoing orders (sale'
                  ' orders -freight- or pos orders -delivery-) belonging to'
                  ' this shipment. The user can not manually change this field'
                  ' is automatically calculated')),
        'in_volumetric_weight': fields.function(
            _get_freight_current_weight,
            type='float',
            string='Incoming Volumetric Weight',
            help=('The accumulated volumetric weight of the orders to be'
                  ' collected. It is a calculated field that sums the'
                  ' volumetric weight of all the products in the incoming'
                  ' orders (purchase orders -applies to freight-) belonging to'
                  ' this shipment. The user can not manually change this field'
                  ' is automatically calculated')),
        'initial_shipped_volumetric_weight': fields.float(
            string='Shipped Volumetric Weight',
            help=('This is the accumultad volumetric weight when the shipment'
                  ' is confirmed and therefore when is shipped. If the'
                  ' shipment is not complete delivered (Some shipment orders'
                  ' could not be delivered) then the value of this field will'
                  ' be different of the Volumetric Weight field.')),
        'max_weight': fields.function(
            _get_vehicle_weight_field,
            string='Maximum Weight Capacity',
            type='float',
            help=('The Maximum Weight Capacity of the transport unit'
                  ' associated to the current shipment. The user can not'
                  ' manually change this field its value is automatically'
                  ' import from the transport unit specs.')),
        'max_volumetric_weight': fields.function(
            _get_vehicle_weight_field,
            string='Maximum Volumetric Weight Capacity',
            type='float',
            help=('The Maximum Volumetric Weight Capacity of the transport'
                  ' unit associated to the current shipment. The user can not'
                  ' manually change this field its value is automatically'
                  ' import from the transport unit specs.')),
        'recommended_weight': fields.function(
            _get_vehicle_weight_field,
            string='Recommended Maximum Weight',
            type='float',
            help=('The recommended top weight for save use of the transport'
                  ' unit. The user can not manually change this field its'
                  ' value is automatically import from the transport unit'
                  ' specs.')),
        'recommended_volumetric_weight': fields.function(
            _get_vehicle_weight_field,
            string='Recommended Volumetric Weight',
            type='float',
            help=('The recommended top volumetric weight for save use of the'
                  ' transport unit. The user can not manually change this'
                  ' field its value is automatically import from the'
                  ' transport unit  specs.')),
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
            help='Freight Type'),
        'prefered_sale_order_ids': fields.one2many(
            'sale.order', 'prefered_freight_shipment_id',
            string='Prefered Sale Orders',
            help=('The Sale Orders who its prefered freight shipment was set'
                  ' with the current order.')),
        'out_picking_ids': fields.one2many(
            'stock.picking', 'out_fs_id',
            string='Outgoing Pickings',
            help='Outgoing Pickings'),
        'in_picking_ids': fields.one2many(
            'stock.picking', 'in_fs_id',
            string='Incoming Pickings',
            help='Incoming Pickings'),
        'sale_order_ids': fields.function(
            fnct=_get_sale_order_ids,
            type='many2many',
            relation='sale.order',
            string='Processed Sale Orders',
            help=('Sale Orders real send')),
        'prefered_purchase_ids': fields.one2many(
            'purchase.order', 'prefered_fs_id',
            string='Scheduled Purchase Orders',
            help=('The purchase orders that planned to be collected for this'
                  ' shipment (through the purchase order itself).'
                  ' However, these purchase orders are not necessarily those'
                  ' that were approved to be collected.')),
        'purchase_order_ids': fields.function(
            fnct=_get_purchase_ids,
            type='many2many',
            relation='purchase.order',
            string='Purchase Orders',
            help=('It represent the purchase orders added to this shipment.'
                  ' The orders are approved to be collected by this'
                  ' shipment.')),
        'message_exceptions': fields.text(
            'Exceptions history messages',
            help=('This field holds de the history of exceptions for the'
                  ' current freight.')),
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

        'is_complete_delivered': fields.boolean(
            'This Freight Shipment was Complete Delivered',
            help=('This field is a flag that permit to know if the shipment'
                  ' was complete delivered all its orders to be delivery. Is'
                  ' it set then all the planned orders were delivered, if it'
                  ' not, this field will be waiting to be')),
        # Note: This field is use like a flag that trigger the message log
        # notifications about the realase of undelivered pos orders and
        # pickings
        'company_id': fields.many2one(
            'res.company',
            string='Company',
            help=('This fields it only matters when there is a multi company'
                 ' enviroment')),
    }

    _defaults = {
        'state': 'draft',
        'work_shift': 'morning',
        'is_complete_delivered': True,
        'sequence': '/',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id 
    }

    def get_weight_exceptions(self, cr, uid, context=None):
        """
        Make and return the dictonary with all the weight capacity exceptions
        values corresponding values.
            (scope, weight_capacity_field)
        """
        context = context or {}
        res = {
            'ow': [('out', 'recommended_weight')],
            'ovw': [('out', 'recommended_volumetric_weight')],
            'iw': [('in', 'recommended_weight')],
            'ivw': [('in', 'recommended_volumetric_weight')],
        }
        res.update({
            'ow_ovw': res['ow'] + res['ovw'],
            'iw_ivw': res['iw'] + res['ivw'],
            'ovw_ivw': res['ovw'] + res['ivw'],
            'ovw_iw': res['ovw'] + res['iw'],
            'ovw_iw_ivw': res['ovw'] + res['iw'] + res['ivw'],
            'ow_ivw': res['ow'] + res['ivw'],
            'ow_iw': res['ow'] + res['iw'],
            'ow_iw_ivw': res['ow'] + res['iw'] + res['ivw'],
            'ow_ovw_ivw': res['ow'] + res['ovw'] + res['ivw'],
            'ow_ovw_iw': res['ow'] + res['ovw'] + res['iw'],
            'ow_ovw_iw_ivw': res['ow'] + res['ovw'] + res['iw'] + res['ivw'],
        })
        return res

    def get_except_condition_list(self, cr, uid, except_key, context=None):
        """
        Search a key in the in the exception key dictionary.
        @param except_key: the key of the exception. 
        @return: the list of (scope, weight_capacity_fields) that represent
                 the exception.
        """
        context = context or {}
        res = self.get_weight_exceptions(cr, uid, context=context) 
        return res[except_key]

    def get_weight_exception(self, cr, uid, context=None):
        """
        @return: the list of the valid weight exceptions in the freight
        shipment. This method is used at the _check_weight_conditions to
        extract the list of all valid conditions when the fulfill paramter
        is not given. and weight capacity exception is given like a tuple of
        the form
            (scope, weight capacity field)
        """
        context = context or {}
        except_list = ['ow', 'ovw', 'iw', 'ivw']
        except_dict = self.get_weight_exceptions(cr, uid, context=context)
        res = []
        for except_key in except_list:
            res.extend(except_dict.pop(except_key))
        return res

    def _check_weight_conditions(self, cr, uid, ids, except_key, context=None):
        """
        This method is used in the _track() property of the freigh shipment
        class. It used to check when some list of weight capacities are
        are not fulfill. This method was implemeted in order to verficate the
        weight capacities and facilitate the check of various weight capacities
        with different values.

        First verificate that the no fulfill weight capacites given are not
        fulfill, if satisfied then verificate the fulfill weight capacities.

        @param except_key: string with the key of the exception.

        Note: 'weight capacities' are tuples of the form
              ('scope', 'weight_capacity_field')

        @retun: True or False
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids
        res = {}.fromkeys(ids, True)
        no_fulfill = self.get_except_condition_list(
            cr, uid, except_key, context=context)
        fulfill = list(
            set(self.get_weight_exception(cr, uid, context=context)) -
            set(no_fulfill))

        print ' ---- comprobando condiciones'
        for fs_brw in self.browse(cr, uid, ids, context=context):
            for capacity in no_fulfill:
                if self.is_weight_fulfill(
                    cr, uid, fs_brw.id, capacity[0], capacity[1], 
                    context=context):
                    res[fs_brw.id] = False
                    break
            print ' ---- ', (res[fs_brw.id], 'ACC MAYOR QUE', no_fulfill)
            if res[fs_brw.id]:
                for capacity in fulfill:
                    if not self.is_weight_fulfill(
                        cr, uid, fs_brw.id, capacity[0], capacity[1], 
                        context=context):
                        res[fs_brw.id] = False
                        break

        print ' ---- res', res

        if len(ids) == 1:
            return res.values()[0]
        else:
            return res

    _track = {
        'state': {
            'freight_shipment.mt_fs_new':
                lambda self, cr, uid, obj, ctx=None: obj['state'] in ['draft'],
            'freight_shipment.mt_fs_waiting':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['awaiting'],
            'freight_shipment.mt_fs_exception_ovw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ovw', context=ctx),
            'freight_shipment.mt_fs_exception_ow':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ow', context=ctx),
            'freight_shipment.mt_fs_exception_ow_ovw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ow_ovw', context=ctx),
            'freight_shipment.mt_fs_exception_iw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'iw', context=ctx),
            'freight_shipment.mt_fs_exception_ivw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ivw', context=ctx),
            'freight_shipment.mt_fs_exception_iw_ivw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'iw_ivw', context=ctx),
            'freight_shipment.mt_fs_exception_ovw_ivw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ovw_ivw', context=ctx),
            'freight_shipment.mt_fs_exception_ovw_iw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ovw_iw', context=ctx),
            'freight_shipment.mt_fs_exception_ovw_iw_ivw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ovw_iw_ivw', context=ctx),
            'freight_shipment.mt_fs_exception_ow_ivw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ow_ivw', context=ctx),
            'freight_shipment.mt_fs_exception_ow_iw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ow_iw', context=ctx),
            'freight_shipment.mt_fs_exception_ow_iw_ivw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ow_iw_ivw', context=ctx),
            'freight_shipment.mt_fs_exception_ow_ovw_ivw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ow_ovw_ivw', context=ctx),
            'freight_shipment.mt_fs_exception_ow_ovw_iw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ow_ovw_iw', context=ctx),
            'freight_shipment.mt_fs_exception_ow_ovw_iw_ivw':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['exception'] and 
                    self._check_weight_conditions(
                        cr, uid, obj['id'], 'ow_ovw_iw_ivw', context=ctx),
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
            'freight_shipment.mt_fs_shipment_exception':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['shipment_exception'],
            'freight_shipment.mt_fs_delivered':
                lambda self, cr, uid, obj, ctx=None:
                    obj['state'] in ['delivered'],
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
        'is_complete_delivered': {
            'freight_shipment.mt_fs_complete_delivered':
                lambda self, cr, uid, obj, ctx=None:
                    obj['is_complete_delivered'] == False,
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

    def _get_seq_type(self, cr, uid, context=None):
        """
        Search in the sequence codes (sequence.type model) for those sequences
        correspoding to the freight shipment object.
        @return: the id of the sequence type (sequence code)
        """
        context = context or {}
        seq_type_obj = self.pool.get('ir.sequence.type')
        seq_type_ids = seq_type_obj.search(
            cr, uid, [
                ('code', 'like', '%freight.shipment%'),
                ('name', 'like', '%Freight%')],
            context=context)
        #print ' ---- sequence code existentes', seq_type_ids
        return seq_type_ids and len(seq_type_ids) == 1 and seq_type_ids[0] \
               or seq_type_ids

    def _create_seq_type(self, cr, uid, context=None):
        """
        Create a new sequence type for freight shipment model 
        @return the id of the new sequence type
        """
        context = context or {}
        seq_type_obj = self.pool.get('ir.sequence.type')
        seq_type_id = seq_type_obj.create(
            cr, uid, {
                'name': 'Freight Shipment',
                'code': 'freight.shipment'},
            context=context)
        #print ' ---- creado nuevo sequence code', seq_type_id
        return seq_type_id

    def assign_sequence(self, cr, uid, ids, context=None):
        """
        This method calculate the sequence for a freight shipment and write
        the corresponding value over the sequence field.
        @return True
        """
        context = context or {}
        seq_obj = self.pool.get('ir.sequence')
        seq_type_obj = self.pool.get('ir.sequence.type')
        ids = isinstance(ids, (long, int)) and [ids] or ids
        error_msg_for_multi_seq_type = \
            _('This procedure can not continue because there is more than one'
              ' Sequence Code for the model freight shipment. Please select'
              ' one Sequence Code and delete the rest.\n\n Go to Settings >'
              ' Technical > Sequence & Identifiers > Sequence Codes.')
        seq_type_id = \
            self._get_seq_type(cr, uid, context=context) or \
            self._create_seq_type(cr, uid, context=context)
        # TODO: what really do when there is more than one seq code? 
        if isinstance(seq_type_id, (list)):
            raise osv.except_osv(_('Warning!!'), error_msg_for_multi_seq_type)
        seq_type_code = seq_type_obj.browse(
            cr, uid, seq_type_id, context=context).code
        #print ' ---- sequence code', (seq_type_id, seq_type_code)
        for fs_brw in self.browse(cr, uid, ids, context=context):
            if fs_brw.sequence != '/':
                continue
            freight_type = fs_brw.type.upper() + '/'
            # print ' ---- freight_type', freight_type
            seq_ids = seq_obj.search(
                cr, uid, [
                    ('company_id', '=', fs_brw.company_id.id),
                    ('code', '=', seq_type_code),
                    ('prefix', '=', freight_type)],
                context=context)
            #print ' ---- seq_ids', seq_ids
            if not seq_ids:
                values = {
                    'name': 'Freight Shipment - ' + fs_brw.company_id.name,
                    'code': seq_type_code,
                    'prefix': freight_type,
                    'padding': 6,
                    'number_increment': 1,
                    'company_id': fs_brw.company_id.id 
                }
                seq_ids = [seq_obj.create(cr, uid, values, context=context)]
                #print ' ---- create new sequence', seq_ids
            #for seq_brw in seq_obj.browse(cr, uid, seq_ids, context=context):
                #print ' ---- seq', (
                #   seq_brw.id, seq_brw.name, seq_brw.code,
                #   seq_brw.company_id.name, seq_brw.prefix,
                #   seq_brw.implementation)
            sequence = seq_obj.next_by_id(cr, uid, seq_ids[0], context=context)
            self.write(
                cr, uid, fs_brw.id, {'sequence': sequence}, context=context)
            #print ' ---- sequence', sequence 
            #print ' ---- context', context
        return True

    def _set_exception_msg(self, cr, uid, ids, etype, context=None):
        """
        It set the exception log messages in the correspoding freight
        shipments.
        @param etype: the exception type. could be:
                      - 'out_volumetric_weight'
                      - 'out_weight
        @return: True
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids
        exception = self._get_fields_exceptions(cr, uid, context=context)
        if etype not in exception.keys():
            raise osv.except_osv(
                _('Programming Error!!'),
                _('The exception to be set by the _set_exception_msg method is'
                  ' not defined. please if you want to use this field need to'
                  ' create the exception first. You need to modify the'
                  ' dictionary return by the _get_fields_exception method.'))

        for fs_brw in self.browse(cr, uid, ids, context=context):
            string_param = tuple(
                 [getattr(fs_brw, val) for val in exception[etype]['values']])
            values = {'message_exceptions':
                (fs_brw.message_exceptions or '')
                + (exception[etype]['error_msg'] % string_param)}
            self.write(cr, uid, fs_brw.id, values, context=context)
        return True

    def _get_fields_exceptions(self, cr, uid, context=None):
        """
        This method define a dictonary that manage the maximum and recommend
        weight fields with exception data like error message and values
        implicated. If there is a weight field exception then this data is
        used.
        @return: dictonary with the defined exceptions like:
            {field_name : {'error_msg', 'values'}}
        """
        context = context or {}
        exception_dict = {
            'out_volumetric_weight': {
                'error_msg':
                _(' - Outgoing Volumetric Weight Exceeded:'
                  ' The volumetric weight of the outgoing orders in the %s'
                  ' shipment is greater than the volumetric weight capacity'
                  ' of the used transport unit (%s > %s).\n'),
                'values':
                ['name', 'out_volumetric_weight', 'max_volumetric_weight'],
            },
            'out_weight': {
                'error_msg':
                _(' - Outgoing Weight Exceeded:'
                  ' The weight of the outgoing orders in the %s shipment'
                  ' is greater than the physical weight capacity of the'
                  ' used transport unit (%s > %s).\n'),
                'values':
                ['name', 'out_weight', 'max_weight'],
            },
            'in_volumetric_weight': {
                'error_msg':
                _(' - Incoming Volumetric Weight Exceeded:'
                  ' The volumetric weight of the incoming orders in the %s'
                  ' shipment is greater than the volumetric weight capacity'
                  ' of the used transport unit (%s > %s).\n'),
                'values':
                ['name', 'in_volumetric_weight', 'max_volumetric_weight'],
            },
            'in_weight': {
                'error_msg':
                _(' - Incoming Weight Exceeded:'
                  ' The weight of the incoming orders in the %s shipment'
                  ' is greater than the physical weight capacity of the'
                  ' used transport unit (%s > %s).\n'),
                'values':
                ['name', 'in_weight', 'max_weight'],
            }
        }
        return exception_dict

    def action_assign(self, cr, uid, ids, context=None):
        """
        Change the state of a freight shipment order from 'awaiting' to
        'exception' or to 'confirm' state and also set a sequence number
        to the freight shipment because is confirmed with or with no
        exceptions.
        The freight shipment change to 'confirm' state is the freight shipment
        values fulfill some conditions, otherwise the freight shipment will
        change to 'expception' state.
        The evaluated conditions are:

          - that the accumulated volumetrict weight capacity of the freight is
            less or equal to max volumetrict weight capacity for this freight.
          - that the accumulated  weight capacity of the freight is less or
            equal to max weight capacity for this freight.

        @return: True
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids
        error_msg = \
            _('Your current burden exceeds the maximum transport unit'
              ' %s capacity. This freight shipment Assing can not be done.'
              ' Please remove some orders items to continue.')
        for fso_brw in self.browse(cr, uid, ids, context=context):
            for scope in ['in', 'out']:
                for max_field in  ['max_volumetric_weight', 'max_weight']:
                    if not self.is_weight_fulfill(
                        cr, uid, fso_brw.id, scope, max_field,
                        context=context):
                        raise osv.except_osv(
                            _('Invalid Procedure!!!'), error_msg % (
                                max_field[4:].replace('_', ' ')))

            exceptions = []
            for scope in ['in', 'out']:
                exceptions.append(not self.is_weight_fulfill(
                    cr, uid, fso_brw.id, scope, 'recommended_volumetric_weight', context=context))
                exceptions[-1] and self._set_exception_msg(
                    cr, uid, fso_brw.id, '%s_volumetric_weight' % (scope,), context=context)

                exceptions.append(not self.is_weight_fulfill(
                    cr, uid, fso_brw.id, scope, 'recommended_weight', context=context))
                exceptions[-1] and self._set_exception_msg(
                    cr, uid, fso_brw.id, '%s_weight' %(scope,), context=context)

            self.assign_sequence(cr, uid, fso_brw.id, context=context)
            self.write(
                cr, uid, fso_brw.id,
                {'state': any(exceptions) and 'exception' or 'confirm'},
                context=context)
        return True

    def check_zone(self, cr, uid, ids, context=None):
        """
        @return: True if the pos orders and sale orders asociated to the
        freight shipment are in the same zone of the freight shipment.
        False otherwise.
        """
        context = context or {}
        zone_obj = self.pool.get('freight.zone')
        ids = isinstance(ids, (long, int)) and [ids] or ids
        res = {}.fromkeys(ids)
        for fs_brw in self.browse(cr, uid, ids, context=context):
            order_brws = fs_brw.pos_order_ids + fs_brw.sale_order_ids
            in_zone = []
            for pos_brw in fs_brw.pos_order_ids:
                lat, lon = \
                    (pos_brw.delivery_address.gmaps_lat,
                     pos_brw.delivery_address.gmaps_lon)
                in_zone += [zone_obj.insidezone(
                    cr, uid, fs_brw.zone_id.id, lat, lon, context=context)]
            for so_brw in fs_brw.sale_order_ids:
                lat, lon = \
                    (so_brw.partner_shipping_id.gmaps_lat,
                     so_brw.partner_shipping_id.gmaps_lon)
                #Note: this so_brw.partner_shipping_id may change
                in_zone += [zone_obj.insidezone(
                    cr, uid, fs_brw.zone_id.id, lat, lon, context=context)]
            res[fs_brw.id] = all(in_zone)
        if len(res.keys()) == 1:
            return res.values()[0]
        else:
            return res

    def action_force(self, cr, uid, ids, context=None):
        """
        This method force the freight.shipment to be confirm even if the
        valuation conditions of zone and burden are not fulfilled. This method
        is use by the 'Force Dispatch' button in the freight shipment form at
        the Exception state.
        """
        context = context or {}
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        return True

    def is_weight_fulfill(self, cr, uid, ids, scope, capacity_weight_field,
                          context=None):
        """
        Check if the freight accumulated weight value is less or equal to
        a freight max or recommended weight capacity.
        @param scope: In what scope the capacity field will be checked. Could be in
            incoming or outgoing orders. The possible value of this parameter:
            ['in', 'out']
        @param capacity_weight_field: the name of the weight capacity in the
            freight shipment that want to be check. the possible values are:
                - max_volumetric_weight
                - max_weight
                - recommended_weight
                - recommended_volumetric_weight
        @return: True if the condition is satisfied or False if is not.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = []
        acc_weight = '%s_' %(scope,) + (
            'volumetric_weight' in capacity_weight_field 
            and 'volumetric_weight' or 'weight')

        for fs_brw in self.browse(cr, uid, ids, context=context):
            res.append(
                getattr(fs_brw, acc_weight)
                <= getattr(fs_brw, capacity_weight_field))
        # print ' ---- ', (res, scope, capacity_weight_field)
        if len(ids) == 1:
            return res[0]
        else:
            return res

    def action_back_to_awaiting(self, cr, uid, ids, context=None):
        """
        Return the freight shipment to the awaiting state to make the user the
        posibility of resolve the exceptions.
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
        This method will change the freight shipment from 'Loaded' state to
        Shipped state. It represent the order to make the unit go out and do
        the shipment. It also set the initial_shipped_weight field for log
        history of the freight shipment. It also set the shipment_state of the
        vehicle to busy state indicating that the vehicle is in use because is
        out shippinh a freight shipment.
        @return True
        """
        context = context or {}
        vehicle_obj = self.pool.get('fleet.vehicle')
        ids = isinstance(ids, (long, int)) and [ids] or ids
        for fs_brw in self.browse(cr, uid, ids, context=context):
            self.write(
                cr, uid, fs_brw.id,
                {'state': 'shipped',
                 'initial_shipped_weight': fs_brw.out_weight,
                 'initial_shipped_volumetric_weight':
                 fs_brw.out_volumetric_weight, 
                 'date_shipped': time.strftime('%Y-%m-%d %H:%M:%S')},
                context=context)
            vehicle_obj.write(
                cr, uid, [fs_brw.vehicle_id.id], {'shipment_state': 'busy'},
                context=context)
        return True

    def action_delivered(self, cr, uid, ids, context=None):
        """
        This method will change the freight shipment from Shipped state to
        Delivered state. Used for the Delivered button in the freight shipment
        order. It also set the vehicle state to free to indicate that the
        vehicle returns and it can be use for another freight shipment.
        """
        context = context or {}
        vehicle_obj = self.pool.get('fleet.vehicle')
        ids = isinstance(ids, (long, int)) and [ids] or ids
        fs_ids = {'delivered': [], 'shipment_exception': []}
        for fs_brw in self.browse(cr, uid, ids, context=context):
            if self._successfully_delivery_state(cr, uid, fs_brw.id,
                                                 context=context):
                fs_ids['delivered'] += [fs_brw.id]
            else:
                fs_ids['shipment_exception'] += [fs_brw.id]
        fs_ids['delivered'] and self.write(
            cr, uid, fs_ids['delivered'], {
                'state': 'delivered',
                'date_delivered': time.strftime('%Y-%m-%d %H:%M:%S')
            }, context=context)
        fs_ids['shipment_exception'] and self.write(
            cr, uid, fs_ids['shipment_exception'], {
                'state': 'shipment_exception',
                'date_delivered': time.strftime('%Y-%m-%d %H:%M:%S')
            }, context=context)
        #print '---- fs_ids', fs_ids
        vehicle_ids = list(set(
            [fs_brw.vehicle_id.id
             for fs_brw in self.browse(cr, uid, ids,  context=context)]))
        vehicle_obj.write(
            cr, uid, vehicle_ids, {'shipment_state': 'free'}, context=context)
        return True

    def _successfully_delivery_state(self, cr, uid, ids, context=None):
        """
        Checks if all the pickings and pos orders in the freight shipment are
        succesfully delivered. Check every element delivery state field. 
        @return True if all the pos.orders and stock.picking.out associated to
        the given fregith shipment have been succesfully shipped. False
        otherwise.
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids
        res = {}.fromkeys(ids)
        for fs_brw in self.browse(cr, uid, ids, context=context):
            pending_items = []
            for pos_brw in fs_brw.pos_order_ids:
                if pos_brw.delivery_state != 'delivered':
                    pending_items.append(pos_brw.id)
            for picking_brw in fs_brw.out_picking_ids:
                if picking_brw.delivery_state != 'delivered':
                    pending_items.append(picking_brw.id)
            res[fs_brw.id] = not pending_items and True or False
            #print '---- fs %s pending_items %s' % (fs_brw.id, pending_items)
        if len(res.keys()) == 1:
            return res.values()[0]
        else:
            return res

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

    def action_dumping(self, cr, uid, ids, context=None):
        """
        This method is used in the "Release Undelivered Orders" button. Will
        release the pos orders and picking orders that was unsuccessfully
        delivered to be later assing to another freight shipment and be re-
        send.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        pos_obj = self.pool.get('pos.order')
        picking_obj = self.pool.get('stock.picking')
        for fs_brw in self.browse(cr, uid, ids, context=context):
            pos_ids = \
                [pos_brw.id
                 for pos_brw in fs_brw.pos_order_ids
                 if pos_brw.delivery_state != 'delivered']
            picking_ids = \
                [picking_brw.id
                 for picking_brw in fs_brw.out_picking_ids
                 if picking_brw.delivery_state != 'delivered']
            pos_obj.write(
                cr, uid, pos_ids,
                {'freight_shipment_id': False, 'delivery_state': 'exception'},
                context=context)
            picking_obj.write(
                cr, uid, picking_ids,
                {'in_fs_id': False, 'out_fs_id': False,
                 'delivery_state': 'exception'}, context=context) 
        self.write(
            cr, uid, ids, {
                'state': 'delivered',
                'is_complete_delivered': False}, context=context)
        #print '---- pos_ids', pos_ids
        #print '---- picking_ids', picking_ids
        return True

    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
                context=None, count=False, access_rights_uid=None):
        """
        Overwrite the _search() method to filter the freight shipments in the
        sale order form taking into account the partner shipment zone (with
        the partnet shipment address), the work_shift and the delivery date. 
        """
        context = context or {}
        partner_obj = self.pool.get('res.partner')
        incoterm_obj = self.pool.get('stock.incoterms')
        if (context.get('filter_freight_shipment_ids', False)):
            incoterm_id = context.get('incoterm', False)
            is_delivery = incoterm_id and incoterm_obj.browse(
                cr, uid, incoterm_id, context=context).is_delivery or False
            partner_shipping_id = context.get('partner_shipping_id', False)
            work_shift = context.get('work_shift', False)
            delivery_date = context.get('delivery_date', False)

            if is_delivery:
                if partner_shipping_id:
                    zone_ids = partner_obj.get_zone_ids(
                        cr, uid, partner_shipping_id, context=context)
                    if zone_ids:
                        args.append(['zone_id', 'in', zone_ids])
                if work_shift:
                    args.append(['work_shift','=', work_shift])
                if delivery_date:
                    args.append(['date_delivery', '<=', delivery_date])
        return super(freight_shipment, self)._search(cr, uid, args,
                     offset=offset, limit=limit, order=order, context=context,
                     count=count, access_rights_uid=access_rights_uid)


class sale_order(osv.Model):

    _inherit = "sale.order"

    def _get_shipment_weight(self, cr, uid, ids, field_name, arg,
                             context=None):
        """
        This is a method for a fucntional field. It calculate the weight of the
        sale order by getting the moves associated to every sale orde line at
        the sale order and then sum the correspoding weight or
        volumetric weight field of the products.
        @param filed_name: the name of the field. it could be 'shipment_weight'
                           or 'shipment_volumetric_weight'.
        @return: a dictionary with sale order ids as keys and the weight sum
                 at the values.
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids 
        res = {}.fromkeys(ids, 0.0)
        weight_field = 'move_brw.product_id.' + \
            (field_name == 'shipment_weight' and 'product_tmpl_id.weight' or
             field_name == 'shipment_volumetric_weight' and 'volumetric_weight' or 0.0)
        for so_brw in self.browse(cr, uid, ids, context=context):
            move_brws = \
                [move_brw
                 for picking_brw in so_brw.picking_ids
                 for move_brw in picking_brw.move_lines]
            for move_brw in move_brws:
                res[so_brw.id] += (move_brw.product_qty * eval(weight_field))
        return res

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
        'delivery_date': fields.datetime(
            'Estimated Delivery Date',
            help='The date that this sale order need to be delivered'),
        'work_shift': fields.selection(
            [('morning', 'Morning'),
             ('afternoon', 'Afternoon'),
             ('night', 'Night')],
            string='Work Shift',
            help='Work Shift'),
        'shipment_weight': fields.function(
            _get_shipment_weight,
            string='Shipment Weight',
            type='float',
            help='The Shipment Weight sum of the sale order lines'),
        'shipment_volumetric_weight': fields.function(
            _get_shipment_weight,
            string='Shipment Volumetric Weight',
            type='float',
            help='The Shipment Volumetric Weight sum of the sale order lines'),
    }

    def onchange_partner_shipping_id(self, cr, uid, ids, context=None):
        """
        This is an onchange method used in the sale order form view at the
        partner_shipping_id field. When this field change whatever another
        partner or clear value then the prefered_freigh_shipment_id field
        will be clear, always.
        """
        context = context or {}
        res = {'value': {'prefered_freight_shipment_id': False}}
        return res

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """
        Overwrite the _prepare_order_picking method to add the prefered fregiht
        shipment order set in the sale order to the pickings generating in
        the confirm sale order process.
        """
        context = context or {}
        res = super(sale_order, self)._prepare_order_picking(
            cr, uid, order, context=context)
        res.update(
            {'out_fs_id': order.prefered_freight_shipment_id.id})
        return res

    # Note: This method is not used yet. Is not of utility in the next
    # iteration then delete it.
    def matching_freight_shipment_ids(self, cr, uid, ids, context=None):
        """
        This method return the ids of the matiching freight shipments that
        match with the sale order configuration:
            - match at zone
            - match at estimated delivery date.
        @return If there is only one sale order id then return the list of
                freight shipments ids matching. If there is more than one
                sale order id then return a dictionary of the form
                (key: sale_order_id, value: corresponding freight shioment ids)
        """
        context = context or {}
        fs_obj = self.pool.get('freight.shipment')
        partner_obj = self.pool.get('res.partner')
        ids = isinstance(ids, (long, int)) and [ids] or ids
        res = {}.fromkeys(ids)
        for sale_brw in self.browse(cr, uid, ids, context=context):
            # check the zones of the delivery address.
            zone_ids = partner_obj.get_zone_ids(
                cr, uid, sale_brw.partner_shipping_id.id, context=context)
            search_criteria = [
                ('zone_id', 'in', zone_ids),
                ('date_delivery', '>=', sale_brw.delivery_date)]
            res[sale_brw.id] = self.search(
                cr, uid, search_criteria, context = context)
        if len(res.keys()) == 1:
            return res.values()[0]
        else:
            return res

    def action_button_confirm(self, cr, uid, ids, context=None):
        """
        This method overwrite the original action_button_confirm method at the
        sale module to add a verification before launch the action.
        This verification consist on check if the incoterm delivery type is
        for delivery (the sale order have to be delivered using a freight
        shipment) and restict the user to confirm a sale order until the
        prefered freight shipment field is set.
        @return: ir.actions.act_window defined in the original method.
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        so_brw = self.browse(cr, uid, ids[0], context=context)
        if (so_brw.incoterm and so_brw.incoterm.is_delivery
            and not so_brw.prefered_freight_shipment_id):
            raise osv.except_osv(
                _('Invalid Procedure!!!'),
                _('Sale Order use a incoterm of type delivery, please you need'
                  ' to set the Prefered Freight Shipment field to continue.'
                  ' Or, you can change the incoterm used to one that is not'
                  ' for delivery.'))
        return super(sale_order, self).action_button_confirm(
            cr, uid, ids, context=context)


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
        picking_field = picking_type in ['out'] and 'out_fs_id' or 'in_fs_id'
        res.update(
            {'%s' % (picking_field,): eval('picking.%s.id' % picking_field)})
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

    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
                context=None, count=False, access_rights_uid=None):
        """
        Overwrite the _search() method to filter the pos order items in the
        freight shipment form taking into account the delivery address zone
        of the freight shipment with the ones in de delivery address of the
        pos orders.
        """
        context = context or {}
        partner_obj = self.pool.get('res.partner')
        pos_obj = self.pool.get('pos.order')
        if (context.get('filter_pos_order_by_zone', False)):
            zone_id = context.get('filter_zone_id', False)
            if not zone_id:
                raise osv.except_osv(
                    _('Error!'),
                    _('Please you need to define the freight shipment zone'
                      ' first to filter the possible POS orders to be add.'))
            else:
                context.pop('filter_pos_order_by_zone')
                context.pop('filter_zone_id')
                pos_ids = pos_obj.search(
                    cr, uid, [('delivery', '=', True)], context=context)
                fs_zone_pos_ids = []
                for pos_brw in pos_obj.browse(cr, uid, pos_ids, context=context):
                    if (pos_brw.delivery_address and
                        zone_id in partner_obj.get_zone_ids(
                            cr, uid, pos_brw.delivery_address.id,
                            context=context)):
                        fs_zone_pos_ids.append(pos_brw.id)
                fs_zone_pos_ids and args.append(['id', 'in', fs_zone_pos_ids])
        return super(pos_order, self)._search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count, access_rights_uid=access_rights_uid)

    def onchange_delivery_address(self, cr, uid, ids, context=None):
        """
        This is an onchange method over the delivery_address field in the pos
        order form view, that clears the freight_shipment_id field every time
        the delivery_address field change or its be clear.
        """
        context = context  or {}
        res = {'value': {'freight_shipment_id': False}}
        return res

    def onchange_partner_id(self, cr, uid, ids, part=False, context=None):
        """
        This is an onchange method used in the pos order form view at the
        partner_id field. When this field change whatever another
        partner or clear value then the delivery_address field will be clear,
        always.
        """
        context = context or {}
        res = super(pos_order, self).onchange_partner_id(
            cr, uid, ids, part, context=context)
        res['value']['delivery_address'] = False
        return res

    def create_picking(self, cr, uid, ids, context=None):
        """
        Overwrithe the create_picking method defined at the point of sale
        module to add the pos_id field when creating the stock picking out
        of the pos order.
        @return: True
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids
        super(pos_order, self).create_picking(cr, uid, ids, context=context)
        for pos_brw in self.browse(cr, uid, ids, context=context):
            if not pos_brw.state=='draft':
                continue
            if pos_brw.picking_id:
                pos_brw.picking_id.write(
                    {'pos_id': pos_brw.id}, context=context)
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
        'recommended_physical_capacity' : fields.float(
            'Recommended Physical Weight Capacity',
            help=('This is the maxime physical weight quantity recommended for'
                  ' save use of the vehicle')),
        'recommended_volumetric_capacity' : fields.float(
            'Recommended Volumetric Weight Capacity',
            help=('This is the maxime volumetric weight quantity recommended'
                 ' for save use of the vehicle')),
        'shipment_state': fields.selection(
            [('free', 'Free'),
             ('busy', 'Busy'),
             ('mtto', 'Maintenance')],
             'Shipment State',
             help=('The state for shipment use of the vehicle:'
                   '  - Free: Avaible for use.\n'
                   '  - Busy: The vehicle is in use.\n'
                   '  - Maintenance: The vehicle is in maintenance and can not'
                   '    be use.\n')),
    }

    _defaults = {
        'shipment_state': 'free',
    }

    def action_maintenance(self, cr, uid, ids, context=None):
        """
        This method is used in a button at the vehicle form view that set the
        vehicle shipment state to Maintenance. This method it verify the
        current vehicle state first and then it update the state taking this
        criteria:
            - If vehicle is free then it can change to maintenance.
            - If vehicle is busy then it can not change to maintenance.
            - If vehicle is maintenance then it is pointless to change state.

        Note: this method works with 3 vehicle shipment state defined at the
              time this method was designed: 'free', 'busy' and 'maintenance'
              shipment states. If any other programmer add a new shipment state
              then will raise an exception indicating that this method need to
              be redefine by that shipment state too.

        @return True
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids
        error_msg = str()
        valid_shipment_states = ['free', 'busy', 'mtto']
        vehicles =  {}.fromkeys(valid_shipment_states)
        for key in vehicles:
            vehicles[key] = []

        for vehicle_brw in self.browse(cr, uid, ids, context=context):
            if vehicle_brw.shipment_state in vehicles.keys():
                vehicles[vehicle_brw.shipment_state].append(vehicle_brw)
            else:
                vehicles[vehicle_brw.shipment_state] = [vehicle_brw]
      
        new_states = set(vehicles.keys()) - set(valid_shipment_states) 
        if new_states:
            raise osv.except_osv (
                _('Programming Error!!!'),
                _('The action_maintenance() method at the freight shipment'
                  ' module must be re-write. Only manage the [\'free\','
                  ' \'busy\', \'maintenance\'] shipment state but there are'
                  ' anothers states defined that need to be process.\n\n'
                  ' New shipment states:\n%s' % (list(new_states), )))

        if vehicles['busy']:
            error_msg += \
                _('The next transport units are busy so they can not be sent'
                  ' to maintenance.\n\n %s' % (
                    [v.name for v in vehicles['busy']]))
        elif vehicles['mtto']:
            error_msg += \
                _('The next transport units are already in maintenance.\n\n %s'
                  % ([v.name for v in vehicles['mtto']]))
        if error_msg:
            raise osv.except_osv(_('Warning!!!'), error_msg)

        self.write(
            cr, uid, [v.id for v in vehicles['free']],
            {'shipment_state': 'mtto'}, context=context)
        return True

    def action_free(self, cr, uid, ids, context=None):
        """
        This method is a object type button at the vehicle form view that make
        the change of the vehicle from maintenance shipment state to free.
        @return True
        """
        context = context or {}
        ids = isinstance(ids, (long, int)) and [ids] or ids
        vehicle_ids = \
            [v.id
             for v in self.browse(cr, uid, ids, context=context)
             if v.shipment_state == 'mtto']
        self.write(
            cr, uid, vehicle_ids, {'shipment_state': 'free'}, context=context)
        return True

class res_partner(osv.Model):

    _inherit = 'res.partner'
    
    def get_zone_ids(self, cr, uid, ids, context=None):
        """
        Check on every zone defined.
        @return: a list of zone ids where the partner given belongs. 
        """
        context = context or {}
        zone_obj = self.pool.get('freight.zone')
        ids = isinstance(ids, (long, int)) and [ids] or ids
        res = {}.fromkeys(ids)
        zone_ids = zone_obj.search(cr, uid, [], context=context)
        for partner_brw in self.browse(cr, uid, ids, context=context):
            res[partner_brw.id] = \
                [zone_id
                 for zone_id in zone_ids
                 if zone_obj.insidezone(
                    cr, uid, zone_id, partner_brw.gmaps_lat,
                    partner_brw.gmaps_lon, context=context)]
        if len(res.keys()) == 1:
            return res.values()[0]
        else:
            return res


class purchase_order(osv.Model):

    _inherit = 'purchase.order'
    _columns = {
        'freight_shipment_id': fields.many2one(
            'freight.shipment',
            string='Freight Shipment',
            help='The Freight shipment that will collect the purchase order.'),
        'prefered_fs_id': fields.many2one(
            'freight.shipment',
            string='Prefered Freight Shipment',
            help=('The shipment planned to collect the purchase order'
                  ' products.'
                  ' Represent the first shipment order option.'
                  ' However, is not always the really shipment order used.')),
        'fs_ids': fields.many2many(
            'freight.shipment',
            'purchase_order_freight_shipment_rel',
            'purchase_id', 'fs_id',
            string='Final Freight Shipments',
            help=('The real shipment order where this purchase order was'
                  ' collected.'
                  ' A purchase order could be collected by parts, so more than'
                  ' one shipment order can be used.')),
    }

