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
    "name" : "HR Employee Driver License",
    "version" : "0.1",
    "depends" : ["hr","mail","fleet",],
    "author" : "Vauxoo",
    "description" : """
    This module adds the field driver license and expiration date on the hr_employee model, and also sets
    alarm messages for expiring licenses
    
                    """,
    "website" : "http://vauxoo.com",
    "category" : "Human Resources",
    "init_xml" : [
    ],
    "demo_xml" : ["hr_employee_driver_license_demo.xml"
    ],
    "update_xml" : [
        "hr_employee_driver_license_view.xml",
    ],
    "active": False,
    "installable": True,
}
