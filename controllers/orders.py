from flask import Blueprint, jsonify, Response, request
from flask_mysqldb import MySQL
import json
import os
from collections import OrderedDict

orders_blueprint = Blueprint('orders', __name__)

mysql = MySQL()

api_key = os.environ['API_KEY']

@orders_blueprint.route('/orders', methods=['GET'])
def get_all_orders():
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        try:
            with mysql.connection.cursor() as cur:
                cur.execute('SELECT * FROM orders')
                orders = cur.fetchall()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        if not orders:
            return jsonify({'error': 'No orders found.'}), 404
        
        all_orders = [
            {
                "order_id": order[0],
                'customer_id': order[1],
                'item': order[2],
                "price": order[3]
            } for order in orders
        ]

        return jsonify(all_orders)
    else:
        return jsonify({'Message': 'Unauthorized'}), 401

# Get a order by id
@orders_blueprint.route('/orders/<string:name>', methods=['GET'])
def get_orders_by_customer(name):
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        try:
            with mysql.connection.cursor() as cur:
                cur.execute('SELECT * FROM orders WHERE customer_id = %s', [name])
                orders = cur.fetchall()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        if not orders:
            return jsonify({'error': 'No orders found.'}), 404
        
        all_orders = [
            {
                "order_id": order[0],
                'customer_id': order[1],
                'item': order[2],
                "price": order[3]
            } for order in orders
        ]

        return jsonify(all_orders)
    else:
        return jsonify({'Message': 'Unauthorized'}), 401
    
# Get a order by id
@orders_blueprint.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM orders WHERE order_id = %s', [id])
        order = cur.fetchone()
        cur.close()
        print(order)
        # If the order is not found, raise a 404 error
        if not order:
            return jsonify({'message': f"No orders with id {id} found"}), 404

        # create an ordered dictionary with the desired order of keys
        formattedorder = {
            'order_id': order[0],
            'customer_id': order[1],
            'item': order[2],
            'price': order[3]
        }

        # If the order is found, return it as JSON
        return jsonify(formattedorder), 200
    else:
        return jsonify({'Message': 'Unauthorized'}), 401




# Create a new order
@orders_blueprint.route('/orders', methods=['POST'])
def create_order():
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        required_fields = set(['customer_id', 'item', 'price'])
        if not required_fields.issubset(request.json.keys()):
            return Response({'Invalid Data'}, status=400)

        data = {field: request.json[field] for field in required_fields}
        cur = mysql.connection.cursor()

        # Check if customer exists
        cur.execute('SELECT * FROM customer_details WHERE customer_id = %(customer_id)s',
                    {'customer_id': data['customer_id']})
        customer = cur.fetchone()
        if not customer:
            cur.close()
            return jsonify({'message': f"Customer with ID {data['customer_id']} not found"}), 404

        # Insert order details and get the ID of the newly inserted row
        cur.execute('INSERT INTO orders (customer_id, item, price) VALUES (%(customer_id)s, %(item)s, %(price)s)',
                    data)
        new_id = cur.lastrowid
        mysql.connection.commit()

        cur.close()

        return jsonify({'message': 'Order created successfully', "new_id": str(new_id)}), 201
    else:
        return jsonify({'Message': 'Unauthorized'}), 401



# Update an existing order
@orders_blueprint.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        required_fields = set(['customer_id', 'item', 'price'])
        if not required_fields.issubset(request.json.keys()):
            return jsonify({'Error': 'Invalid Data'}), 400

        data = {field: request.json[field] for field in required_fields}

        # Extract values from the request and add them to the dictionary
        for key in required_fields:
            data[key] = request.json[key]

        data['order_id'] = id

        cur = mysql.connection.cursor()
        # Check if the provided ID exists in the database
        cur.execute('SELECT * FROM orders WHERE order_id = %s', [id])
        order = cur.fetchone()
        if not order:
            return Response(json.dumps({'message': f"Order with ID {id} not found"}), status=404, mimetype='application/json')
        try:
            cur.execute(
                'UPDATE orders SET item=%s, price=%s WHERE order_id=%s',
                (data['item'], data['price'], data['order_id']))
            mysql.connection.commit()
        except mysql.connector.Error as error:
            return jsonify({'error': f'Error updating order Details: {error}'}), 500

        cur.close()

        return jsonify({'message': 'Order updated successfully'}), 200
    else:
        return jsonify({'Message': 'Unauthorized'}), 401



# Delete a order
@orders_blueprint.route('/orders/<int:id>', methods=['DELETE'])
def delete_orders(id):
    submiited_key = request.headers.get('Authorization')
   
    if submiited_key == api_key:
        cur = mysql.connection.cursor()

        # Check if the provided ID exists in the database
        cur.execute('SELECT * FROM orders WHERE order_id = %s', [id])
        order = cur.fetchone()
        if not order:
            return Response(json.dumps({'message': f"Order details with ID {id} not found"}), status=404, mimetype='application/json')
        try:
            cur.execute('DELETE FROM orders WHERE order_id = %s', [id])
        except mysql.connector.Error as error:
            return jsonify({'error': f'Error deleting order: {error}'}), 500
        
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Order deleted successfully'})
    else:
        return jsonify({'Message': 'Unauthorized'}), 401