import pandas as pd
from sqlalchemy import create_engine

# Configurations
server = 'P-TN-STGNG-DB01\MSSQL2022' 
database = 'RETAIL_CUSTOMERS'         
table_name = 'RETAIL_CUSTOMERS'        
excel_file_path = r"C:\Users\gkazeneza\Downloads\Book1.xlsx"


engine = create_engine(f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes")
df = pd.read_excel(excel_file_path)
df.to_sql(table_name, con=engine, if_exists='append', index=False)
print("Data uploaded successfully!")
