"""
テストアカウント作成スクリプト
管理者（coach）と利用者（client）のテストアカウントを1つずつ作成します
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import UserAuth, Coach, Client
from app.utils.auth import get_password_hash


def create_test_accounts():
    """テストアカウントの作成"""
    db: Session = SessionLocal()

    try:
        print("テストアカウントを作成しています...")

        # 1. 管理者（Coach）アカウントの作成
        print("\n=== 管理者アカウント（Coach） ===")

        # 既存の管理者アカウントをチェック
        existing_coach_auth = db.query(UserAuth).filter(
            UserAuth.email == "coach@example.com"
        ).first()

        if existing_coach_auth:
            print("管理者アカウントは既に存在します")
            coach_user = existing_coach_auth
        else:
            # 認証情報の作成
            coach_user = UserAuth(
                email="coach@example.com",
                password_hash=get_password_hash("coach123"),
                user_type="coach",
                role="coach"
            )
            db.add(coach_user)
            db.flush()  # IDを取得するためにflush

            # コーチプロフィールの作成
            coach_profile = Coach(
                user_id=coach_user.user_id,
                name="田中 太郎",
                furigana="たなか たろう",
                email="coach@example.com",
                phone="090-1234-5678",
                mtg_url="https://meet.google.com/test-coach"
            )
            db.add(coach_profile)
            db.commit()

            print("管理者アカウントを作成しました")

        print(f"  メールアドレス: coach@example.com")
        print(f"  パスワード: coach123")
        print(f"  ユーザーID: {coach_user.user_id}")

        # 2. 利用者（Client）アカウントの作成
        print("\n=== 利用者アカウント（Client） ===")

        # 既存の利用者アカウントをチェック
        existing_client_auth = db.query(UserAuth).filter(
            UserAuth.email == "client@example.com"
        ).first()

        if existing_client_auth:
            print("利用者アカウントは既に存在します")
            client_user = existing_client_auth
        else:
            # 認証情報の作成
            client_user = UserAuth(
                email="client@example.com",
                password_hash=get_password_hash("client123"),
                user_type="client",
                role="client"
            )
            db.add(client_user)
            db.flush()  # IDを取得するためにflush

            # クライアントプロフィールの作成
            client_profile = Client(
                user_id=client_user.user_id,
                name="山田 花子",
                furigana="やまだ はなこ",
                email="client@example.com",
                phone="080-9876-5432",
                company_name="株式会社サンプル",
                occupation="営業職",
                status="active"
            )
            db.add(client_profile)
            db.commit()

            print("利用者アカウントを作成しました")

        print(f"  メールアドレス: client@example.com")
        print(f"  パスワード: client123")
        print(f"  ユーザーID: {client_user.user_id}")

        print("\n" + "="*50)
        print("テストアカウントの作成が完了しました！")
        print("="*50)
        print("\nログイン方法:")
        print("  1. バックエンドを起動: uvicorn app.main:app --reload")
        print("  2. フロントエンドからログイン:")
        print("     - 管理者: coach@example.com / coach123")
        print("     - 利用者: client@example.com / client123")

    except Exception as e:
        db.rollback()
        print(f"\nエラーが発生しました: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_accounts()
