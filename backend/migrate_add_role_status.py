"""
SQLAlchemyを使用したマイグレーション: role と status カラムを追加
"""
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models.user import UserAuth


def run_migration():
    """role と status カラムを追加するマイグレーション"""
    print("Starting migration...")

    with engine.connect() as connection:
        try:
            # トランザクション開始
            trans = connection.begin()

            print("Step 1: Adding role column...")
            connection.execute(text("""
                ALTER TABLE users_auth
                ADD COLUMN IF NOT EXISTS role VARCHAR(20)
            """))

            print("Step 2: Setting role values based on user_type...")
            connection.execute(text("""
                UPDATE users_auth
                SET role = user_type
                WHERE role IS NULL
            """))

            print("Step 3: Making role column NOT NULL...")
            connection.execute(text("""
                ALTER TABLE users_auth
                ALTER COLUMN role SET NOT NULL
            """))

            print("Step 4: Adding index on role...")
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_auth_role
                ON users_auth(role)
            """))

            print("Step 5: Adding status column...")
            connection.execute(text("""
                ALTER TABLE users_auth
                ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active'
            """))

            print("Step 6: Adding index on status...")
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_auth_status
                ON users_auth(status)
            """))

            print("Step 7: Setting default status for existing records...")
            connection.execute(text("""
                UPDATE users_auth
                SET status = 'active'
                WHERE status IS NULL
            """))

            print("Step 8: Adding comments...")
            connection.execute(text("""
                COMMENT ON COLUMN users_auth.role IS
                'ユーザーロール: super_admin, coach, client'
            """))
            connection.execute(text("""
                COMMENT ON COLUMN users_auth.status IS
                'アカウント状態: active, inactive, suspended'
            """))

            # コミット
            trans.commit()
            print("\n" + "="*60)
            print("✓ Migration completed successfully!")
            print("="*60)
            print("\nNext steps:")
            print("1. Run: python create_super_admin.py")
            print("2. Start the backend server")

        except Exception as e:
            trans.rollback()
            print(f"\n✗ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    run_migration()
