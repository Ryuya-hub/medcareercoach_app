"""
データベーススキーマ確認スクリプト
"""
import psycopg2
from app.config import settings

def check_schema():
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor()

    print("=== Checking clients table ===")
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'clients'
        ORDER BY ordinal_position
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\n=== Checking coaches table ===")
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'coaches'
        ORDER BY ordinal_position
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\n=== Checking applications table ===")
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'applications'
        ORDER BY ordinal_position
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_schema()
