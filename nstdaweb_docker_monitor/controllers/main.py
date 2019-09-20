# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenElanz
#    Copyright (C) 2012-2013 Elanz Centre (<http://www.openelanz.fr>).
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

import logging
import ssl

import openerp
from openerp import http
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _

from openerp.addons.web.controllers import main
from openerp.addons.web.controllers.main import Session
from datetime import datetime
import datetime

_logger = logging.getLogger(__name__)
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


class nstdaweb_docker_monitor_http(http.Controller):
    @http.route('/app/nstdaweb_docker_monitor/get_port', auth='public')
    def index(self, api_key=None, api_secret=None, m=None):
        if not api_key or not api_secret or not m:
            return "-1"
        env_source = request.env['nstdaweb.docker.monitor.source']
        source = env_source.sudo().search(
            [('api_key', '=', api_key), ('api_secret', '=', api_secret)], limit=1
        )
        port = '-1'
        if source:
            port = source.sudo().forecast_port(m)
        else:
            port = "-1"
        return str(port)

    @http.route('/app/nstdaweb_docker_monitor/last_use', auth='public')
    def last_use(self, api_key=None, api_secret=None):
        if not api_key or not api_secret:
            return "-1"
        monitor = request.env['nstdaweb.docker.monitor.source']
        source = monitor.sudo().search(
            [('api_key', '=', api_key), ('api_secret', '=', api_secret)], limit=1
        )
        last_use_data = "-1"
        if source:
            last_use_data = source.sudo().last_use_data()
        else:
            last_use_data = "-1"
        return str(last_use_data)

    @http.route('/app/nstdaweb_docker_monitor/standby', auth='public')
    def standby(self, api_key=None, api_secret=None):
        if not api_key or not api_secret:
            return "-1"
        monitor = request.env['nstdaweb.docker.monitor.source']
        source = monitor.sudo().search(
            [('api_key', '=', api_key), ('api_secret', '=', api_secret)], limit=1
        )
        data = "-1"
        if source:
            data = source.sudo().set_standby()
        else:
            data = "-1"
        return str(data)
    

