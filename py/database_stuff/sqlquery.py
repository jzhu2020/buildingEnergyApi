
import sqlite3
from sqlite3 import Error


def establish_connection(file):
    try:
        conn = sqlite3.connect(file)
        return conn
    except Error as e:
        print(e)

    return None


def query(connection, command):
    cursor = connection.cursor()
    cursor.execute(command)
    return cursor.fetchall()