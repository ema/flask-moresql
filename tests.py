
import flask
import unittest
import simplejson

from flask_moresql import MoreSQL, parse_rfc1738_args

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.config['TESTING'] = True

class DatabaseURI(BaseTest):

    def test_missing_connstring(self):
        self.assertRaises(RuntimeError, MoreSQL, self.app)

    def test_invalid_connstring(self):
        self.app.config['MORESQL_DATABASE_URI'] = 'bananas'
        self.assertRaises(RuntimeError, MoreSQL, self.app)

    def test_non_postgres_connstring(self):
        self.app.config['MORESQL_DATABASE_URI'] = \
            'mysql://username:password@hostname:3306/test'
        self.assertRaises(RuntimeError, MoreSQL, self.app)

    def test_postgres_connstring(self):
        expected = {  
            'username': 'user', 
            'password': 'pass', 
            'host': 'host',
            'port': '5432',
            'database': 'dbname'
        }

        db_params = parse_rfc1738_args('postgres://user:pass@host:5432/dbname')
        self.assertEquals(expected, db_params)

class BasicApp(BaseTest):
    
    def setUp(self):
        BaseTest.setUp(self)

        self.app.config['MORESQL_DATABASE_URI'] = \
            'postgres://ema:test@localhost:5432/moresql'
        self.db = MoreSQL(self.app)
        self.client = self.app.test_client()

    def __test_return_basic_type(self, sqltype, expected):
        if type(expected) is str:
            return_expected = "'%s'" % expected
        else:
            return_expected = expected

        self.db.cursor.execute("""
            CREATE OR REPLACE FUNCTION get_%s() RETURNS %s AS $$ 
            BEGIN 
                RETURN %s;
            END;
            $$ LANGUAGE plpgsql;
        """ % (sqltype, sqltype, return_expected))

        @self.app.route('/test')
        def test():
            return self.db.execute('get_%s' % sqltype)

        rv = self.client.get('/test')
        self.assertEquals(200, rv.status_code)
        self.assertEquals(expected, simplejson.loads(rv.data))

    def test_return_string(self):
        self.__test_return_basic_type('text', 'hello world')

    def test_return_int(self):
        self.__test_return_basic_type('integer', 42)

    def test_return_float(self):
        self.__test_return_basic_type('real', 3.14)

    def test_return_bool(self):
        self.__test_return_basic_type('boolean', True)

    def test_in_return(self):
        self.db.cursor.execute("""
            CREATE OR REPLACE FUNCTION sum_n(x int, y int)
            RETURNS integer AS $$
            BEGIN
                RETURN x + y;
            END;
            $$ LANGUAGE plpgsql;
            """)

        @self.app.route('/test', methods=['GET'])
        def test():
            return self.db.execute('sum_n', 
                fields=[ 'x', 'y', ])

        rv = self.client.get('/test?x=10&y=32')
        self.assertEquals(200, rv.status_code)
        self.assertEquals(42, simplejson.loads(rv.data))
        
    def test_in_out(self):
        self.db.cursor.execute("""
            CREATE OR REPLACE FUNCTION sum_n_product(x int, y int,  
                OUT sum int, OUT prod int) AS $$
            BEGIN
                sum := x + y;
                prod := x * y;
            END;
            $$ LANGUAGE plpgsql;
            """)

        @self.app.route('/test', methods=['GET'])
        def test():
            return self.db.execute('sum_n_product', 
                fields=[ 'x', 'y', 'sum', 'prod' ])

        rv = self.client.get('/test?x=10&y=32')
        self.assertEquals(200, rv.status_code)
        self.assertEquals({ 'sum': 42, 'prod': 320 }, simplejson.loads(rv.data))

        @self.app.route('/test_omit_out', methods=['GET'])
        def sum2():
            return self.db.execute('sum_n_product', 
                fields=[ 'x', 'y', ])

        rv = self.client.get('/test_omit_out?x=10&y=32')
        self.assertEquals(200, rv.status_code)
        self.assertEquals({ 'sum': 42, 'prod': 320 }, simplejson.loads(rv.data))

    def test_return_table(self):
        self.db.cursor.execute("""
            CREATE TEMPORARY TABLE films(
                code        char(5) CONSTRAINT firstkey PRIMARY KEY,
                title       varchar(40) NOT NULL,
                did         integer NOT NULL,
                date_prod   date,
                kind        varchar(10),
                len         interval hour to minute
            );

            CREATE OR REPLACE FUNCTION get_films(wanted_title text) 
            RETURNS TABLE (c char, d integer) AS $$
            BEGIN
                RETURN QUERY SELECT code, did FROM films 
                    WHERE title=wanted_title;
            END
            $$ LANGUAGE plpgsql;
            """)

        @self.app.route('/test', methods=['GET'])
        def test():
            return self.db.execute('get_films', fields=[ 'title', ])

        # empty list
        rv = self.client.get('/test?title=ciao')
        self.assertEquals(200, rv.status_code)
        self.assertEquals([], simplejson.loads(rv.data))

        # one row
        self.db.cursor.execute("""INSERT INTO films (code, title, did)
            VALUES (%s, %s, %s)""", ('tt011', 'The Shawshank Redemption', 42))

        rv = self.client.get('/test?title=The Shawshank Redemption')
        self.assertEquals(200, rv.status_code)
        self.assertEquals({ 'c': 'tt011', 'd': 42 }, simplejson.loads(rv.data))

        self.db.cursor.execute("""INSERT INTO films (code, title, did)
            VALUES (%s, %s, %s)""", ('tt012', 'The Shawshank Redemption', 43))

        # multiple rows
        rv = self.client.get('/test?title=The Shawshank Redemption')
        self.assertEquals(200, rv.status_code)
        expected = [ { 'c': 'tt011', 'd': 42 }, { 'c': 'tt012', 'd': 43 } ]
        self.assertEquals(expected, simplejson.loads(rv.data))

if __name__ == "__main__":
    unittest.main()
