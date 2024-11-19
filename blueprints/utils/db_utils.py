# blueprints/utils/db_utils.py

import pyodbc
from flask import current_app

def get_db_connection(config):
    """
    Establishes a connection to the SQL Server based on the provided configuration.

    :param config: Dictionary containing database connection details.
    :return: pyodbc.Connection object
    """
    auth_method = config.get('authentication_method', 'Windows')
    server = config.get('instance', 'localhost')
    database = config.get('database_name', 'sample_db')

    if auth_method == 'SQL':
        username = config.get('username', '')
        password = config.get('password', '')
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
        )
    elif auth_method == 'Windows':
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
        )
    else:
        raise ValueError("Unsupported authentication method.")

    try:
        connection = pyodbc.connect(connection_string)
        return connection
    except pyodbc.Error as e:
        current_app.logger.error(f"Database connection failed: {e}")
        return None
