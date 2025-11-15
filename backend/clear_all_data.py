"""
すべてのサンプルデータを削除するスクリプト
テストアカウント含む、すべてのユーザーとデータを削除します
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import UserAuth, Coach, Client
from app.models.application import Application, ApplicationHistory, CompanyAnalysis
from app.models.appointment import Appointment, CoachAvailability
from app.models.resume import (
    Resume, WorkExperience, EducationHistory,
    Certification, Skill, ResumeReview, ReviewComment, ReviewTemplate
)


def clear_all_data():
    """すべてのデータを削除"""
    db: Session = SessionLocal()

    try:
        print("すべてのデータを削除しています...")

        # 各テーブルからすべてのレコードを削除
        # リレーションシップを考慮して順序を決定

        print("  - Review comments")
        db.query(ReviewComment).delete()

        print("  - Resume reviews")
        db.query(ResumeReview).delete()

        print("  - Review templates")
        db.query(ReviewTemplate).delete()

        print("  - Skills")
        db.query(Skill).delete()

        print("  - Certifications")
        db.query(Certification).delete()

        print("  - Education history")
        db.query(EducationHistory).delete()

        print("  - Work experiences")
        db.query(WorkExperience).delete()

        print("  - Resumes")
        db.query(Resume).delete()

        print("  - Application history")
        db.query(ApplicationHistory).delete()

        print("  - Applications")
        db.query(Application).delete()

        print("  - Company analysis")
        db.query(CompanyAnalysis).delete()

        print("  - Appointments")
        db.query(Appointment).delete()

        print("  - Coach availability")
        db.query(CoachAvailability).delete()

        print("  - Clients")
        db.query(Client).delete()

        print("  - Coaches")
        db.query(Coach).delete()

        print("  - User auth")
        db.query(UserAuth).delete()

        db.commit()

        print("\n" + "="*50)
        print("すべてのデータを削除しました！")
        print("="*50)
        print("\n新しいアカウントを登録してください：")
        print("  - フロントエンドの登録ページから登録")
        print("  - または create_test_accounts.py を実行してテストアカウント作成")

    except Exception as e:
        db.rollback()
        print(f"\nエラーが発生しました: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    response = input("本当にすべてのデータを削除しますか？ (yes/no): ")
    if response.lower() == 'yes':
        clear_all_data()
    else:
        print("キャンセルしました")
