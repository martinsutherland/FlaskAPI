from flask import Blueprint, jsonify, Response, request, make_response
from flask_mysqldb import MySQL
import json
import os
from helpers.helper import generate_username
from collections import OrderedDict

usernames_blueprint = Blueprint('usernames', __name__)

mysql = MySQL()

api_key = os.environ['API_KEY']

@usernames_blueprint.route('/usernames/', methods=['OPTIONS'])
def handle_options():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET', 'PUT', 'DELETE')
    return response

@usernames_blueprint.route('/usernames', methods=['GET'])
def get_usernames():
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        try:
            with mysql.connection.cursor() as cur:
                cur.execute('SELECT * FROM username_details')
                usernames = cur.fetchall()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        if not usernames:
            return jsonify({'error': 'No usernames found.'}), 404
        
        all_usernames = [
            {
                'id': username[0],
                'username': username[1],
            } for username in usernames
        ]

        return jsonify(all_usernames)
    else:
        return jsonify({'Message': 'Unauthorized'}), 401

# Get a username by id
@usernames_blueprint.route('/usernames/<int:id>', methods=['GET'])
def get_username(id):
    submiited_key = request.headers.get('Authorization')
    if submiited_key == api_key:
        try:
            with mysql.connection.cursor() as cur:
                cur.execute('SELECT * FROM username_details WHERE id = %s', [id])
                username = cur.fetchone()
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        cur.close()

        # If the username is not found, raise a 404 error
        if not username:
            return jsonify({'message': f"username with {id} not found"}), 404

        # create an ordered dictionary with the desired order of keys
        formattedusername = OrderedDict([
            ('id', username[0]),
            ('username', username[1])
        ])

        # If the username is found, return it as JSON
        return jsonify(formattedusername)
    else:
        return jsonify({'Message': 'Unauthorized'}), 401



# Create a new username
@usernames_blueprint.route('/usernames', methods=['POST'])
def create_username():
    submitted_key = request.headers.get('Authorization')
    if submitted_key == api_key:
        required_fields = set(['firstName', 'lastName'])
        if not required_fields.issubset(request.json.keys()):
            return Response('Invalid Data', status=400)

        data = {field: request.json[field] for field in required_fields}
        cur = mysql.connection.cursor()

        firstName = data['firstName']
        lastName = data['lastName']
        
        username = generate_username(firstName, lastName)

        cur.execute('INSERT INTO username_details (username) VALUES (%(username)s)', 
                    {'username': username})
        mysql.connection.commit()

        cur.execute('SELECT * FROM username_details WHERE username = %(username)s', 
                    {'username': username})
        result = cur.fetchone()
        cur.close()

        return jsonify({'new_id': result[0],'username': result[1]}), 201
    else:
        return jsonify({'message': 'Unauthorized'}), 401


# Delete a username
@usernames_blueprint.route('/usernames/<int:id>', methods=['DELETE'])
def delete_usernames(id):
    submiited_key = request.headers.get('Authorization')
    if submiited_key == api_key:
        cur = mysql.connection.cursor()

        # Check if the provided ID exists in the database
        cur.execute('SELECT * FROM username_details WHERE id = %s', [id])
        username = cur.fetchone()
        if not username:
            return Response(json.dumps({'message': f"username with ID {id} not found"}), status=404, mimetype='application/json')
        try:
            cur.execute('DELETE FROM username_details WHERE id = %s', [id])
        except mysql.connector.Error as error:
            return jsonify({'error': f'Error deleting username: {error}'}), 500
        
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Username deleted successfully'}), 200
    else:
        return jsonify({'Message': 'Unauthorized'}), 401