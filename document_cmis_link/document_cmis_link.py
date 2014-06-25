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


class document_directory(osv.osv):

    _inherit = 'document.directory'

    _columns = {
        'cmis_dropoff': fields.char('CMIS DropOff ID', size=256),
    }

class document_cmis_link(osv.osv_memory):

    _name = 'document.cmis.link'

    _columns = {
        'document_ids': fields.many2many('document.cmis.link.doc', 'document_cmis_link_rel', 'document_id', 'wizard_id', 'Documents'),
    } 

    def default_get(self, cr, uid, fields, context=None):
        """Load the CMIS drop-off documents in memory"""
        if context is None:
            context = {} 

        attach_obj = self.pool.get('ir.attachment')
        directory_obj = self.pool.get('document.directory')
        link_obj = self.pool.get('document.cmis.link.doc')

        #CLean up the links
        links = link_obj.search(cr, uid, [])
        link_obj.unlink(cr, uid, links) 

        repo = attach_obj.cmis_connect(cr, uid)
        if not repo:
            raise osv.except_osv(_('Error!'),_("Cannot find the default repository in the CMIS Server."))

        model_id = self.pool.get('ir.model').search(cr, uid, [('model','=',context['active_model'])])[0]
        dirs = self.pool.get('document.directory').search(cr, uid, [('ressource_type_id','=',model_id)])

        dir_found = False

        for directory in self.pool.get('document.directory').browse(cr, uid, dirs):
            # Process only for CMIS enabled directories
            if not directory.cmis_dropoff:
                continue
            dir_found = True

            # Find the CMIS dropoff directory
            try:
                cmisDir = repo.getObject(directory.cmis_dropoff)
            except:
                raise osv.except_osv(_('Error!'),_("Cannot find this directory (%s) in the DMS. You may not have the right to access it."%(directory.name)))

            if not cmisDir:
                raise osv.except_osv(_('Error!'),_("No CMIS Drop Off Directory found for the key : %s"%(directory.cmis_dropoff)))

            # Get the directory files list
            childrenRS = cmisDir.getChildren()
            children = childrenRS.getResults()
            
            for child in children:
                link_obj.create(cr, uid, {'name':child.properties['cmis:name'], 'cmis_key':child.properties['cmis:objectId']})

        if not dir_found:
            raise osv.except_osv(_('Error!'),_("No Drop off Directory found for this model : %s"%(context['active_model'])))


        return super(document_cmis_link, self).default_get(cr, uid, fields, context=context)


    def cmis_document_link(self, cr, uid, ids, context=None):
        """Display the list of the documents found on the ressource cmis dropoff directory and allow to select and link a document as attachment"""

        attach_obj = self.pool.get('ir.attachment')
        wizard = self.pool.get('document.cmis.link').browse(cr, uid, ids[0])
        docs = wizard.document_ids

        repo = attach_obj.cmis_connect(cr, uid)
        if not repo:
            raise osv.except_osv(_('Error!'),_("Cannot find the default repository in the CMIS Server."))

        for doc in docs:
            cmisFile = repo.getObject(doc.cmis_key)

            # If a document is found
            # Download the file (Uses a bit of bandwidth but then it just have to rely on the document_cmis code)
            result = cmisFile.getContentStream()
            c = result.read()
            content = base64.encodestring(c)

            inv_vals = { 
                'res_model': context['active_model'],
                'res_id': context['active_id'],
                'name': doc.name,
                'datas_fname': doc.name,
                'datas': content,
            }

            # Create the Attachment
            attach_id = attach_obj.create(cr, uid, inv_vals, context=context)
            if attach_id:
                # Delete the temporary document from the dropoff
                cmisFile.delete()
            else:
                raise osv.except_osv(_('Error!'),_("Cannot create this attachment"))

        return True

class document_cmis_link_doc(osv.osv_memory):

    _name = 'document.cmis.link.doc'

    _columns = {
        'name': fields.char('File Name', size=128),
        'cmis_key': fields.char('CMIS Key', size=256),
        'wizard_id': fields.many2one('document.cmis.link', 'Wizard', required=False),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
