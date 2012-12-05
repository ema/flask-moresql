Flask-MoreSQL
=============

.. module:: flask_moresql

Flask-MoreSQL is an extension to `Flask`_ that allows you to easily build
RESTful APIs on top of your `PostgreSQL`_ applications. It is a thin layer of
glue between PostgreSQL stored procedures and Flask web applications.

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

To start using your PostgreSQL database, create a :class:`Flask` application
and connect it to a :class:`MoreSQL` object::

    from flask import Flask
    from flask_moresql import MoreSQL

    app = Flask(__name__)
    app.config['MORESQL_DATABASE_URI'] = 'postgres://user:pass@host:5432/dbname'
    db = MoreSQL(app)

Make sure to specify your database credentials in `MORESQL_DATABASE_URI`.

You can then map routes to specific stored procedures as follows::

    @app.route('/user', methods=['GET'])
    def get_user_data():
        return db.execute('get_user', fields=['username', 'password'])

The return value of your stored procedure will be returned as JSON to the user.

API Reference
-------------

.. autoclass:: MoreSQL
   :members:

