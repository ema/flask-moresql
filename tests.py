
import flask
import unittest
import simplejson

from flask_moresql import MoreSQL

class DatabaseURI(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)

    def test_missing_connstring(self):
        self.assertRaises(RuntimeError, MoreSQL, self.app)

    def test_invalid_connstring(self):
        self.app.config['MORESQL_DATABASE_URI'] = 'bananas'
        self.assertRaises(RuntimeError, MoreSQL, self.app)

    def test_non_postgres_connstring(self):
        self.app.config['MORESQL_DATABASE_URI'] = 'mysql://username:password@hostname:3306/test'
        self.assertRaises(RuntimeError, MoreSQL, self.app)

class BasicApp(unittest.TestCase):
    
    def setUp(self):
        app = flask.Flask(__name__)
        app.config['MORESQL_DATABASE_URI'] = 'postgres://ema:test@localhost:5432/moresql'
        app.debug = True
    
        db = MoreSQL(app)

        self.app = app
        self.db = db

    def tearDown(self):
        pass

    def test_basic(self):
        c = self.app.test_client()

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
        def index():
            return self.db.execute('get_user', params=['username', 'password'])

        rv = c.post('/test', data={ 'username': 'test_user', 'password': 'test_password', })
        self.assertEquals(200, rv.status_code)
        self.assertEquals([ [ "test_user", ] ], simplejson.loads(rv.data))

if __name__ == "__main__":
    unittest.main()
