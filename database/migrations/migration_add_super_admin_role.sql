-- 統括管理者機能を追加するマイグレーション
-- users_auth テーブルに role カラムを追加

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

-- コメント追加
COMMENT ON COLUMN users_auth.role IS 'ユーザーロール: super_admin, coach, client';
COMMENT ON COLUMN users_auth.status IS 'アカウント状態: active, inactive, suspended';
