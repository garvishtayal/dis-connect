UPDATE users
SET initial_prompt = 'Manifest your next big role'
WHERE initial_prompt IS NULL;

ALTER TABLE users
ALTER COLUMN initial_prompt SET NOT NULL;

ALTER TABLE users
DROP COLUMN IF EXISTS onboarding_completed;
