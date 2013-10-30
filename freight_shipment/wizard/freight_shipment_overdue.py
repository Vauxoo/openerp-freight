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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class freight_shipment_overdue(osv.osv_memory):

    _name = "freight.shipment.overdue"
    _description = "Check Overdues"

    """
    Freight Shipment Overdue
    """

    def check_overdue(self, cr, uid, ids, context=None):
        """
        This function check the dates of the freight shipment and compare them.
        If the freight shipment have any overdue the the freight shipment
        is_overdue field is change to True if not is change to False.
        """
        context = context or {}
        fs_obj = self.pool.get('freight.shipment')
        for form in self.read(cr, uid, ids, context=context):
            fs_ids = {True: [], False: []}
            for fs_id in context['active_ids']:
                if (fs_obj._check_shipment_overdue(
                        cr, uid, fs_id, context=context) or
                        fs_obj._check_prepare_overdue(
                            cr, uid, fs_id, context=context)):
                    fs_ids[True] += [fs_id]
                else:
                    fs_ids[False] += [fs_id]
            fs_obj.write(
                cr, uid, fs_ids[True], {'is_overdue': True}, context=context)
            fs_obj.write(
                cr, uid, fs_ids[False], {'is_overdue': False}, context=context)
        return {'type': 'ir.actions.act_window_close'}

