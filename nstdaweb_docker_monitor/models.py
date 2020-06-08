# -*- coding: utf-8 -*-

from datetime import timedelta
from openerp import models, fields, api, exceptions, _
from openerp.exceptions import ValidationError
from passlib.tests.utils import limit
from datetime import datetime
from datetime import date, timedelta
import datetime
import string
import random
import urllib
import logging
import httplib
import urllib2

_logger = logging.getLogger(__name__)

class nstdaweb_docker_monitor_source(models.Model):
    _name = 'nstdaweb.docker.monitor.source'

    @api.multi
    def action_gen_port(self):
        assert len(
            self) == 1, 'This option should only be used for a single id at a time.'
        env_port = self.env['nstdaweb.docker.monitor.port']
        port_min = int(self.port_min)
        port_max = int(self.port_max) + 1
        if isinstance(port_max, int) and isinstance(port_min, int):
            # Clear
            for p in self.port_ids:
                if p.port not in range(port_min, port_max):
                    p.unlink()
            # Create
            for i in range(port_min, port_max):
                use = self.port_ids.search(
                    [('port', '=', i)], limit=1
                )
                if not use:
                    res = env_port.create({
                        'source_id': self.id,
                        'port': i
                    })
        return True

    @api.one
    def action_reset_api(self):
        assert len(
            self) == 1, 'This option should only be used for a single id at a time.'
        self.api_key = self.api_generator()
        self.api_secret = self.api_generator(32)

    def forecast_port(self, m):
        port = -1
        if self.port_ids:
            already_port = self.port_ids.sudo().search(
                [('source_id', '=', self.id), ('res_module', '=', m)],
                limit=1
            )
            if not already_port:
                blank_port = self.port_ids.sudo().search(
                    [('source_id', '=', self.id), ('res_module', '=', False)], limit=1, order='port asc')
                # CASE Blank Port
                if blank_port:
                    blank_port.res_module = m
                    blank_port.frequency = 1
                    port = blank_port.port
                else:
                    # CASE Blank display_last_use For Add new port
                    oldest_port = self.port_ids.sudo().search([('source_id', '=', self.id)], order='write_date asc, port asc')
                    for xp in oldest_port:
                        last_use = xp.display_last_use
                        if last_use == False:
                            if xp:
                                xp.res_module = m
                                xp.frequency = 1
                                port = xp.port
                                _logger.info('### Module Old Active: '+ str(xp.res_module) +' ### Display_last_use: ' + str(last_use))
                    # CAES Nomal New Module Get Last Use
                    if port == -1:
                        today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
                        min = str(datetime.datetime.now().strftime("%Y-%m-%d"))
                        oldest_ports = self.port_ids.sudo().search([('source_id', '=', self.id)], order='write_date asc, port asc')
                        active_port = oldest_ports and oldest_ports[0] or False
                        for xp in oldest_ports:
                            todayx = datetime.datetime.strptime(
                                today, '%Y-%m-%d'
                            )
                            write_date = datetime.datetime.strptime(
                                str(xp.write_date)[:10], '%Y-%m-%d'
                            )
                            diff = todayx - write_date
                            last_use = xp.display_last_use
                            
                            if xp.display_status_code != "OK" and diff.days > 1:
                                min = last_use
                                active_port = xp
                                break
                                
                            if last_use < min and xp.display_status_code == "OK" and diff.days > 1:
                                min = last_use
                                active_port = xp
                        if active_port:
                            active_port.res_module = m
                            active_port.frequency = 1
                            port = active_port.port
                            _logger.info('### Module Active: '+ str(active_port.res_module) +' ### Display_last_use: ' + str(min))
                            
