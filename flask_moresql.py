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

from flask import request, make_response

def parse_rfc1738_args(name):
    """Parse the given database URI and return a dictionary of database
    connection values.

    Eg: parse_rfc1738_args('postgres://user:pass@host:5432/dbname')
        -> { 
            'username': 'user', 
            'password': 'pass', 
            'host': 'host',
            'port': '5432',
            'database': 'dbname'
           }
    """
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

    match = pattern.match(name)
    if match is None:
        raise RuntimeError("Wrong DB URI string '%s'" % name)

    components = match.groupdict()

    if components['name'] != 'postgres':
        raise RuntimeError("MoreSQL only supports postgres databases")

    if components['password'] is not None:
        components['password'] = urllib.unquote_plus(components['password'])

    del components['name']
    return components

def _convert_http_value(value):
    """Try to parse the given JSON value. Return raw value on failure."""
    try:
        return simplejson.loads(value)
    except simplejson.JSONDecodeError:
        return value

def _get_procedure_arguments(fields, values):
    """Return a list of parameters to be passed to the stored procedure."""
    if fields is None:
        # The stored procedure has been called without parameters
        return []

    if values:
        # Use user-supplied values
        return [ values.get(field) for field in fields ]

    # Use HTTP request values
    return [ _convert_http_value(request.values.get(field)) 
        for field in fields if request.values.get(field) is not None ]

class MoreSQL(object):
    """Used to connect to a given PostgreSQL database.

    To use MoreSQL you need to first create a Flask application, and then bind
    a MoreSQL instance to it::

        app = Flask(__name__)
        db = MoreSQL(app)
    """
    
    def __init__(self, app):
        self.app = app

        creds = parse_rfc1738_args(app.config.get('MORESQL_DATABASE_URI'))
        
        self.connection = psycopg2.connect(user=creds['username'], 
                                           password=creds['password'], 
                                           dbname=creds['database'], 
                                           host=creds['host'], 
                                           port=creds['port'])

        self.cursor = self.connection.cursor()

    def execute(self, procname, fields=None, values=None):
        """Execute the given stored procedure. Return results as a JSON
        HTTP response.
        
        :param procname: the stored procedure name
        :param fields: a list of dictionary fields used as parameters of the
                       stored procedure. The procedure will be called with no
                       arguments if omitted
        :param values: an optional dictionary of values from which the
                       parameters should be taken. If omitted, default to the 
                       values passed via HTTP
        """
        procargs = _get_procedure_arguments(fields, values)

        result = self.cursor.callproc(procname, procargs)

        self.connection.commit()

        if procargs == result:
            # The parameters have not been modified. There was no in/out
            # parameter, we have to fetch returned results from the cursor.
            result = self.cursor.fetchall()

        if len(result) == 1:
            if len(result[0]) == 1:
                result = result[0][0]
            else:
                result = result[0]

        return make_response(simplejson.dumps(result))
