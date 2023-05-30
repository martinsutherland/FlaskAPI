from flask import Blueprint, jsonify, Response, request, make_response
from flask_mysqldb import MySQL
import json
import os
from helpers.helper import generate_customer_id
from collections import OrderedDict

customers_blueprint = Blueprint('customers', __name__)

mysql = MySQL()

api_key = os.environ['API_KEY']

@customers_blueprint.route('/customers/', methods=['OPTIONS'])
def handle_options():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET', 'PUT', 'DELETE')
    return response

@customers_blueprint.route('/customers', methods=['GET'])
def get_customers():
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        try:
            with mysql.connection.cursor() as cur:
                cur.execute('SELECT * FROM customer_details')
                customers = cur.fetchall()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        if not customers:
            return jsonify({'error': 'No customers found.'}), 404
        
        all_customers = [
            {
                'customer_id': customer[0],
                'firstName': customer[1],
                "lastName": customer[2],
                'address': customer[3],
                'email': customer[4]
            } for customer in customers
        ]

        return jsonify(all_customers)
    else:
        return jsonify({'Message': 'Unauthorized'}), 401

# Get a customer by id
@customers_blueprint.route('/customers/<string:name>', methods=['GET'])
def get_customer(name):
    submiited_key = request.headers.get('Authorization')
    if submiited_key == api_key:
        try:
            with mysql.connection.cursor() as cur:
                cur.execute('SELECT * FROM customer_details WHERE customer_id = %s', [name])
                customer = cur.fetchone()
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        cur.close()

        # If the customer is not found, raise a 404 error
        if not customer:
            return jsonify({'message': f"Customer with name {name} not found"}), 404

        # create an ordered dictionary with the desired order of keys
        formattedCustomer = OrderedDict([
            ('customer_id', customer[0]),
            ('firstName', customer[1]),
            ('lastName', customer[2]),
            ('address', customer[3]),
            ('email', customer[4])
        ])

        # If the customer is found, return it as JSON
        return jsonify(formattedCustomer)
    else:
        return jsonify({'Message': 'Unauthorized'}), 401



# Create a new customer
@customers_blueprint.route('/customers', methods=['POST'])
def create_customer():
    submiited_key = request.headers.get('Authorization')
    if submiited_key == api_key:
        required_fields = set(['firstName', 'lastName', 'address', 'email'])
        if not required_fields.issubset(request.json.keys()):
            return Response({'Invalid Data'}, status=400)

        customer_id = generate_customer_id()
        
        data = {field: request.json[field] for field in required_fields}
        cur = mysql.connection.cursor()
        
        data['customer_id'] = customer_id

        cur.execute('INSERT INTO customer_details (customer_id, firstName, lastName, address, email) VALUES (%(customer_id)s, %(firstName)s, %(lastName)s, %(address)s, %(email)s)',
            data)
        mysql.connection.commit()
        cur.execute('SELECT * FROM customer_details WHERE customer_id = %(customer_id)s',
                    {'customer_id': data['customer_id']})
        customer = cur.fetchone()
        cur.close()
        return jsonify({'message': 'Customer created successfully',
                        "new_id": customer[0]
                        }), 201
    else:
        return jsonify({'Message': 'Unauthorized'}), 401

# Update an existing customer
@customers_blueprint.route('/customers/<string:id>', methods=['PUT'])
def update_customer(id):
    submiited_key = request.headers.get('Authorization')
    if submiited_key == api_key:
        required_fields = set(['firstName', 'lastName', 'address', 'email'])
        if not required_fields.issubset(request.json.keys()):
            return jsonify({'Error': 'Invalid Data'}), 400

        data = {field: request.json[field] for field in required_fields}

        # Extract values from the request and add them to the dictionary
        for key in required_fields:
            data[key] = request.json[key]

        data['customer_id'] = id

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM customer_details WHERE customer_id = %s', [id])
        customer = cur.fetchone()
        
        # If the customer is not found, raise a 404 error
        if not customer:
            return jsonify({'message': f"Customer with name {id} not found"}), 404
        
        try:
            cur.execute(
                'UPDATE customer_details SET firstName=%s, lastName=%s, address=%s, email=%s  WHERE customer_id=%s',
                (data['firstName'], data['lastName'], data['address'], data['email'], data['customer_id']))
            mysql.connection.commit()
        except mysql.connector.Error as error:
            return jsonify({'error': f'Error creating customer: {error}'}), 500

        cur.close()

        return jsonify({'message': 'Customer updated successfully'}), 200
    else:
        return jsonify({'Message': 'Unauthorized'}), 401




# Delete a customer
@customers_blueprint.route('/customers/<string:id>', methods=['DELETE'])
def delete_customers(id):
    submiited_key = request.headers.get('Authorization')
    if submiited_key == api_key:
        cur = mysql.connection.cursor()

        # Check if the provided ID exists in the database
        cur.execute('SELECT * FROM customer_details WHERE customer_id = %s', [id])
        customer = cur.fetchone()
        if not customer:
            return Response(json.dumps({'message': f"customer with ID {id} not found"}), status=404, mimetype='application/json')
        try:
            cur.execute('DELETE FROM customer_details WHERE customer_id = %s', [id])
        except mysql.connector.Error as error:
            return jsonify({'error': f'Error deleting customer: {error}'}), 500
        
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Customer deleted successfully'}), 200
    else:
        return jsonify({'Message': 'Unauthorized'}), 401