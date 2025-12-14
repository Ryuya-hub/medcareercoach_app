-- Add name fields to coaches table
ALTER TABLE coaches
ADD COLUMN IF NOT EXISTS last_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS first_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS last_name_kana VARCHAR(50),
ADD COLUMN IF NOT EXISTS first_name_kana VARCHAR(50);

-- Add name fields to clients table
ALTER TABLE clients
ADD COLUMN IF NOT EXISTS last_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS first_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS last_name_kana VARCHAR(50),
ADD COLUMN IF NOT EXISTS first_name_kana VARCHAR(50);

-- Update name column to allow NULL for backward compatibility
ALTER TABLE coaches ALTER COLUMN name DROP NOT NULL;
ALTER TABLE clients ALTER COLUMN name DROP NOT NULL;

-- Populate name fields from existing name/furigana where they exist
UPDATE coaches
SET
    last_name = SPLIT_PART(name, ' ', 1),
    first_name = SPLIT_PART(name, ' ', 2),
    last_name_kana = SPLIT_PART(furigana, ' ', 1),
    first_name_kana = SPLIT_PART(furigana, ' ', 2)
WHERE name IS NOT NULL AND last_name IS NULL;

UPDATE clients
SET
    last_name = SPLIT_PART(name, ' ', 1),
    first_name = SPLIT_PART(name, ' ', 2),
    last_name_kana = SPLIT_PART(furigana, ' ', 1),
    first_name_kana = SPLIT_PART(furigana, ' ', 2)
WHERE name IS NOT NULL AND last_name IS NULL;
