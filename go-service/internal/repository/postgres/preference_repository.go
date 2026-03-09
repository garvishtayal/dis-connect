package postgres

import "context"

// PreferenceRepository persists user preferences in Postgres.
type PreferenceRepository struct {
	db *Client
}

// NewPreferenceRepository creates a PreferenceRepository.
func NewPreferenceRepository(db *Client) *PreferenceRepository {
	return &PreferenceRepository{db: db}
}

// UpdatePreferences updates the JSONB preferences column for a user.
// The preferences argument is marshaled to JSON.
func (r *PreferenceRepository) UpdatePreferences(ctx context.Context, userID string, preferences map[string]any) error {
	if preferences == nil {
		preferences = map[string]any{}
	}
	const query = `
UPDATE users
SET preferences = $2
WHERE id = $1;
`
	_, err := r.db.DB.ExecContext(ctx, query, userID, preferences)
	return err
}