#                             if m != 'x':
#                                 url = active_port.source_id.url + 'app/nstdaweb_docker_monitor/standby?api_key={1}&api_secret={2}'
#                                 new_url = url.format(active_port.port, active_port.source_id.api_key, active_port.source_id.api_secret)
#                                 _logger.info("### Module Call Standy URL: " + new_url)
#                                 test_data = active_port.test_connect(new_url)
#                                 if test_data == True:
#                                     dataurl = urllib.urlopen(new_url)
#                                     code = dataurl.getcode()
#                                     if code == 200:
#                                         datareturn = dataurl.read()
#                                         _logger.info('### Module Call Standy Code: '+ str(code) +' ### Datareturn: ' + str(datareturn))
                                    
            else:
                # CASE Have Module
                already_port.frequency = already_port.frequency + 1
                port = already_port.port
        _logger.info('### forecast_port: ' + str(port))
        return port

    @api.one
    @api.depends('port_ids')
    @api.onchange('port_ids')
    def _compute_forecast_port(self):
        if self.port_ids:
            self.display_forecast_port = str(self.forecast_port(m='x'))

    @api.one
    @api.depends('port_ids')
    @api.onchange('port_ids')
    def _compute_time_diff(self):
        self.display_time_diff = 'Port is not fully.'
        if self.port_ids:
            empty = self.port_ids.sudo().search(
                [('res_module', '=', False)]
            )
            if not empty:
                min = str(datetime.datetime.now().strftime("%Y-%m-%d"))
                max = str('1900-01-01')
                for xp in self.port_ids:
                    last_use = xp.display_last_use
                    if last_use != '1900-01-01':
                        if last_use < min:
                            min = last_use
                        if last_use > max:
                            max = last_use
                
