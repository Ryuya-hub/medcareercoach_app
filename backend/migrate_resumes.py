"""
職務経歴書テーブルをフリーテキスト形式に変更するマイグレーションスクリプト
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def main():
    # データベース接続
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL not found in .env file")
        sys.exit(1)

    print(f"Connecting to database...")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("Starting migration...")

        # 1. 新しいcontentカラムを追加
        print("1. Adding content column...")
        try:
            conn.execute(text("ALTER TABLE resumes ADD COLUMN IF NOT EXISTS content TEXT"))
            conn.commit()
            print("   [OK] Content column added")
        except Exception as e:
            print(f"   - Content column already exists or error: {e}")
            conn.rollback()

        # 2. 既存データを移行
        print("2. Migrating existing data...")
        try:
            result = conn.execute(text("""
                UPDATE resumes
                SET content = COALESCE(
                  NULLIF(TRIM(CONCAT_WS(E'\n\n',
                    CASE WHEN self_pr IS NOT NULL THEN '【自己PR】' || E'\n' || self_pr END,
                    CASE WHEN motivation IS NOT NULL THEN '【志望動機】' || E'\n' || motivation END
                  )), ''),
                  ''
                )
                WHERE content IS NULL OR content = ''
            """))
            conn.commit()
            print(f"   [OK] Migrated {result.rowcount} rows")
        except Exception as e:
            print(f"   [ERROR] Error migrating data: {e}")
            conn.rollback()

        # 3. 古いカラムを削除
        print("3. Dropping old columns...")
        old_columns = ['full_name', 'birth_date', 'address', 'phone', 'email',
                       'desired_position', 'desired_salary', 'self_pr', 'motivation']

        for column in old_columns:
            try:
                conn.execute(text(f"ALTER TABLE resumes DROP COLUMN IF EXISTS {column}"))
                conn.commit()
                print(f"   [OK] Dropped column: {column}")
            except Exception as e:
                print(f"   - Column {column} already dropped or error: {e}")
                conn.rollback()

        # 4. 確認
        print("\n4. Verification:")
        result = conn.execute(text("""
            SELECT resume_id, client_id, version_number, status,
                   LEFT(content, 50) as content_preview,
                   created_at
            FROM resumes
            ORDER BY created_at DESC
            LIMIT 5
        """))

        rows = result.fetchall()
        if rows:
            print(f"   Found {len(rows)} resumes:")
            for row in rows:
                print(f"   - Version {row.version_number}: {row.content_preview}...")
        else:
            print("   No resumes found in database")

    print("\n[OK] Migration completed successfully!")

if __name__ == "__main__":
    main()
