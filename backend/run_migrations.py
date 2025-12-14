import os
import psycopg2
from app.config import settings

def run_migration_file(cursor, filepath):
    """SQLマイグレーションファイルを実行"""
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
        cursor.execute(sql)
        print(f"[OK] Executed: {os.path.basename(filepath)}")

def main():
    """データベースマイグレーションを実行"""
    print("Starting database migrations...")

    # データベース接続
    conn = psycopg2.connect(settings.DATABASE_URL)
    conn.autocommit = False

    try:
        cursor = conn.cursor()

        # マイグレーションファイルのパス
        migration_files = [
            "../database/migrations/migration_add_application_fields.sql",
            "../database/migrations/migration_update_name_phone_fields.sql",
            "../database/migrations/migration_remove_coach_id_from_clients.sql",
            "../database/migrations/migration_add_super_admin_role.sql",
        ]

        # 各マイグレーションファイルを実行
        for migration_file in migration_files:
            filepath = os.path.join(os.path.dirname(__file__), migration_file)
            if os.path.exists(filepath):
                print(f"Running migration: {os.path.basename(filepath)}")
                run_migration_file(cursor, filepath)
            else:
                print(f"[WARN] Migration file not found: {filepath}")

        # コミット
        conn.commit()
        print("\n[SUCCESS] All migrations completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
