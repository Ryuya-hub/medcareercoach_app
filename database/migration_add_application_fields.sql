-- Migration: Add next_action_date, preference_rating, and interview_questions to applications table
-- Date: 2025-11-13

-- Add next_action_date column
ALTER TABLE applications
ADD COLUMN IF NOT EXISTS next_action_date DATE;

-- Add preference_rating column with default value of 3
ALTER TABLE applications
ADD COLUMN IF NOT EXISTS preference_rating INTEGER DEFAULT 3;

-- Add interview_questions column (JSONB for PostgreSQL)
ALTER TABLE applications
ADD COLUMN IF NOT EXISTS interview_questions JSONB;

-- Update existing records to have default preference_rating of 3
UPDATE applications
SET preference_rating = 3
WHERE preference_rating IS NULL;
