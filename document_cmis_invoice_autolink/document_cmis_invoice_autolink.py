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

from osv import osv, fields
from openerp.tools.translate import _
from cmislib.model import CmisClient, Repository
import base64
import logging
_logger = logging.getLogger(__name__)



class account_invoice_autolink(osv.osv):

    _name = "account.invoice.autolink"

    def cmis_document_autolink(self, cr, uid, ids, context=None):
        """Looks for any documents in Alfresco loading directory having the same filename then the supplier invoice reference.
        If a document is found, that document is then attached to the ressource."""

        attach_obj = self.pool.get('ir.attachment')
        attach_id = False

        #Get the "Invoices to Process" directory from the system property
        inv2process_key = self.pool.get('ir.config_parameter').get_param(cr, uid, 'document_cmis.invoice_autolink_directory')

        if not inv2process_key:
                _logger.error("No CMIS Invoice Autolink Directory Key system property found")
                raise osv.except_osv(_('Error!'),_("No CMIS Invoice Autolink Directory Key system property found. Please check the document_cmis.invoice_autolink_directory system property."))

        for invoice in self.pool.get('account.invoice').browse(cr, uid, context['active_ids']):
            if invoice.type == "in_invoice":
                if invoice.supplier_invoice_number:
                    repo = attach_obj.cmis_connect(cr, uid)
                    if not repo:
                        raise osv.except_osv(_('Error!'),_("Cannot find the default repository in the CMIS Server."))

                    # Find the CMIS Invoice Aotulink directory
                    cmisDir = repo.getObject(inv2process_key)
                    if not cmisDir:
                        raise osv.except_osv(_('Error!'),_("No CMIS Invoice Autolink Directory found for the key:"%(inv2process_key)))
    
                    # Get the directory files list
                    childrenRS = cmisDir.getChildren()
                    children = childrenRS.getResults()
                    doc = False

                    #Get the file name
                    name = invoice.supplier_invoice_number.replace(' ','_').replace('/','_') + '.pdf'

                    # Search if a file exists
                    for child in children:
                        if name == child.properties['cmis:name']:
                            cmisFileId = repo.getObject(child.properties['cmis:objectId'])
                            doc = child
                    if not doc:
                        raise osv.except_osv(_('Error!'),_("No document to attach could be found"))

                    # If a document is found
                    # Download the file (Uses a bit of bandwidth but then it just have to rely on the document_cmis code)
                    result = doc.getContentStream()
                    c = result.read()
                    content = base64.encodestring(c)

                    inv_vals = {
                        'res_model': 'account.invoice',
                        'res_id': invoice.id,
                        'name': name,
                        'datas_fname': name,
                        'datas': content,
                    }

                    # Create the Attachment
                    attach_id = attach_obj.create(cr, uid, inv_vals, context=context)
                    if attach_id:
                        # Delete the temporary document
                        doc.delete()
                    else:
                        raise osv.except_osv(_('Error!'),_("Cannot create this attachment"))

                else:
                    raise osv.except_osv(_('Error!'),_("No Supplier Invoice Number could be found for this invoice"))

            else:
                raise osv.except_osv(_('Error!'),_("This functionality only works with Supplier Invoices"))
        
            return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
