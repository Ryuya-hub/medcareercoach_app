# 転職支援顧客管理システム

転職支援会社向けの顧客管理WEBアプリケーション

## 機能概要

### コーチ向け機能
- ダッシュボード（統計情報、今週の面談、添削待ちリスト）
- 顧客管理（CRUD、検索、ステータス管理）
- 応募企業管理（応募状況の管理、履歴追跡、企業分析）
- 面談予約管理（カレンダー表示、空き枠登録、予約管理）
- 職務経歴書添削（閲覧、コメント追加、添削完了）

### 利用者向け機能
- ダッシュボード（応募状況、統計情報）
- 応募企業管理（応募登録、進捗管理）
- 面談予約（コーチの空き枠確認、予約申請）
- 職務経歴書作成・編集（基本情報、職務経歴、学歴、資格、スキル、自己PR、志望動機）

## 技術スタック

### バックエンド
- **フレームワーク**: FastAPI 0.109.0
- **ORM**: SQLAlchemy 2.0.25
- **データベース**: Supabase (PostgreSQL)
- **認証**: JWT (python-jose)
- **パスワードハッシュ**: bcrypt (passlib)

### フロントエンド
- **フレームワーク**: React 18.2.0
- **ビルドツール**: Vite 5.0
- **ルーティング**: React Router 6
- **状態管理**: Zustand, TanStack Query
- **UIスタイリング**: Tailwind CSS 3.4
- **フォーム**: React Hook Form + Zod
- **通知**: React Hot Toast
- **アイコン**: Lucide React

## セットアップ

### 前提条件
- Python 3.9+
- Node.js 18+
- Supabase アカウント

### 1. Supabase データベースのセットアップ

Supabaseダッシュボードで新しいプロジェクトを作成し、`database/schema.sql`を実行してテーブルを作成します。

```bash
# Supabase SQLエディタで実行
psql -h <supabase-host> -U postgres -d postgres -f database/schema.sql
```

### 2. バックエンドのセットアップ

```bash
cd backend

# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化 (Windows)
venv\Scripts\activate
# 仮想環境の有効化 (Mac/Linux)
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
copy .env.example .env
# .envファイルを編集して、Supabaseの接続情報を設定

# アプリケーションの起動
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. フロントエンドのセットアップ

```bash
cd frontend

# 依存パッケージのインストール
npm install

# 環境変数の設定
echo "VITE_API_URL=http://localhost:8000" > .env

# 開発サーバーの起動
npm run dev
```

### 4. アクセス

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs

## 環境変数

### バックエンド (.env)

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
DATABASE_URL=postgresql://user:password@host:port/database

# JWT Configuration
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

### フロントエンド (.env)

```env
VITE_API_URL=http://localhost:8000
```

## プロジェクト構造

```
job-support-app/
├── backend/              # バックエンド（FastAPI）
│   ├── app/
│   │   ├── api/         # APIエンドポイント
│   │   ├── models/      # SQLAlchemyモデル
│   │   ├── schemas/     # Pydanticスキーマ
│   │   ├── services/    # ビジネスロジック
│   │   ├── utils/       # ユーティリティ
│   │   ├── config.py    # 設定
│   │   ├── database.py  # DB接続
│   │   └── main.py      # アプリケーションエントリーポイント
│   └── requirements.txt
├── frontend/            # フロントエンド（React）
│   ├── src/
│   │   ├── components/  # Reactコンポーネント
│   │   ├── pages/       # ページコンポーネント
│   │   ├── services/    # API通信
│   │   ├── context/     # Context API
│   │   ├── hooks/       # カスタムフック
│   │   └── App.jsx      # ルートコンポーネント
│   └── package.json
└── database/            # データベーススキーマ
    └── schema.sql
