
from flask import Flask
from flask_moresql import MoreSQL

app = Flask(__name__)
app.config['MORESQL_DATABASE_URI'] = 'postgres://ema:test@localhost:5432/moresql'
db = MoreSQL(app)

@app.route('/', methods=['GET'])
def index():
    return db.execute('get_user', params=['username', 'password'])

if __name__ == "__main__":
    app.run()
    
