from flask import Flask
import os
from flask_mysqldb import MySQL
from flask_cors import CORS
from controllers.customers import customers_blueprint
from controllers.finances import finances_blueprint
from controllers.orders import orders_blueprint
from controllers.usernames import usernames_blueprint

app = Flask(__name__)
CORS(app)
# Configure MySQL

app.config['MYSQL_HOST'] = os.environ['DB_HOST']
app.config['MYSQL_USER'] = os.environ['DB_USERNAME']
app.config['MYSQL_PASSWORD'] = os.environ['DB_PASSWORD']
app.config['MYSQL_DB'] = os.environ['DB_NAME']

# Initialize MySQL
mysql = MySQL()
mysql.init_app(app)

# Register blueprints
app.register_blueprint(customers_blueprint)
app.register_blueprint(finances_blueprint)
app.register_blueprint(orders_blueprint)
app.register_blueprint(usernames_blueprint)

if __name__ == '__main__':
    app.run(port=5000)