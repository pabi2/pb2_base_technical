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
import re

import openerp
from openerp import http
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _

from openerp.addons.web.controllers import main
from openerp.addons.web.controllers.main import Session
from datetime import datetime
import datetime
from openerp.addons.nstdaconf_report import jasperclient

_logger = logging.getLogger(__name__)


class nstdaweb_report_api_clone_jasper(http.Controller):
    
    # api_key='xxxxx'
    # api_secret='xxxxx'
    # m='nstda_gnc'
    # odootesturl='o-test-28001.intra.nstda.or.th'
    # dbport='29001'
    
    @http.route('/app/nstdaweb_report_api/clone_jasper', auth='public')
    def clone_jasper(self, api_key=None, api_secret=None, m=None, odootesturl=None, dbport=None):
        if not api_key or not api_secret or not m or not odootesturl or not dbport:
            return "-1"
        env_source = request.env['nstdaweb.docker.monitor.source']
        env_adminmanage = request.env['nstdaconf.adminmanage']
        source = env_source.sudo().search(
            [('api_key', '=', api_key), ('api_secret', '=', api_secret)], limit=1
        )
        env_m = env_adminmanage.sudo().search(
            [('name', '=', m)], limit=1
        )
        
        # Work Area
        # STEP 1 Export Service
        # STEP 2 Modefy Zip
        # STEP 3 Import Service
        
        if source and env_m and env_m.jasper_username:
            # Export Service
            ir_config = request.env['ir.config_parameter']
            config_odoo_db_url_test = ir_config.get_param('nstdaconf_report.db_url_test')
            config_odoo_db_name_test = ir_config.get_param('nstdaconf_report.db_name_test')
            
            p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
            re_m = re.search(p, odootesturl)
            host = re_m.group('host')
            host_new = host.replace(".", "_").replace("-", "_")
            
            # GET CONFIG JASPER SERVER PRO ONLY
            config_jasper_url_pro = ir_config.get_param('nstdaconf_report.url_pro')
            config_jasper_username_pro = ir_config.get_param('nstdaconf_report.jaster_user_pro')
            config_jasper_password_pro = ir_config.get_param('nstdaconf_report.jaster_pass_pro')
            
            # EXPORT TO PRO ONLY
            config_odoo_url_pro = ir_config.get_param('nstdaconf_report.odoo_url_pro')
            config_odoo_jaster_prefix_path = ir_config.get_param('nstdaconf_report.jaster_prefix_path')
            config_odoo_url_pro = config_odoo_jaster_prefix_path + "/" + config_odoo_url_pro
            
            config_odoo_url_test = config_odoo_jaster_prefix_path + "/" + host_new
            
            j = jasperclient.JasperClient(config_jasper_url_pro, config_jasper_username_pro, config_jasper_password_pro)
            
            
            ds_uri_server= '/Datasources/' + config_odoo_url_test
            res_uri_server= '/Reports/' + config_odoo_url_test
            
            #ds_uri_server = ds_uri_server.replace("/", "%2F")
            #res_uri_server = res_uri_server.replace("/", "%2F")
            
            ds_uri = '/Datasources/' + config_odoo_url_pro + '/' + m
            res_uri = '/Reports/' + config_odoo_url_pro + '/' + m
            
            ds_uri = ds_uri.replace(".", "_").replace("-", "_")
            res_uri = res_uri.replace(".", "_").replace("-", "_")
            
            user_id = env_m.jasper_username
            filename = host_new
            
            # Download Zip to PRODUCTION
            export = j.export_service(ds_uri, res_uri, user_id, filename)
            if export:
                _logger.info("### [clone_jasper] Download %s  Success!!" % (filename))
                # Modify Zip
                # GET CONFIG ODOO PRO ONLY
                config_odoo_url_pro = ir_config.get_param('nstdaconf_report.odoo_url_pro')
                config_db_url_pro = ir_config.get_param('nstdaconf_report.db_url_pro')
                config_db_port_pro = ir_config.get_param('nstdaconf_report.db_port_pro')
                config_db_name_pro = ir_config.get_param('nstdaconf_report.db_name_pro')
                
                filename = "export_" + host_new + ".zip"
                
                # Replace "." and "-" to "_"
                re_m_pro = re.search(p, config_odoo_url_pro)
                host_pro = re_m_pro.group('host')
                host_new_pro = host_pro.replace(".", "_").replace("-", "_")
            
                replace_serv_prd = host_new_pro
                replace_serv_test = host_new
                
                prd_db_url = config_db_url_pro
                prd_db_port = config_db_port_pro
                prd_db_dbname = config_db_name_pro
                test_db_url = config_odoo_db_url_test
                test_db_port = dbport
                test_db_dbname = config_odoo_db_name_test
                
                if j.modify_zipfile(filename, replace_serv_prd, replace_serv_test, prd_db_url, prd_db_port, prd_db_dbname, test_db_url, test_db_port, test_db_dbname):
                    _logger.info("### [clone_jasper] Modify Zipfile %s Success!!" % filename)
                    # Import Service
                    # GET CONFIG JASPER SERVER TEST ONLY
                    config_jasper_url_test = ir_config.get_param('nstdaconf_report.url_test')
                    config_jasper_username_test = ir_config.get_param('nstdaconf_report.jaster_user_test')
                    config_jasper_password_test = ir_config.get_param('nstdaconf_report.jaster_pass_test')
                    
                    jtest = jasperclient.JasperClient(config_jasper_url_test, config_jasper_username_test, config_jasper_password_test)
                    
                    jtest.delete_resources(res_uri_server)
                    jtest.delete_resources(ds_uri_server)
                    
                    jtest.delete_users(user_id)
                    
                    if jtest.import_service(host_new):
                        _logger.info("### [clone_jasper] Import Service Success!!")
                        return "1"
                    else:
                        _logger.error("### [clone_jasper] Import Service Error!!")
                        return "-1"
                else:
                    _logger.error("### [clone_jasper] Modify Zip Error!!")
                    return "-1"
            else:
                _logger.error("### [clone_jasper] Export Service Error!!")
                return "-1"
        else:
            _logger.warning("### [clone_jasper] Source Not found in Adminmanage!!")
            return "2"  
