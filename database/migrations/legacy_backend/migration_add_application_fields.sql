-- Add interview_questions JSONB field to applications table
ALTER TABLE applications
ADD COLUMN IF NOT EXISTS interview_questions JSONB DEFAULT '{}'::jsonb;
