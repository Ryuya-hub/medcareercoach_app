# 統括管理者機能セットアップガイド

## 概要
このガイドでは、統括管理者機能を有効化し、`rh.main.address@gmail.com` アカウントに統括管理者権限を付与する手順を説明します。

## 手順

### 1. データベースマイグレーション（Supabase Studioで実行）

Supabase Studio の SQL Editor で以下のSQLを実行してください：

```sql
-- 1. role カラムを追加（デフォルトは NULL）
ALTER TABLE users_auth
ADD COLUMN IF NOT EXISTS role VARCHAR(20);

-- 2. 既存レコードの role を user_type に基づいて設定
UPDATE users_auth
SET role = user_type
WHERE role IS NULL;

-- 3. role カラムを NOT NULL に変更
ALTER TABLE users_auth
ALTER COLUMN role SET NOT NULL;

-- 4. role カラムにインデックスを追加
CREATE INDEX IF NOT EXISTS idx_users_auth_role ON users_auth(role);

-- 5. status カラムを追加（アカウントの状態管理）
ALTER TABLE users_auth
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';

-- 6. status カラムにインデックスを追加
CREATE INDEX IF NOT EXISTS idx_users_auth_status ON users_auth(status);

-- 7. コメント追加
COMMENT ON COLUMN users_auth.role IS 'ユーザーロール: super_admin, coach, client';
COMMENT ON COLUMN users_auth.status IS 'アカウント状態: active, inactive, suspended';
```

### 2. 統括管理者アカウントの作成

バックエンドディレクトリで以下のスクリプトを実行：

```bash
cd backend
python create_super_admin.py
```

このスクリプトは：
- `rh.main.address@gmail.com` が既に存在する場合：統括管理者権限を付与
- アカウントが存在しない場合：新規作成（パスワード: `rh1129217`）

### 3. 統括管理者の権限

✅ すべてのコーチ/利用者のアカウントを管理
✅ アカウントの強制削除
✅ アカウントの新規登録（メールアドレス/パスワードを管理者が付与）
✅ アカウントのステータス変更（active, inactive, suspended）

### 4. ログイン情報

**統括管理者アカウント:**
- メールアドレス: `rh.main.address@gmail.com`
- パスワード: `rh1129217`
- ロール: `super_admin`

### 5. 管理画面へのアクセス

ログイン後、ダッシュボードに「ユーザー管理」メニューが表示されます（統括管理者のみ）。

### 6. API エンドポイント

統括管理者専用APIエンドポイント：

- `GET /api/admin/users` - 全ユーザーリスト取得
- `PATCH /api/admin/users/{user_id}/status` - ユーザーステータス変更
- `DELETE /api/admin/users/{user_id}` - ユーザー削除
- `POST /api/admin/users` - 新規ユーザー作成

### トラブルシューティング

**マイグレーションエラーが発生する場合：**
1. Supabase StudioのTable Editorで`users_auth`テーブルを確認
2. `role`カラムと`status`カラムが既に存在する場合は、マイグレーションをスキップ

**統括管理者作成スクリプトが失敗する場合：**
1. `.env`ファイルの`DATABASE_URL`が正しいか確認
2. Supabaseの接続情報が最新か確認
3. 手動でSupabase StudioのSQL Editorから以下を実行：

```sql
-- 既存ユーザーに統括管理者権限を付与
UPDATE users_auth
SET role = 'super_admin', status = 'active'
WHERE email = 'rh.main.address@gmail.com';
```

## 次のステップ

1. バックエンドサーバーを起動: `uvicorn app.main:app --reload`
2. フロントエンドサーバーを起動: `npm run dev`
3. `http://localhost:3000/login` でログイン
4. ダッシュボードの「ユーザー管理」から機能を確認
