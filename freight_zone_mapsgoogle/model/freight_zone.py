#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha <humbertoarocha@gmail.com>
#    Audited by: Nhomar Hernandez <nhomar@gmail.com>
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
from openerp import tools
import datetime
import openerp.addons.decimal_precision as dp

class freight_zone_mapsgoogle(osv.Model):
    _name = 'freight.zone.mapsgoogle'
    _description = 'Zone'
    _columns = {
        'name' : fields.char('Zone Name', 256, required=True, help='Zone Name'),
        'gmaps_area_ids' : fields.one2many('freight.area.mapsgoogle', 'gmaps_zone_id', 'Area', help=''),
    }

class freight_area_mapsgoogle(osv.Model):
    _name = 'freight.area.mapsgoogle'
    _rec_name = 'id'
    _description = 'Area'
    _columns = {
       # 'name' : fields.char('Area', 256, help='Area'),
        'gmaps_zone_id' : fields.many2one('freight.zone.mapsgoogle', 'Zone', help=''),
        'gmaps_lat': fields.float('Latitude', required=True, 
            digits_compute=dp.get_precision('Gmaps'), help="Point's Latitude"),   
        'gmaps_lon': fields.float('Longitude', required=True,
            digits_compute=dp.get_precision('Gmaps'), help="Point's Longitude"),   
    }
