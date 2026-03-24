import pyodbc

def get_connection():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost;"
        "Database=QuanLySinhVien;"
        "Trusted_Connection=yes;"
    )