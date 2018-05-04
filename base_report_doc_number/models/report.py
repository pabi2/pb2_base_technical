# -*- coding: utf-8 -*-

import time
import base64
import logging

from openerp import models, api, fields

_logger = logging.getLogger(__name__)


def get_file_name(filename, report, eval_args):
    if filename and report.save_as_prefix:
        filename = eval(report.save_as_prefix, eval_args)
    return filename


class IRactionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    save_as_prefix = fields.Char(
        string='Save as Prefix',
        help='This is the filename of the \
        save as used to store the printing result.\
        Keep empty to not save the printed reports with given prefix.\
        You can use a python expression with the\
        object and time variables. Do not give file extension.',
    )


class Report(models.Model):
    _inherit = "report"

    @api.v7
    def _check_attachment_use(self, cr, uid, ids, report):
        """ Check attachment_use field.
        If set to true and an existing pdf is already saved, load
        this one now. Else, mark save it.
        """
        save_in_attachment = {}
        save_in_attachment['model'] = report.model
        save_in_attachment['loaded_documents'] = {}

        if report.attachment:
            for record_id in ids:
                obj = self.pool[report.model].browse(cr, uid, record_id)
                filename = eval(report.attachment, {'object': obj,
                                                    'time': time})
                # Call hook to change filename
                eval_args = {'object': obj, 'time': time}
                filename = get_file_name(filename, report, eval_args)
                # If the user has checked 'Reload from Attachment'
                if report.attachment_use:
                    alreadyindb = [('datas_fname', '=', filename),
                                   ('res_model', '=', report.model),
                                   ('res_id', '=', record_id)]
                    attach_ids = self.pool['ir.attachment'].search(cr, uid,
                                                                   alreadyindb)
                    if attach_ids:
                        # Add the loaded pdf in the loaded_documents list
                        pdf = self.pool['ir.attachment'].\
                            browse(cr, uid, attach_ids[0]).datas
                        pdf = base64.decodestring(pdf)
                        save_in_attachment['loaded_documents'][record_id] = pdf
                        _logger.info('The PDF document %s was \
                            loaded from the database' % filename)
                        # Do not save this document as we already ignore it
                        continue

                # If the user has checked 'Save as Attachment Prefix'
                if filename is False:
                    # May be false if, for instance,
                    # the 'attachment' field contains a condition
                    # preventing to save the file.
                    continue
                else:
                    save_in_attachment[record_id] = filename
                    # Mark current document to be saved
        return save_in_attachment
