Flask-MoreSQL
=============

.. module:: flask_moresql

Flask-MoreSQL is an extension to `Flask`_, a microframework for Python, that
allows developers to easily build RESTful APIs on top of `PostgreSQL`_
databases. 

In other words, it is a thin layer of glue between Python web applications and
PostgreSQL stored procedures.

Flask-MoreSQL depends on the `psycopg2`_ module.

Installation
------------

Install the extension with one of the following commands::

    $ pip install Flask-MoreSQL

Alternatively, use `easy_install`::

    $ easy_install Flask-MoreSQL

.. _Relational Model: http://en.wikipedia.org/wiki/Relational_model
.. _Flask: http://flask.pocoo.org/
.. _PostgreSQL: http://postgresql.org/
.. _psycopg2: http://pypi.python.org/pypi/psycopg2

Usage
-----

To use Flask-MoreSQL, create a :class:`Flask` application and connect it to a
:class:`MoreSQL` object::

    from flask import Flask
    from flask.ext.moresql import MoreSQL

    app = Flask(__name__)
    app.config['MORESQL_DATABASE_URI'] = 'postgres://user:pass@host:5432/dbname'
    db = MoreSQL(app)

Make sure to specify your database credentials in `MORESQL_DATABASE_URI`.

You can then map routes to specific stored procedures as follows::

    @app.route('/user', methods=['GET'])
    def get_user_data():
        return db.execute('get_user', fields=['username', 'password'])

The example above maps GET requests to `/user` to the `get_user` stored
procedure. Other than the stored procedure name, the :meth:`execute` method
takes a list as a parameter to specify which of the HTTP request values have to
be used in the stored procedure call, `username` and `password` in our example.

If request values have to be modified before calling the stored procedure, they
can be passed to :meth:`execute` via the optional keyword argument `values`::

    @app.route('/user', methods=['GET'])
    def get_user_data():
        modified_values = {
            'username': request.values.get('username').lower(),
            'password': request.values.get('password')
        }
        return db.execute('get_user', 
                          fields=['username', 'password'], 
                          values=modified_values)

Finally, the value returned by the stored procedure is returned as JSON to the
client.

API Reference
-------------

.. autoclass:: MoreSQL
   :members:

