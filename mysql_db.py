import mysql.connector
from mysql.connector import pooling
import config

# Tạo connection pool
dbconfig = {
    "host": config.MYSQL_HOST,
    "user": config.MYSQL_USER,
    "password": config.MYSQL_PASSWORD,
    "database": config.MYSQL_DB
}

connection_pool = pooling.MySQLConnectionPool(pool_name="mypool",
                                              pool_size=5,
                                              **dbconfig)

def get_connection():
    return connection_pool.get_connection()

def query_db(query, params=(), one=False):
    """ Truy vấn dữ liệu (SELECT) """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return (result[0] if result else None) if one else result

def insert_db(query, params=()):
    """ Thực thi INSERT, UPDATE, DELETE """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()