```

## API エンドポイント

### 認証
- `POST /api/auth/login` - ログイン
- `POST /api/auth/register` - ユーザー登録
- `GET /api/auth/verify` - トークン検証
- `POST /api/auth/logout` - ログアウト

### 顧客管理
- `GET /api/clients` - 顧客一覧
- `GET /api/clients/{id}` - 顧客詳細
- `POST /api/clients` - 顧客登録
- `PUT /api/clients/{id}` - 顧客更新
- `DELETE /api/clients/{id}` - 顧客削除

### 応募企業管理
- `GET /api/applications` - 応募一覧
- `GET /api/applications/{id}` - 応募詳細
- `POST /api/applications` - 応募登録
- `PUT /api/applications/{id}` - 応募更新
- `GET /api/applications/history/{id}` - 応募履歴

### 面談予約管理
- `GET /api/appointments` - 予約一覧
- `GET /api/appointments/{id}` - 予約詳細
- `POST /api/appointments` - 予約作成
- `PUT /api/appointments/{id}` - 予約更新
- `DELETE /api/appointments/{id}` - 予約キャンセル
- `GET /api/appointments/coach-availability/{coach_id}` - コーチ空き枠取得

### 職務経歴書管理
- `GET /api/resumes/client/{client_id}` - 顧客の職務経歴書一覧
- `GET /api/resumes/{id}` - 職務経歴書詳細
- `POST /api/resumes` - 職務経歴書作成
- `PUT /api/resumes/{id}` - 職務経歴書更新
- `POST /api/resumes/{id}/submit` - 職務経歴書提出
- `GET /api/resumes/coach/pending` - 添削待ち一覧

## 主要機能の使い方

### 1. ユーザー登録とログイン
1. http://localhost:3000 にアクセス
2. 「アカウント登録はこちら」をクリック
3. 必要情報を入力（ユーザータイプ：コーチまたは利用者）
4. 登録後、自動的にダッシュボードに遷移

### 2. 職務経歴書の作成（利用者）
1. 利用者でログイン
2. サイドバーから「職務経歴書」をクリック
3. 基本情報、自己PR、志望動機を入力
4. 「保存」をクリック
5. 「コーチに提出」をクリック

### 3. 職務経歴書の添削（コーチ）
1. コーチでログイン
2. サイドバーから「職務経歴書添削」をクリック
3. 添削待ちリストから職務経歴書を選択
4. 内容を確認してコメントを入力
5. 「添削完了」をクリック

### 4. 応募企業の管理
1. サイドバーから「応募管理」をクリック
2. 「新規応募登録」をクリック
3. 企業名、応募日、選考段階を入力
4. 「登録」をクリック

## 開発

### バックエンドのテスト実行
```bash
cd backend
pytest
```

### フロントエンドのビルド
```bash
cd frontend
npm run build
```

### コード品質チェック
```bash
# フロントエンド
npm run lint

# バックエンド
flake8 app/
```

## デプロイ

### バックエンド
- Heroku、AWS、Google Cloud、Renderなどにデプロイ可能
- Dockerイメージを作成してコンテナデプロイも可能

### フロントエンド
- Vercel、Netlify、AWS S3 + CloudFrontなどにデプロイ可能

## ライセンス

MIT License

## サポート

問題が発生した場合は、Issueを作成してください。


  - フロントエンド: http://localhost:3000
  - ログインページ: http://localhost:3000/login

  アカウント情報

  初期管理者アカウント:
  - メールアドレス: rh.1129.music.music@gmail.com
  - パスワード: rh1129217

  新規登録:
  - 利用者登録: http://localhost:3000/register
  - 管理者登録: http://localhost:3000/register/coach（招待コード: COACH2025SECURE）
  - 
  https://medcareercoach-app.netlify.app/admin/dashboard
アカウント管理

https://medcareercoach-app.netlify.app/login
ログイン画面

https://medcareercoach-app.netlify.app/admin/dashboard
アカウント管理

https://medcareercoach-app.netlify.app/login
ログイン画面


  現在の状況

  - ✓ バックエンド: http://localhost:8000 で起動中
  - ✓ データベース: Supabase に接続済み
  - ✓ 初期管理者アカウント: 作成済み
  - ✓ データベース: Supabase に接続済み
  - ✓ 初期管理者アカウント: 作成済み
  - ⏳ フロントエンド: 手動で起動してください

    利用者としてログイン:
  - メール: client@example.com
  - パスワード: client123

  コーチとしてログイン:
  - メール: coach@example.com
  - パスワード: coach123
