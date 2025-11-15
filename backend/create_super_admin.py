"""
統括管理者アカウント作成スクリプト
rh.main.address@gmail.com に統括管理者権限を付与します
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import UserAuth, Coach
from app.utils.auth import get_password_hash


def create_super_admin():
    """統括管理者アカウントの作成"""
    db: Session = SessionLocal()

    # 統括管理者の情報
    admin_email = "rh.main.address@gmail.com"
    admin_password = "rh1129217"
    admin_name = "統括管理者"

    try:
        print("統括管理者アカウントを作成しています...")

        # 既存のアカウントをチェック
        existing_user = db.query(UserAuth).filter(
            UserAuth.email == admin_email
        ).first()

        if existing_user:
            print(f"\n既存のアカウントが見つかりました: {admin_email}")
            print("統括管理者権限を付与しています...")

            # 統括管理者権限を付与
            existing_user.role = "super_admin"
            existing_user.status = "active"
            db.commit()

            print("\n" + "="*60)
            print("既存アカウントに統括管理者権限を付与しました！")
            print("="*60)
            print(f"\nメールアドレス: {admin_email}")
            print(f"ユーザーID: {existing_user.user_id}")
            print(f"ロール: {existing_user.role}")
            print(f"ステータス: {existing_user.status}")
            return

        # 新規アカウントを作成
        print(f"\n新規アカウントを作成します: {admin_email}")

        # 認証情報の作成
        user_auth = UserAuth(
            email=admin_email,
            password_hash=get_password_hash(admin_password),
            user_type="coach",
            role="super_admin",
            status="active"
        )
        db.add(user_auth)
        db.flush()  # IDを取得するためにflush

        # コーチプロフィールの作成
        coach_profile = Coach(
            user_id=user_auth.user_id,
            name=admin_name,
            last_name="統括",
            first_name="管理者",
            last_name_kana="トウカツ",
            first_name_kana="カンリシャ",
            email=admin_email
        )
        db.add(coach_profile)
        db.commit()

        print("\n" + "="*60)
        print("統括管理者アカウントの作成が完了しました！")
        print("="*60)
        print(f"\nメールアドレス: {admin_email}")
        print(f"パスワード: {admin_password}")
        print(f"ユーザーID: {user_auth.user_id}")
        print(f"ロール: {user_auth.role}")
        print(f"ステータス: {user_auth.status}")
        print("\nログイン方法:")
        print("  1. フロントエンド (http://localhost:3000/login) にアクセス")
        print(f"  2. メールアドレス: {admin_email}")
        print(f"  3. パスワード: {admin_password}")
        print("\n統括管理者の権限:")
        print("  ✓ すべてのコーチ/利用者のアカウント管理")
        print("  ✓ アカウントの強制削除")
        print("  ✓ アカウントの新規登録（アドレス/パスワードを付与）")
        print("  ✓ アカウントのステータス変更")

    except Exception as e:
        db.rollback()
        print(f"\nエラーが発生しました: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_super_admin()
