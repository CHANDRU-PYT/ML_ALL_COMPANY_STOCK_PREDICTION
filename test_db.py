import mysql.connector
import os

DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "Chandru@1234",
    "database": "stock_predictor",
}

def test_conn():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("[OK] Connection successful!")
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Tables: {tables}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[FAIL] {e}")

if __name__ == "__main__":
    test_conn()
