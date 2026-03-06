package postgres

import (
	"context"
)

// ContentRepository handles content cache and shown_content.
type ContentRepository struct {
	db *Client
}

// NewContentRepository creates a ContentRepository.
func NewContentRepository(db *Client) *ContentRepository {
	return &ContentRepository{db: db}
}

// MarkShown inserts a shown_content row for a user and URL.
func (r *ContentRepository) MarkShown(ctx context.Context, userID, url string) error {
	const query = `
INSERT INTO shown_content (user_id, content_url)
VALUES ($1, $2)
ON CONFLICT (user_id, content_url) DO NOTHING;
`
	_, err := r.db.DB.ExecContext(ctx, query, userID, url)
	return err
}

// WasShown checks if a URL has been shown to a user.
func (r *ContentRepository) WasShown(ctx context.Context, userID, url string) (bool, error) {
	const query = `
SELECT 1
FROM shown_content
WHERE user_id = $1 AND content_url = $2
LIMIT 1;
`
	var one int
	err := r.db.DB.QueryRowContext(ctx, query, userID, url).Scan(&one)
	if err != nil {
		return false, nil
	}
	return true, nil
}

