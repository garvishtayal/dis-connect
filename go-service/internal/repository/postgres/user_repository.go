package postgres

import (
	"context"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
)

// UserRepository persists and loads users.
type UserRepository struct {
	db *Client
}

// NewUserRepository creates a UserRepository.
func NewUserRepository(db *Client) *UserRepository {
	return &UserRepository{db: db}
}

// CreateUser inserts a new user row and returns its ID.
func (r *UserRepository) CreateUser(ctx context.Context, u *models.User) (string, error) {
	const query = `
INSERT INTO users (initial_prompt)
VALUES ($1)
RETURNING id;
`
	var id string
	if err := r.db.DB.QueryRowContext(ctx, query, u.InitialPrompt).Scan(&id); err != nil {
		return "", err
	}
	return id, nil
}

// UpsertAuthUser inserts or updates a user row keyed by Firebase UID.
func (r *UserRepository) UpsertAuthUser(ctx context.Context, u *models.User) (string, error) {
	const query = `
INSERT INTO users (
	firebase_uid,
	email,
	display_name,
	photo_url,
	provider,
	last_sign_in_at,
	initial_prompt
)
VALUES ($1, $2, $3, $4, $5, NOW(), $6)
ON CONFLICT (firebase_uid)
DO UPDATE SET
	email = EXCLUDED.email,
	display_name = COALESCE(EXCLUDED.display_name, users.display_name),
	photo_url = COALESCE(EXCLUDED.photo_url, users.photo_url),
	provider = EXCLUDED.provider,
	last_sign_in_at = NOW()
RETURNING id;
`
	var id string
	if err := r.db.DB.QueryRowContext(
		ctx,
		query,
		u.FirebaseUID,
		u.Email,
		u.DisplayName,
		u.PhotoURL,
		u.Provider,
		u.InitialPrompt,
	).Scan(&id); err != nil {
		return "", err
	}
	return id, nil
}
