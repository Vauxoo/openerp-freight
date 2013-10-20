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
    
class freight_zone_mapsgoogle(osv.Model):
    _name = 'freight.zone.mapsgoogle'
    _description = 'Zone'
    _columns = {
        'name' : fields.char('Zone Name', 256, help='Zone Name'),
        'area_ids' : fields.one2many('freight.area.mapsgoogle', 'zone_id', 'Area', help=''),
    }

class freight_area_mapsgoogle(osv.Model):
    _name = 'freight.area.mapsgoogle'
    _description = 'Zone Benchmark'
    _columns = {
        'name' : fields.char('Area', 256, help='Area'),
        'zone_id' : fields.many2one('freight.zone.mapsgoogle', 'Zone', help=''),
        'latitude': fields.integer('Latitude', help="Point's Latitude"),   
        'longitude': fields.integer('Longitude', help="Point's Longitude"),   
    }
