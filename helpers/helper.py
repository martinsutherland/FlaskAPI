import random
import string
from flask_mysqldb import MySQL

mysql = MySQL()
used_ids = set()
usernames = set()

def generate_customer_id():
    while True:
        # generate a 7-digit string with 3 random characters and 4 random digits
        customer_id = ''.join(random.choices(string.ascii_uppercase, k=3)) + ''.join(random.choices(string.digits, k=4))

        # check if the customer_id has already been used
        if customer_id in used_ids:
            continue

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM customer_details WHERE customer_id = %s', [customer_id])
        customer = cur.fetchone()
        cur.close()

        if customer is None:
            # customer_id is unique, add it to the set of used IDs and return it
            used_ids.add(customer_id)
            return customer_id


def generate_username(firstname, lastname):
    username = firstname.lower() + '.' + lastname.lower()
    index = 0
    while True:
        if index > 0:
            username = firstname.lower() + '.' + lastname.lower() + str(index).zfill(2)

        if username in usernames:
            index += 1
            continue

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM username_details WHERE username = %s', [username])
        user = cur.fetchone()
        cur.close()

        if user is None:
            used_ids.add(username)
            return username

        index += 1


