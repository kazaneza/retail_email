# blueprints/utils/db_utils.py

import pyodbc

def get_db_connection(config):
    try:
        if config['authentication_method'] == 'SQL':
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config['instance']};"
                f"DATABASE={config['database_name']};"
                f"UID={config['username']};"
                f"PWD={config['password']}"
            )
        elif config['authentication_method'] == 'Windows':
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config['instance']};"
                f"DATABASE={config['database_name']};"
                f"Trusted_Connection=yes;"
            )
        else:
            return None

        connection = pyodbc.connect(conn_str)
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None
