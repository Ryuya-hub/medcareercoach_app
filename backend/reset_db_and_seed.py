"""
本番環境用データリセット＆シードスクリプト
注意: このスクリプトを実行すると、データベース内の全データが消去・再作成されます。
"""
import sys
import os

# パスを解決してappモジュールをインポート可能にする
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.database import Base, engine
from create_initial_admin import create_initial_admin
from create_test_accounts import create_test_accounts

def reset_and_seed():
    print("WARNING: This will DELETE ALL DATA in the database.")
    confirm = input("Type 'yes' to proceed: ")
    if confirm != 'yes':
        print("Aborted.")
        return

    print("\n[1/3] Dropping and Recreating Tables...")
    try:
        # テーブル削除・再作成
        # Note: カスケード削除が必要な場合はSQLを直接実行する必要があるかもしれませんが、
        # SQLAlchemyのmetadata.drop_allは依存関係順に削除を試みます。
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("Tables recreated successfully.")
    except Exception as e:
        print(f"Error resetting tables: {e}")
        return

    print("\n[2/3] Creating Initial Admin...")
    try:
        create_initial_admin()
    except Exception as e:
        print(f"Error creating admin: {e}")

    print("\n[3/3] Creating Test Accounts...")
    try:
        create_test_accounts()
    except Exception as e:
        print(f"Error creating test accounts: {e}")

    print("\nDone!")

if __name__ == "__main__":
    # 非対話モードで実行したい場合は入力をスキップするロジックが必要だが、
    # 安全のためデフォルトは確認ありにする。
    # サーバーコンソールで実行することを想定。
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        # Force mode logic could be added here
        pass
    
    reset_and_seed()
