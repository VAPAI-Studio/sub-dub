-- Add target_language to dubs table
ALTER TABLE dubs ADD COLUMN IF NOT EXISTS target_language text DEFAULT 'unknown';

-- Backfill: copy target_language from translations where project_id matches
UPDATE dubs d
SET target_language = t.target_language
FROM translations t
WHERE d.project_id = t.project_id
  AND d.target_language = 'unknown';

-- Remove duplicate translations (keep most recent per project+language)
DELETE FROM translations a
USING translations b
WHERE a.project_id = b.project_id
  AND a.target_language = b.target_language
  AND a.created_at < b.created_at;

-- Remove duplicate dubs (keep most recent per project+language)
DELETE FROM dubs a
USING dubs b
WHERE a.project_id = b.project_id
  AND a.target_language = b.target_language
  AND a.created_at < b.created_at;

-- Add unique constraints
ALTER TABLE translations ADD CONSTRAINT translations_project_language_unique UNIQUE (project_id, target_language);
ALTER TABLE dubs ADD CONSTRAINT dubs_project_language_unique UNIQUE (project_id, target_language);
