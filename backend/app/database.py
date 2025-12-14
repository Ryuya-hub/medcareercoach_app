from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import urllib.parse
import os

# Pythonの環境をUTF-8に設定（Windows対応）
os.environ.setdefault('PYTHONUTF8', '1')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# DATABASE_URLをパースしてエンコーディングの問題を回避
database_url = settings.DATABASE_URL

if "sqlite" in database_url:
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL接続時にクライアントエンコーディングをUTF-8に設定
    # pool_recycle: 接続を1時間ごとにリサイクル（エンコーディング問題の回避）
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,  # 1時間ごとに接続をリサイクル
        connect_args={
            "client_encoding": "utf8",
            "options": "-c client_encoding=utf8",
            "sslmode": "require"
        },
        echo=False,  # SQLログを無効化
        pool_reset_on_return='rollback'  # 接続返却時にロールバック
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """データベースセッションの依存性注入用"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
