"""
利用者に担当コーチを割り当てるスクリプト
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import Coach, Client


def assign_coach():
    """利用者に担当コーチを割り当て（多対多リレーション）"""
    db: Session = SessionLocal()

    try:
        print("担当コーチの割り当てを開始します...")

        # コーチを取得
        coach = db.query(Coach).filter(Coach.email == "coach@example.com").first()
        if not coach:
            print("エラー: コーチが見つかりません")
            return

        print(f"コーチ: {coach.name} (ID: {coach.coach_id})")

        # 利用者を取得
        client = db.query(Client).filter(Client.email == "client@example.com").first()
        if not client:
            print("エラー: 利用者が見つかりません")
            return

        print(f"利用者: {client.name} (ID: {client.client_id})")

        # 多対多リレーションシップに追加
        if coach not in client.coaches:
            client.coaches.append(coach)

        # 主担当コーチとしても設定
        client.coach_id = coach.coach_id
        db.commit()

        print("\n担当コーチの割り当てが完了しました！")
        print(f"利用者「{client.name}」の担当コーチは「{coach.name}」になりました")
        print(f"担当コーチ数: {len(client.coaches)}")

    except Exception as e:
        db.rollback()
        print(f"\nエラーが発生しました: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    assign_coach()
