#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
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

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from openerp import tools
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
from openerp.addons.crm_partner_assign import crm_partner_assign as CRM
try:
    from googlemaps import GoogleMaps
except:
    _logger.error('Install googlemaps "sudo pip install googlemaps" to use web_gmaps module.')

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {

        'gmaps_lat': fields.float('Geo Latitude', 
            digits_compute=dp.get_precision('Gmaps Partner')),
        'gmaps_lon': fields.float('Geo Longitude',
            digits_compute=dp.get_precision('Gmaps Partner')),
    }
    
    def precise_geo_localize(self, cr, uid, ids, context=None):
        # Don't pass context to browse()! We need country names in english below

        #gmaps = GoogleMaps("http://maps.googleapis.com/maps/api/js?key=AIzaSyBwNE-vFDyyOb62ODaRiqpiL2kz8wR0aTc")
        for partner in self.browse(cr,uid,ids):

            street = partner.street and partner.street or ''
            street2 = partner.street2 and partner.street2 or ''

            address = CRM.geo_query_address(
                street="%s %s" % (street, street2),
                zip=partner.zip,
                city=partner.city,
                state=partner.state_id.name,
                country=partner.country_id.name)

            #lat, lng = gmaps.address_to_latlng(address)
            result = CRM.geo_find(address)
  
            if result:
                self.write(cr, uid, [partner.id], {
                    'gmaps_lat': result[0],
                    'gmaps_lon': result[1],
                }, context=context)
        return True
