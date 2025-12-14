-- 職務経歴書テーブルをフリーテキスト形式に変更するマイグレーション
-- 実行前に必ずバックアップを取得してください

-- 1. 新しいcontentカラムを追加
ALTER TABLE resumes ADD COLUMN IF NOT EXISTS content TEXT;

-- 2. 既存データを移行（既存のself_prとmotivationをcontentに統合）
UPDATE resumes
SET content = COALESCE(
  NULLIF(TRIM(CONCAT_WS(E'\n\n',
    CASE WHEN self_pr IS NOT NULL THEN '【自己PR】' || E'\n' || self_pr END,
    CASE WHEN motivation IS NOT NULL THEN '【志望動機】' || E'\n' || motivation END
  )), ''),
  ''
)
WHERE content IS NULL;

-- 3. 古いカラムを削除
ALTER TABLE resumes DROP COLUMN IF EXISTS full_name;
ALTER TABLE resumes DROP COLUMN IF EXISTS birth_date;
ALTER TABLE resumes DROP COLUMN IF EXISTS address;
ALTER TABLE resumes DROP COLUMN IF EXISTS phone;
ALTER TABLE resumes DROP COLUMN IF EXISTS email;
ALTER TABLE resumes DROP COLUMN IF EXISTS desired_position;
ALTER TABLE resumes DROP COLUMN IF EXISTS desired_salary;
ALTER TABLE resumes DROP COLUMN IF EXISTS self_pr;
ALTER TABLE resumes DROP COLUMN IF EXISTS motivation;

-- 4. 確認用クエリ（コメントアウトを外して実行）
-- SELECT resume_id, client_id, version_number, status,
--        LEFT(content, 100) as content_preview,
--        created_at
-- FROM resumes
-- ORDER BY created_at DESC
-- LIMIT 10;
