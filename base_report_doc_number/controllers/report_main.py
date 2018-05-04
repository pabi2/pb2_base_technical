# -*- coding: utf-8 -*-
import time
import simplejson

from openerp.addons.report.controllers.main import ReportController
from openerp.http import request

from openerp.addons.web.http import route, request
from openerp.addons.web.controllers.main import _serialize_exception
from openerp.tools import html_escape

from werkzeug import url_decode
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from werkzeug.datastructures import Headers


def get_file_name(filename, docids):
    if not docids:
        return filename
    report = request.env['ir.actions.report.xml'].\
        search([('report_name', '=', filename)])
    if not report.save_as_prefix:
        return filename
    docids = str(docids).split(',')
    active_ids = docids
    model = report.model
    if model and active_ids and len(active_ids) == 1:
        record = request.env[model].browse(int(active_ids[0]))
        eval_args = {'object': record, 'time': time}
        new_filename = eval(report.save_as_prefix, eval_args)
        if new_filename:
            filename = new_filename
    return filename


class ReportsNumber(ReportController):

    @route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        """This function is used by 'qwebactionmanager.js' in order to
        trigger the download of a pdf/controller report.

        :param data: a javascript array JSON.stringified containg
        report internal url ([0]) and type [1]
        :returns: Response with a filetoken cookie and an attachment header
        """
        requestcontent = simplejson.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        try:
            if type == 'qweb-pdf':
                reportname = url.split('/report/pdf/')[1].split('?')[0]

                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')

                if docids:
                    # Generic report:
                    response = self.report_routes(reportname,
                                                  docids=docids,
                                                  converter='pdf')
                else:
                    # Particular report:
                    data = url_decode(url.split('?')[1]).items()
                    # decoding the args represented in JSON
                    response = self.report_routes(reportname,
                                                  converter='pdf',
                                                  **dict(data))
                # Call hook to change filename
                reportname = get_file_name(reportname, docids)
                response.headers.add('Content-Disposition',
                                     'attachment; filename=%s.pdf;'
                                     % reportname)
                response.set_cookie('fileToken', token)
                return response
            elif type == 'controller':
                reqheaders = Headers(request.httprequest.headers)
                response = Client(request.httprequest.app,
                                  BaseResponse).get(url,
                                                    headers=reqheaders,
                                                    follow_redirects=True)
                response.set_cookie('fileToken', token)
                return response
            else:
                return
        except Exception, e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return request.make_response(html_escape(simplejson.dumps(error)))
