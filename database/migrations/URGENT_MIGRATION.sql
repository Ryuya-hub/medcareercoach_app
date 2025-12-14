-- ⚠️ 緊急マイグレーション：role と status カラムを追加
-- このSQLをSupabase SQL Editorで実行してください

-- トランザクション開始
BEGIN;

-- 1. role カラムを追加
ALTER TABLE users_auth
ADD COLUMN IF NOT EXISTS role VARCHAR(20);

-- 2. 既存のレコードに role を設定（user_typeをコピー）
UPDATE users_auth
SET role = user_type
WHERE role IS NULL;

-- 3. role カラムを NOT NULL に変更
ALTER TABLE users_auth
ALTER COLUMN role SET NOT NULL;

-- 4. role カラムにインデックスを追加
CREATE INDEX IF NOT EXISTS idx_users_auth_role ON users_auth(role);

-- 5. status カラムを追加
ALTER TABLE users_auth
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';

-- 6. 既存のレコードに status を設定
UPDATE users_auth
SET status = 'active'
WHERE status IS NULL;

-- 7. status カラムにインデックスを追加
CREATE INDEX IF NOT EXISTS idx_users_auth_status ON users_auth(status);

-- 8. rh.main.address@gmail.com に統括管理者権限を付与
UPDATE users_auth
SET role = 'super_admin', status = 'active'
WHERE email = 'rh.main.address@gmail.com';

-- 9. コメントを追加
COMMENT ON COLUMN users_auth.role IS 'ユーザーロール: super_admin, coach, client';
COMMENT ON COLUMN users_auth.status IS 'アカウント状態: active, inactive, suspended';

-- コミット
COMMIT;

-- ✅ マイグレーション完了
-- 以下のクエリで確認してください:
-- SELECT email, user_type, role, status FROM users_auth WHERE email = 'rh.main.address@gmail.com';
