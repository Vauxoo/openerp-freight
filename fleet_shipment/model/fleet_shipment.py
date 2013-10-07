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
    }

    _defaults = {
        'state': 'draft',
    }

class pos_order(osv.Model):

    _inherit = "pos.order"

    _columns = {
        'fleet_shipment_id': fields.many2one(
            'fleet.shipment',
            string='Fleet Shipment',
            required=True,
            help='Fleet Shipment'),
    }


