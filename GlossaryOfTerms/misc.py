import sys
import sqlite3
from cryptography.fernet import Fernet


# Function for working with the sqlite3 library
# After connecting to the database connection,
# it allows you to use the SQL LOWER function without bugs
def sqlite_lower(value_):
    return value_.lower()


# Function for working with the sqlite3 library
# After connecting to the database connection,
# it allows you to use the SQL UPPER function without bugs
def sqlite_upper(value_):
    return value_.upper()


# Function-constructor for working with the sqlite3 library
# After connecting to the database connection,
# it allows you to get decrypting function with specified key
def sqlite_decrypt_constructor(key: bytes):
    def sqlite_decrypt(value_):
        return Fernet(key).decrypt(value_.encode()).decode()

    return sqlite_decrypt


class SqliteConcatStrings:
    def __init__(self):
        self.result = []

    def step(self, value):
        self.result.append(value)

    def finalize(self):
        if not self.result:
            return ""
        return "; ".join(sorted(set(self.result)))


# Function for working with the sqlite3 library
# After connecting to the database connection,
# it allows you to compare data in case-insensitive SQL queries
def sqlite_ignore_case_collation(value1_, value2_):
    if value1_.lower() == value2_.lower():
        return 0
    elif value1_.lower() < value2_.lower():
        return -1
    else:
        return 1


# The standard Exception Hook allows you to output possible errors
# to the console when launching an application during development
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def execute_query(connection: sqlite3.Connection, query: str, functions: tuple = (), aggregates: tuple = ()):
    connection.create_function('LOWER', 1, sqlite_lower)
    connection.create_function('UPPER', 1, sqlite_upper)
    connection.create_collation('NOCASE', sqlite_ignore_case_collation)
    for func in functions:
        connection.create_function(*func)
    for aggregate in aggregates:
        connection.create_aggregate(*aggregate)
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor


def get_max_table_id(connection: sqlite3.Connection, name: str, key: bytes):
    cursor = execute_query(connection, f'SELECT MAX(DECRYPT(id)) FROM {name}',
                           (('DECRYPT', 1, sqlite_decrypt_constructor(key)),))
    result = cursor.fetchone()
    if result[0] is None:
        return 0
    else:
        return int(result[0])


def delete_items_of_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                delete_items_of_layout(item.layout())


# A function for encrypting data with encrypting key
def encrypt_data(data: bytes, key: bytes):
    return Fernet(key).encrypt(data)


def decrypt_data(data: bytes, key: bytes):
    return Fernet(key).decrypt(data)
