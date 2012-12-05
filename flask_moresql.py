# -*- coding: utf-8 -*-
"""     
    flask_moresql
    =============
    
    A thin layer of glue between PostgreSQL stored procedures and Flask web
    applications. 
       
    :copyright: (C) 2012 by Emanuele Rocca.
    :license: BSD, see LICENSE for more details.
"""

import re
import urllib
import psycopg2 
import simplejson

from functools import wraps

from flask import request, make_response

def _parse_rfc1738_args(name):
    if name is None:
        raise RuntimeError("MORESQL_DATABASE_URI needs to be specified")

    pattern = re.compile(r'''
        (?P<name>[\w\+]+)://
        (?:
        (?P<username>[^:/]*)
        (?::(?P<password>[^/]*))?
        @)?
        (?:
        (?P<host>[^/:]*)
        (?::(?P<port>[^/]*))?
        )?
        (?:/(?P<database>.*))?
        ''', re.X)

    m = pattern.match(name)
    if m is None:
        raise RuntimeError("Wrong DB URI string '%s'" % name)

    components = m.groupdict()

    if components['name'] != 'postgres':
        raise RuntimeError("MoreSQL only supports postgres databases")

    if components['password'] is not None:
        components['password'] = urllib.unquote_plus(components['password'])

    del components['name']
    return components

class MoreSQL(object):
    """Represents a PostgreSQL database."""
    
    def __init__(self, app):
        self.app = app

        creds = _parse_rfc1738_args(app.config.get('MORESQL_DATABASE_URI'))
        
        self.connection = psycopg2.connect(user=creds['username'], 
                                      password=creds['password'], 
                                      dbname=creds['database'], 
                                      host=creds['host'], 
                                      port=creds['port'])

        self.cursor = self.connection.cursor()

    def execute(self, procname, fields, values=None):
        """Execute the given stored procedure. Return results as a JSON
        HTTP response.
        
        :param procname: the stored procedure name
        :param fields: a list of dictionary fields used as parameters of the
                       stored procedure
        :param values: an optional dictionary of values from which the
                       parameters should be taken. If omitted, default to the 
                       values passed via HTTP
        """
        if values is None:
            values = request.values

        procargs = [ values.get(field) for field in fields ]

        self.cursor.callproc(procname, procargs)
        self.connection.commit()

        return make_response(simplejson.dumps(self.cursor.fetchall()))

if __name__ == "__main__":
    print _parse_rfc1738_args('postgres://ema:test@localhost:5432/silencebay')
