from flask import Blueprint, jsonify, Response, request
from flask_mysqldb import MySQL
import json
import os
from collections import OrderedDict

finances_blueprint = Blueprint('finances', __name__)

mysql = MySQL()

api_key = os.environ['API_KEY']

@finances_blueprint.route('/finances', methods=['GET'])
def get_finances():
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        try:
            with mysql.connection.cursor() as cur:
                cur.execute('SELECT * FROM finance_details')
                finances = cur.fetchall()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        if not finances:
            return jsonify({'error': 'No financial details found.'}), 404
        
        all_finances = [
            {
                'customer_id': finance[0],
                'sortCode': finance[1],
                "accountNumber": finance[2],
                'accountType': finance[3]
            } for finance in finances
        ]

        return jsonify(all_finances)
    else:
        return jsonify({'Message': 'Unauthorized'}), 401

# Get a finance by id
@finances_blueprint.route('/finances/<string:name>', methods=['GET'])
def get_finance(name):
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM finance_details WHERE customer_id = %s', [name])
        finance = cur.fetchone()
        cur.close()

        # If the finance is not found, raise a 404 error
        if not finance:
            return jsonify({'message': f"Financial details with customer_id {name} not found"}), 404

        # create an ordered dictionary with the desired order of keys
        formattedfinance = OrderedDict([
            ('customer_id', finance[0]),
            ('sortCode', finance[1]),
            ('accountNumber', finance[2]),
            ('accountType', finance[3])
        ])

        # If the finance is found, return it as JSON
        return jsonify(formattedfinance)
    else:
        return jsonify({'Message': 'Unauthorized'}), 401




# Create a new finance
@finances_blueprint.route('/finances', methods=['POST'])
def create_finance():
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        required_fields = set(['customer_id', 'sortCode', 'accountNumber', 'accountType'])
        if not required_fields.issubset(request.json.keys()):
            return Response({'Invalid Data'}, status=400)

        data = {field: request.json[field] for field in required_fields}
        cur = mysql.connection.cursor()

        # Check if finance details already exist for the given customer_id
        cur.execute('SELECT * FROM finance_details WHERE customer_id = %(customer_id)s',
                    {'customer_id': data['customer_id']})
        existing_finance = cur.fetchone()
        if existing_finance:
            cur.close()
            return jsonify({'message': f"Finance details already exist for customer with ID {data['customer_id']}"})

        # Check if customer exists
        cur.execute('SELECT * FROM customer_details WHERE customer_id = %(customer_id)s',
                    {'customer_id': data['customer_id']})
        customer = cur.fetchone()
        if not customer:
            cur.close()
            return jsonify({'message': f"Customer with ID {data['customer_id']} not found"})

        # Insert finance details
        cur.execute('INSERT INTO finance_details (customer_id, sortCode, accountNumber, accountType) VALUES (%(customer_id)s, %(sortCode)s, %(accountNumber)s, %(accountType)s)',
                    data)
        mysql.connection.commit()

        # Fetch inserted finance details and return response
        cur.execute('SELECT * FROM finance_details WHERE customer_id = %(customer_id)s',
                    {'customer_id': data['customer_id']})
        finance = cur.fetchone()
        cur.close()
        return jsonify({'message': 'Financial details created successfully',
                        "new_id": finance[0]
                        }), 201
    else:
        return jsonify({'Message': 'Unauthorized'}), 401


# Update an existing finance
@finances_blueprint.route('/finances/<string:id>', methods=['PUT'])
def update_finance(id):
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        required_fields = set(['sortCode', 'accountNumber', 'accountType'])
        if not required_fields.issubset(request.json.keys()):
            return jsonify({'Error': 'Invalid Data'}), 400

        data = {field: request.json[field] for field in required_fields}

        # Extract values from the request and add them to the dictionary
        for key in required_fields:
            data[key] = request.json[key]

        data['customer_id'] = id

        cur = mysql.connection.cursor()
        # Check if the provided ID exists in the database
        cur.execute('SELECT * FROM finance_details WHERE customer_id = %s', [id])
        finance = cur.fetchone()
        if not finance:
            return Response(json.dumps({'message': f"Financial details with ID {id} not found"}), status=404, mimetype='application/json')
        try:
            cur.execute(
                'UPDATE finance_details SET sortCode=%s, accountNumber=%s, accountType=%s WHERE customer_id=%s',
                (data['sortCode'], data['accountNumber'], data['accountType'], data['customer_id']))
            mysql.connection.commit()
        except mysql.connector.Error as error:
            return jsonify({'error': f'Error updating Financial Details: {error}'}), 500

        cur.close()

        return jsonify({'message': 'Finance updated successfully'}), 200
    else:
        return jsonify({'Message': 'Unauthorized'}), 401



# Delete a finance
@finances_blueprint.route('/finances/<string:id>', methods=['DELETE'])
def delete_finances(id):
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        cur = mysql.connection.cursor()

        # Check if the provided ID exists in the database
        cur.execute('SELECT * FROM finance_details WHERE customer_id = %s', [id])
        finance = cur.fetchone()
        if not finance:
            return Response(json.dumps({'message': f"Financial details with ID {id} not found"}), status=404, mimetype='application/json')
        try:
            cur.execute('DELETE FROM finance_details WHERE customer_id = %s', [id])
        except mysql.connector.Error as error:
            return jsonify({'error': f'Error deleting Financial details: {error}'}), 500
        
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Financial details deleted successfully'})
    else:
        return jsonify({'Message': 'Unauthorized'}), 401