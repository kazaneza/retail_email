# procedure_fetch.py

import pandas as pd
import pyodbc

def fetch_data_from_procedure(account_number, start_date, end_date):
    """
    Fetches data from the SQL Server stored procedure PS_account_statemet_bot.

    Parameters:
        account_number (str): The account number.
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
        tuple: A tuple containing:
            - dataframe (pd.DataFrame): The retrieved data.
            - account_number (str): The account number used.
            - start_date (str): The start date used.
            - end_date (str): The end date used.
    """
    conn_str = (
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=DATAWAREHOUSE02;'
        r'DATABASE=BK_REPORTING_DB;'
        r'Trusted_Connection=yes;'
    )
    
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC PS_account_statemet_bot ?, ?, ?", account_number, start_date, end_date)
            
            # Fetch column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            data = cursor.fetchall() if cursor.description else []

            # Iterate through result sets if the first one is empty
            while not columns and cursor.nextset():
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    data = cursor.fetchall()
                    break 

            if not columns:
                print("No data returned by the stored procedure.")
                return pd.DataFrame(), account_number, start_date, end_date  
            
            # Create DataFrame
            dataframe = pd.DataFrame.from_records(data, columns=columns)
            
            # Wrap 'Narration' text
            if 'Narration' in dataframe.columns:
                dataframe['Narration'] = dataframe['Narration'].astype(str).str.wrap(57)
            
            return dataframe, account_number, start_date, end_date
    except pyodbc.Error as e:
        print("Error while connecting to SQL Server:", e)
        return pd.DataFrame(), account_number, start_date, end_date
