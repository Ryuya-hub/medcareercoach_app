"""
初期管理者アカウント作成スクリプト
指定されたメールアドレスとパスワードで管理者アカウントを作成します
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import UserAuth, Coach
from app.utils.auth import get_password_hash


def create_initial_admin():
    """初期管理者アカウントの作成"""
    db: Session = SessionLocal()

    # 初期管理者の情報
    admin_email = "rh.1129.music.music@gmail.com"
    admin_password = "rh1129217"
    admin_name = "システム管理者"

    try:
        print("初期管理者アカウントを作成しています...")

        # 既存のアカウントをチェック
        existing_user = db.query(UserAuth).filter(
            UserAuth.email == admin_email
        ).first()

        if existing_user:
            print(f"\nエラー: {admin_email} は既に登録されています")
            return

        # 認証情報の作成
        user_auth = UserAuth(
            email=admin_email,
            password_hash=get_password_hash(admin_password),
            user_type="coach",
            role="super_admin"
        )
        db.add(user_auth)
        db.flush()  # IDを取得するためにflush

        # コーチプロフィールの作成
        coach_profile = Coach(
            user_id=user_auth.user_id,
            name=admin_name,
            email=admin_email
        )
        db.add(coach_profile)
        db.commit()

        print("\n" + "="*50)
        print("初期管理者アカウントの作成が完了しました！")
        print("="*50)
        print(f"\nメールアドレス: {admin_email}")
        print(f"パスワード: {admin_password}")
        print(f"ユーザーID: {user_auth.user_id}")
        print("\nログイン方法:")
        print("  1. フロントエンド (http://localhost:3000/login) にアクセス")
        print(f"  2. メールアドレス: {admin_email}")
        print(f"  3. パスワード: {admin_password}")
        print("\n招待コード（コーチ登録用）:")
        print("  COACH2025SECURE")
        print("\nセキュリティのため、初回ログイン後はパスワードを変更することをお勧めします。")

    except Exception as e:
        db.rollback()
        print(f"\nエラーが発生しました: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_admin()
