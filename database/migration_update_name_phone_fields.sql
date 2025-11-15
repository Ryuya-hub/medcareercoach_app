-- Migration: Update name and phone fields
-- Date: 2025-11-13

-- ========================================
-- Clients Table
-- ========================================

-- Add new columns for clients
ALTER TABLE clients
ADD COLUMN IF NOT EXISTS last_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS first_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS last_name_kana VARCHAR(50),
ADD COLUMN IF NOT EXISTS first_name_kana VARCHAR(50);

-- Migrate existing name data to last_name (temporarily)
-- Note: This assumes existing names are full names
-- Users will need to manually split names or update them through the UI
UPDATE clients
SET last_name = name
WHERE last_name IS NULL;

-- Create a function to normalize phone numbers (remove hyphens)
CREATE OR REPLACE FUNCTION normalize_phone(phone_input TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN REGEXP_REPLACE(phone_input, '[^0-9]', '', 'g');
END;
$$ LANGUAGE plpgsql;

-- Normalize existing phone numbers in clients table
UPDATE clients
SET phone = normalize_phone(phone)
WHERE phone IS NOT NULL AND phone != '';

-- Drop old columns after migration (optional, commented out for safety)
-- ALTER TABLE clients DROP COLUMN IF EXISTS name;
-- ALTER TABLE clients DROP COLUMN IF EXISTS furigana;

-- ========================================
-- Coaches Table
-- ========================================

-- Add new columns for coaches
ALTER TABLE coaches
ADD COLUMN IF NOT EXISTS last_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS first_name VARCHAR(50),
ADD COLUMN IF NOT EXISTS last_name_kana VARCHAR(50),
ADD COLUMN IF NOT EXISTS first_name_kana VARCHAR(50);

-- Migrate existing name data to last_name (temporarily)
UPDATE coaches
SET last_name = name
WHERE last_name IS NULL;

-- Normalize existing phone numbers in coaches table
UPDATE coaches
SET phone = normalize_phone(phone)
WHERE phone IS NOT NULL AND phone != '';

-- Drop old columns after migration (optional, commented out for safety)
-- ALTER TABLE coaches DROP COLUMN IF EXISTS name;
-- ALTER TABLE coaches DROP COLUMN IF EXISTS furigana;

-- Add comment for future reference
COMMENT ON COLUMN clients.last_name IS '姓（苗字）';
COMMENT ON COLUMN clients.first_name IS '名';
COMMENT ON COLUMN clients.last_name_kana IS '姓（苗字）のふりがな';
COMMENT ON COLUMN clients.first_name_kana IS '名のふりがな';
COMMENT ON COLUMN clients.phone IS '電話番号（ハイフンなし、数字のみ）';

COMMENT ON COLUMN coaches.last_name IS '姓（苗字）';
COMMENT ON COLUMN coaches.first_name IS '名';
COMMENT ON COLUMN coaches.last_name_kana IS '姓（苗字）のふりがな';
COMMENT ON COLUMN coaches.first_name_kana IS '名のふりがな';
COMMENT ON COLUMN coaches.phone IS '電話番号（ハイフンなし、数字のみ）';
