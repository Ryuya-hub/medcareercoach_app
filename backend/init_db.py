"""
データベース初期化スクリプト
既存のテーブルをすべて削除し、新しいテーブルを作成します
"""
from app.database import Base, engine
from app.models.user import UserAuth, Coach, Client, client_coach_association
from app.models.application import Application, ApplicationHistory, CompanyAnalysis
from app.models.appointment import Appointment, CoachAvailability, appointment_coaches
from app.models.resume import (
    Resume, WorkExperience, EducationHistory,
    Certification, Skill, ResumeReview, ReviewComment, ReviewTemplate
)


def init_database():
    """データベースの初期化"""
    print("データベーステーブルを作成しています...")

    # すべてのテーブルを削除（既存データがある場合）
    Base.metadata.drop_all(bind=engine)
    print("既存のテーブルを削除しました")

    # すべてのテーブルを作成
    Base.metadata.create_all(bind=engine)
    print("新しいテーブルを作成しました")

    print("\n作成されたテーブル:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

    print("\nデータベースの初期化が完了しました！")


if __name__ == "__main__":
    init_database()
