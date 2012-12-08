# -*- coding: utf-8 -*-

"""A sample application using Flask-MoreSQL"""

from flask import Flask, request
from flask_moresql import MoreSQL

app = Flask(__name__)
app.config['MORESQL_DATABASE_URI'] = 'postgres://user:pass@host:5432/dbname'
db = MoreSQL(app)

@app.route('/dogs', methods=['GET'])
def dogs():
    # Call the 'get_dogs' function with no parameters. 
    # Return all rows as JSON.
    return db.execute('get_dogs')

@app.route('/dogs/<int:dog_id>', methods=['GET', 'POST',])
def dog(dog_id):
    # Call update_dog(dog_id, name, color) if this is a POST request.
    # Use the HTTP values posted for dog_id, name, and color.
    if request.method == 'POST':
        return db.execute('update_dog', fields=[ 'dog_id', 'name', 'color' ])

    # In case of GET requests, call get_dog(dog_id). Here dog_id is explicitly
    # passed to the stored procedure using the 'values' keyword argument.
    return db.execute(
        'get_dog', fields=[ 'dog_id' ], values={ 'dog_id': dog_id })

if __name__ == "__main__":
    app.run(debug=True)
