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

class freight_zone(osv.Model):
    _name = 'freight.zone'
    _inherit = ['gmaps.group']
    _columns = {
            'name':fields.char('Name', 264, help='Name'), 
            
            }

    def insidezone(self, cr, uid, ids, gmaps_lat, gmaps_lon, zone_id=None, context=None):
        """
        determines if a point is inside a zone using geographical coordinates
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        if zone_id:
            list_zone = self.browse(cr, uid, [zone_id], context=context)
        else:
            list_zone = self.browse(cr, uid, ids, context=context)

        latlng = (gmaps_lat, gmaps_lon)
        
        #latlng = (10.48409,-66.910408) #Si, prueba
        #latlng = (10.531078,-66.971445) #No, prueba
        #latlng = (10.516437,-66.950099) #Si, prueba
        #latlng = (10.476310, -66.893070) #Si, "Santa Mónica, Caracas, Distrito Metropolitano de Caracas, Venezuela"

        for zone in list_zone: 
            puntos = zone.gmaps_point_ids
            inPoly = False
            j = len(puntos) - 1
            for i in xrange(0, len(puntos) ):
                p1 = puntos[i]
                p2 = puntos[j]
                
                if(p1.gmaps_lon < latlng[1] and p2.gmaps_lon >= latlng[1] or p2.gmaps_lon <
                        latlng[1] and p1.gmaps_lon >= latlng[1]):
                    if(p1.gmaps_lat + (latlng[1] - p1.gmaps_lon) / (p2.gmaps_lon - p1.gmaps_lon ) *
                            (p2.gmaps_lat - p1.gmaps_lat) < latlng[0]):
                        inPoly = not inPoly

                j = i

        return inPoly


    def maps(self, cr, uid, ids, context = None):
        context = context and context or {}
        ids = isinstance(ids, (int, long)) and ids or ids[0]
        print "******** %s " % (ids)
        return {
            'name': _('Gmaps Zone'),
            'res_model': 'freight.zone',
            'res_id': ids,
            'type': 'ir.actions.client',
            'tag' : 'gmaps.example',
            'params' : {
                'domain':[
                    ('res_id','=',ids),
                ],
            },
        }                                   
