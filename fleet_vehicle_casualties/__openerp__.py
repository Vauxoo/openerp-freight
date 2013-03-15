#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    oszckar@gmail.com
#
#    Developed by Oscar Alcala <oszckar@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Fleet Vehicle Casualties",
    "version" : "0.1",
    "depends" : ["fleet_special_equipment","crm_claim"],
    "author" : "Vauxoo",
    "description" : """
        This module adds the following features: Add vehicle casualties as car crashes and several kind of accidents.
    
                    """,
    "website" : "http://vauxoo.com",
    "category" : "Managing vehicles and contracts",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "fleet_vehicle_casualties_view.xml",
    ],
    "active": False,
    "installable": True,
}
