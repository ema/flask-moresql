
import flask
import unittest
import simplejson

from flask_moresql import MoreSQL

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

class BasicApp(BaseTest):
    
    def setUp(self):
        BaseTest.setUp(self)

        self.app.config['MORESQL_DATABASE_URI'] = \
            'postgres://ema:test@localhost:5432/moresql'
        self.db = MoreSQL(self.app)
        self.client = self.app.test_client()

    def test_return_string(self):
        self.db.cursor.execute("""
CREATE OR REPLACE FUNCTION get_user(uname text, pwd text) 
RETURNS text AS $$ 
DECLARE result text;
BEGIN 
    SELECT uname INTO result; 
    RETURN result;  
END;
$$ LANGUAGE plpgsql;
""")

        @self.app.route('/test', methods=['POST'])
        def test():
            return self.db.execute('get_user', fields=['username', 'password'])

        rv = self.client.post('/test', data={ 'username': 'test_user', 
                                    'password': 'test_password', })
        self.assertEquals(200, rv.status_code)
        self.assertEquals("test_user", simplejson.loads(rv.data))

    def test_return_int(self):
        pass

    def test_inout(self):
        self.db.cursor.execute("""
CREATE OR REPLACE FUNCTION sum_n_product(x int, y int, OUT sum int, OUT prod int) 
AS $$
BEGIN
    sum := x + y;
    prod := x * y;
END;
$$ LANGUAGE plpgsql;
""")

        @self.app.route('/test', methods=['GET'])
        def sum1():
            return self.db.execute('sum_n_product', 
                fields=[ 'x', 'y', 'sum', 'prod' ])

        rv = self.client.get('/test?x=10&y=32')
        self.assertEquals(200, rv.status_code)
        self.assertEquals([ 42, 320 ], simplejson.loads(rv.data))

        @self.app.route('/test_omit_out', methods=['GET'])
        def sum2():
            return self.db.execute('sum_n_product', 
                fields=[ 'x', 'y', ])

        rv = self.client.get('/test_omit_out?x=10&y=32')
        self.assertEquals(200, rv.status_code)
        self.assertEquals([ 42, 320 ], simplejson.loads(rv.data))

if __name__ == "__main__":
    unittest.main()
