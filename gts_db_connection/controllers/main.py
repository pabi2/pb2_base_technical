# -*- coding: utf-8 -*-
# Geo Technosoft Pvt Ltd.

import werkzeug.utils
import werkzeug.wrappers

import openerp
import openerp.modules.registry
from openerp.tools.translate import _
from openerp import http, tools

from openerp.http import request, serialize_exception as _serialize_exception
from openerp import sql_db

import logging
_logger = logging.getLogger(__name__)
_Pool = None


def dsn(db_or_uri, host):
    """parse the given `db_or_uri` and return a 2-tuple (dbname, uri)"""
    if db_or_uri.startswith(('postgresql://', 'postgres://')):
        # extract db from uri
        us = urlparse.urlsplit(db_or_uri)
        if len(us.path) > 1:
            db_name = us.path[1:]
        elif us.username:
            db_name = us.username
        else:
            db_name = us.hostname
        return db_name, db_or_uri
    _dsn = ''
    if host:
        for p in ('host', 'port', 'user', 'password'):
            if p == 'host':
                _dsn += '%s=%s ' % (p, host)
            else:
                cfg = tools.config['db_' + p]
                if cfg:
                    _dsn += '%s=%s ' % (p, cfg)
    else:
        for p in ('host', 'port', 'user', 'password'):
            cfg = tools.config['db_' + p]
            if cfg:
                _dsn += '%s=%s ' % (p, cfg)
    return db_or_uri, '%sdbname=%s' % (_dsn, db_or_uri)

def db_connect(to, allow_uri=False, host=False):
    global _Pool
    if _Pool is None:
        _Pool = sql_db.ConnectionPool(int(tools.config['db_maxconn']))

    db, uri = dsn(to, host)
    if not allow_uri and db != to:
        raise ValueError('URI connections not allowed')
    return sql_db.Connection(_Pool, db, uri)


class DataSetInherit(openerp.addons.web.controllers.main.DataSet):

    def _call_kw(self, model, method, args, kwargs):
        if method.startswith('_'):
            raise Exception("Access Denied: Underscore prefixed methods cannot be remotely called")

        model_obj = request.env['ir.model']
        model_rec = model_obj.sudo().search([('model', '=', model)], limit=1)
        if model_rec.sudo().connection_id:
            try:
                # creating a new connection
                new_cr = db_connect(
                    model_rec.connection_id.database, allow_uri=True,
                    host=model_rec.connection_id.host).cursor()
                result = getattr(request.registry.get(model), method)(
                    new_cr, request.uid, *args, **kwargs)
                new_cr.close()
                return result
            except Exception, e:
                _logger.warning('Exception in connection with other database: %s.', e.args)
                return getattr(request.registry.get(model), method)(
                    request.cr, request.uid, *args, **kwargs)
        return getattr(request.registry.get(model), method)(
            request.cr, request.uid, *args, **kwargs)

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
