# db_mysql.py
import mysql.connector
from mysql.connector import Error

def create_connection():
    """ create a database connection to a MySQL database """
    conn = None
    try:
        # Note: The user will need to configure their own database details.
        conn = mysql.connector.connect(host='localhost',
                                       database='library',
                                       user='user',
                                       password='password',
                                       connection_timeout=5)
        if conn.is_connected():
            print('Connected to MySQL database')

    except Error as e:
        print(f"MySQL Error: {e}")
        # Return None if connection fails
        return None

    return conn
