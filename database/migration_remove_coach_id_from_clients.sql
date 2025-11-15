-- Migration: Remove coach_id column from clients table
-- Description: 担当コーチ概念を完全削除。client_coach多対多テーブルに移行済み

-- clients テーブルからcoach_idカラムを削除
-- (外部キー制約があるため、まず外部キーを削除してからカラムを削除)

-- Step 1: 外部キー制約を確認して削除
DO $$
BEGIN
    -- 外部キー制約が存在する場合のみ削除
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'clients_coach_id_fkey'
        AND table_name = 'clients'
    ) THEN
        ALTER TABLE clients DROP CONSTRAINT clients_coach_id_fkey;
        RAISE NOTICE 'Dropped foreign key constraint: clients_coach_id_fkey';
    END IF;
END $$;

-- Step 2: coach_idカラムを削除
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'clients'
        AND column_name = 'coach_id'
    ) THEN
        ALTER TABLE clients DROP COLUMN coach_id;
        RAISE NOTICE 'Dropped column: coach_id from clients table';
    ELSE
        RAISE NOTICE 'Column coach_id does not exist in clients table';
    END IF;
END $$;

-- Step 3: コメントを追加
COMMENT ON TABLE client_coach IS '利用者とコーチの多対多リレーション。担当コーチ概念廃止後はこちらを使用。';
