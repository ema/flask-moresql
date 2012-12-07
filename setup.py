"""
Flask-MoreSQL
-------------
A thin layer of glue between PostgreSQL stored procedures and Flask web
applications.

Links
`````
* `documentation <http://packages.python.org/Flask-MoreSQL>`_
* `development version
  <http://github.com/ema/flask-moresql/zipball/master#egg=Flask-MoreSQL-dev>`_
"""

from setuptools import setup

setup(
    name='Flask-MoreSQL',
    version='0.1',
    url='http://github.com/ema/flask-moresql',
    license='BSD',
    author='Emanuele Rocca',
    author_email='ema@linux.it',
    description='Call PostgreSQL stored procedures from Flask',
    long_description=__doc__,
    py_modules=['flask_moresql', 'tests', 'example'],
    zip_safe=False,
    platforms='any',
    install_requires=[ 'Flask', 'psycopg2' ],
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
