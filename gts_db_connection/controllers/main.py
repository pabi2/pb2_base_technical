# -*- coding: utf-8 -*-
# Geo Technosoft Pvt Ltd.

import openerp
from openerp.tools.translate import _
from openerp import tools
from openerp.http import request
from openerp import sql_db

import logging
_logger = logging.getLogger('DB Connection')
_Pool = None


def dsn(db_or_uri, conn=False):
    """ Function to prepare connection string"""
    _dsn = ''
    if conn:
        _dsn = 'host=%s port=%s user=%s password=%s' \
               % (str(conn.host).strip(), str(conn.port).strip(),
                  str(conn.user).strip(), str(conn.password).strip())
    else:
        for p in ('host', 'port', 'user', 'password'):
            cfg = tools.config['db_' + p]
            if cfg:
                _dsn += '%s=%s ' % (p, cfg)
    return db_or_uri, '%s dbname=%s' % (_dsn, db_or_uri)


def db_connect(to, allow_uri=False, conn=False):
    """ Function to connect with database"""
    global _Pool
    if _Pool is None:
        _Pool = sql_db.ConnectionPool(int(tools.config['db_maxconn']))

    db, uri = dsn(to, conn)
    return sql_db.Connection(_Pool, db, uri)


class DataSetInherit(openerp.addons.web.controllers.main.DataSet):
    def _call_kw(self, model, method, args, kwargs):
        if method.startswith('_'):
            raise Exception(
                "Access Denied: Underscore prefixed methods cannot be "
                "remotely called")

        model_obj = request.env['ir.model']
        model_rec = model_obj.sudo().search([('model', '=', model)], limit=1)
        if model_rec.sudo().connection_id:
            try:
                # creating a new connection
                new_cr = db_connect(
                    model_rec.connection_id.database, allow_uri=True,
                    conn=model_rec.connection_id).cursor()
                result = getattr(request.registry.get(model), method)(
                    new_cr, request.uid, *args, **kwargs)
                new_cr.close()
                _logger.info(
                    '++++++++ Connection to the database %s is successful'
                    % (model_rec.connection_id.database,))
                return result
            except Exception, e:
                _logger.exception(
                    'Exception in connection with other database: %s.', e.args)
                return getattr(request.registry.get(model), method)(
                    request.cr, request.uid, *args, **kwargs)
        return getattr(request.registry.get(model), method)(
            request.cr, request.uid, *args, **kwargs)

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
