from config.db import get_connection

try:
    connection = get_connection()
    print("Oracle connection successful!")
    connection.close()
except Exception as e:
    print("Connection failed:")
    print(e)