#                 oldest_port = self.port_ids.sudo().search(
#                     [('write_date', '!=', False)],
#                     limit=1,
#                     order='write_date asc'
#                 )
#                 already_port = self.port_ids.sudo().search(
#                     [('write_date', '!=', False)],
#                     limit=1,
#                     order='write_date desc'
#                 )
#                 oldest_write_date = datetime.datetime.strptime(
#                     oldest_port.write_date[:10], '%Y-%m-%d'
#                 )
#                 already_write_date = datetime.datetime.strptime(
#                     already_port.write_date[:10], '%Y-%m-%d'
#                 )

                oldest_write_date = datetime.datetime.strptime(
                    min, '%Y-%m-%d'
                )
                already_write_date = datetime.datetime.strptime(
                    max, '%Y-%m-%d'
                )
                diff = already_write_date - oldest_write_date
                self.display_time_diff = str(diff.days) + " Day. = Max[" + str(max) + "] - Min["+ str(min) + "]"

    def api_generator(self, size=16, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @api.model
    def create(self, vals):
        if not vals.get('api_key', False):
            vals['api_key'] = self.api_generator()
        vals['api_secret'] = self.api_generator(32)
        rec = super(nstdaweb_docker_monitor_source, self).create(vals)
        return rec

    @api.one
    @api.constrains('api_key')
    def _check_api_key(self):
        if self.api_key:
            api_ids = self.search([('api_key', '=', self.api_key)])
            if len(api_ids) > 1:
                error_msg = u"Duplicate API Key"
                raise ValidationError(error_msg)

    def set_standby(self):
        self.env.cr.execute("UPDATE res_users_login "
                       "SET login_dt = now() "
                       "AT TIME ZONE 'UTC' "
                       "WHERE user_id=%s", (1,))
        self.env.cr.commit()
        return str('1')


    def last_use_data(self):
#         user = self.env['res.users'].sudo().search([['login_date', '!=', False]], order="login_date desc", limit=1)
        self.env.cr.execute(""" SELECT
                                    login_dt
                                FROM
                                    res_users_login
                                WHERE
                                    login_dt IS NOT NULL
                                ORDER BY
                                    login_dt DESC
                                LIMIT 1 """)
        datas = self.env.cr.fetchone()
        login_date = datas and datas[0] or False
        res = "-1"
        if login_date:
            res = login_date
        return str(res)

    id = fields.Integer(string="id")
    name = fields.Char(string="Source Name", required=True)
    url = fields.Char(string="UTL", default="https://o-test-{0}.intra.nstda.or.th/")
    
    api_key = fields.Char(string="API Key")
    api_secret = fields.Char(string="API Secret", readonly=True)
    due_date = fields.Integer(string="Time difference Alert(Days)")
    admin_ids = fields.Many2many(
        'res.users',
        'nstdaweb_docker_monitor_port_user_rel',
        string='Admin',
        domain="[('active', '=', True)]",
    )
    port_min = fields.Char(string="Start Port", required=True)
    port_max = fields.Char(string="End Port", required=True)
    port_ids = fields.One2many(
        'nstdaweb.docker.monitor.port',
        'source_id',
        string="Ports"
    )
    display_forecast_port = fields.Char(
        string="Port Next(if new module)",
        compute='_compute_forecast_port'
    )
    display_time_diff = fields.Char(
        string="Time difference(Last login )",
        compute='_compute_time_diff'
    )


class nstdaweb_docker_monitor_port(models.Model):
    _name = 'nstdaweb.docker.monitor.port'
    _order = 'port asc'

    def test_connect(self, url, result=None):
        try:
            if not result:
                urllib2.urlopen(url, timeout=1)
                return True
            else:
                dataurl = urllib.urlopen(url)
                return dataurl
        except urllib2.HTTPError, e:
            if not result:
                return 'HTTPError = ' + str(e.code)
            else:
                return False
        except urllib2.URLError, e:
            if not result:
                return 'URLError = ' + str(e.reason)
            else:
                return False
        except httplib.HTTPException, e:
            if not result:
                return 'HTTPException'
            else:
                return False
        except Exception:
            if not result:
                return 'Exception'
            else:
                return False
    
    def validate_date(self, date_text):
        try:
            if isinstance(date_text, basestring):
                datetime.datetime.strptime(date_text, '%Y-%m-%d')
                return True
            else:
                return False
        except ValueError:
            return False

    @api.one
    @api.depends('source_id', 'res_module', 'port')
    @api.onchange('source_id', 'res_module', 'port')
    def _compute_status_code(self):
        self.display_status_code = '-'
        ir_config = self.env['ir.config_parameter']
        base_url = ir_config.get_param("web.base.url")
        if base_url:
            # Is Product Only
            if base_url.find('o.nstda.or.th') > -1 or base_url.find('127.0.0.1') > -1 or base_url.find('localhost') > -1 or base_url.find('o-test') > -1:
                if self.source_id and self.res_module and self.port:
                    url_test = self.source_id.url.format(self.port)
                    _logger.info(url_test)
                    test_data = self.test_connect(url_test)
                    if test_data == True:
                        code = urllib.urlopen(url_test).getcode()
                        self.display_status_code = httplib.responses[code]
                    else:
                        self.display_status_code = test_data
            else:
                self.display_status_code = 'For Pro. Only'

    @api.one
    @api.depends('source_id', 'res_module', 'port')
    def _compute_last_use(self):
        self.display_last_use = False
        ir_config = self.env['ir.config_parameter']
        base_url = ir_config.get_param("web.base.url")
        if base_url:
            # Is Product Only
            if base_url.find('o.nstda.or.th') > -1 or base_url.find('127.0.0.1') > -1 or base_url.find('localhost') > -1 or base_url.find('o-test') > -1:
                if self.source_id and self.res_module and self.port:
                    url = self.source_id.url + 'app/nstdaweb_docker_monitor/last_use?api_key={1}&api_secret={2}'
                    new_url = url.format(self.port, self.source_id.api_key, self.source_id.api_secret)
                    _logger.info(new_url)
                    test_data = self.test_connect(new_url, result=True)
                    if test_data:
                        dataurl = test_data
                        code = dataurl.getcode()
                        if code == 200:
                            datareturn = dataurl.read()
                            if self.validate_date(datareturn):
                                self.display_last_use = datareturn
                            else:
                                self.display_last_use = '1900-01-01'
                        else:
                            self.display_last_use = '1900-01-01'
                    else:
                        self.display_last_use = '1900-01-01'
            else:
                self.display_last_use = '1900-01-01'

    @api.one
    @api.depends('port')
    @api.onchange('port')
    def _compute_port(self):
        self.display_port = str(self.port)

    source_id = fields.Many2one(
        'nstdaweb.docker.monitor.source', string="Source")
    display_port = fields.Char(string="Port", compute='_compute_port')
    port = fields.Integer(string="Port", required=True)
    res_module = fields.Char(string="Module")
    frequency = fields.Integer(string="Frequency", default=0)
    display_status_code = fields.Char(
        string="Status",
        compute='_compute_status_code'
    )
    display_last_use = fields.Char(
        string="Last login",
        compute='_compute_last_use'
    )
    create_uid = fields.Many2one('res.users', string='Creator')
    create_date = fields.Datetime('Create Date')
    write_uid = fields.Many2one('res.users', string='Writer')
    write_date = fields.Datetime('Latest Call Port')
