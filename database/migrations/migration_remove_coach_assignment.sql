-- ======================================================
-- 担当コーチ概念の削除と面談予約へのコーチ紐付け追加
-- ======================================================

-- 1. 面談予約とコーチの多対多リレーションテーブルを作成
CREATE TABLE IF NOT EXISTS appointments_coaches (
    appointment_coach_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID NOT NULL REFERENCES appointments(appointment_id) ON DELETE CASCADE,
    coach_id UUID NOT NULL REFERENCES coaches(coach_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(appointment_id, coach_id)
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_appointments_coaches_appointment ON appointments_coaches(appointment_id);
CREATE INDEX IF NOT EXISTS idx_appointments_coaches_coach ON appointments_coaches(coach_id);

-- 2. clientsテーブルのcoach_idをnullableにする（削除はしない、既存データ保持のため）
-- すでにnullableなので何もしない

-- 3. 既存の予約データにコーチ情報を追加（appointmentsのcoach_idから取得）
INSERT INTO appointments_coaches (appointment_id, coach_id)
SELECT DISTINCT
    a.appointment_id,
    a.coach_id
FROM appointments a
WHERE a.coach_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM appointments_coaches ac
    WHERE ac.appointment_id = a.appointment_id
    AND ac.coach_id = a.coach_id
);

-- 完了メッセージ
DO $$
BEGIN
    RAISE NOTICE '担当コーチ概念削除のマイグレーション完了';
END $$;
