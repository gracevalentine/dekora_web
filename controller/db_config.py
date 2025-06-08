import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='dekora'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None