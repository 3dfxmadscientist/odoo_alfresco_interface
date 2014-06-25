# -*- coding: utf-8 -*-
##############################################################################
#
#    Smart Solution bvba
#    Copyright (C) 2010-Today Smart Solution BVBA (<http://www.smartsolution.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################## 

{
    "name" : "document_cmis",
    "version" : "1.0",
    "author" : "Smart Solution (fabian.semal@smartsolution.be)",
    "website" : "www.smartsolution.be",
    "category" : "Generic Modules/Document Management",
    "description": """
    The Alfresco interface module replaces the standard database or FTP document storage of OpenERP by Alfresco
    When an attachment is added to a resource, the document is send to Alfresco
    When opening an attachment, the document is opened in Alfresco and if the type is recognized, the document is previewed
    When the attachment is deleted, the document is deleted in Alfresco
    Relies on the standard DMS directory configuration of OpenERP. It allows to freely configure where each resource will be stored in Alfresco. Even across multiple Alfresco sites.
""",
    "depends" : ["document", "web_attach_extended"],
    "data" : [
        'document_cmis_view.xml',
        'document_cmis_data.xml',
        'security/document_cmis_security.xml'
#        'security/ir.model.access.csv'
        ],
    "active": False,
    "installable": True
}
