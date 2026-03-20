package postgres

import (
	"context"
	"database/sql"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
)

// UpgradeRepository persists and loads user_upgrades rows.
type UpgradeRepository struct {
	db *Client
}

// NewUpgradeRepository creates an UpgradeRepository.
func NewUpgradeRepository(db *Client) *UpgradeRepository {
	return &UpgradeRepository{db: db}
}

// Upsert inserts or updates the upgrade record for a user.
func (r *UpgradeRepository) Upsert(ctx context.Context, userID string, upgraded bool, feedback, willingToPay *string) error {
	const query = `
INSERT INTO user_upgrades (user_id, upgraded, feedback, willing_to_pay, updated_at)
VALUES ($1, $2, $3, $4, NOW())
ON CONFLICT (user_id)
DO UPDATE SET
	upgraded       = EXCLUDED.upgraded,
	feedback       = EXCLUDED.feedback,
	willing_to_pay = EXCLUDED.willing_to_pay,
	updated_at     = NOW();
`
	_, err := r.db.DB.ExecContext(ctx, query, userID, upgraded, feedback, willingToPay)
	return err
}

// Get returns the upgrade record for a user. Returns nil if not found.
func (r *UpgradeRepository) Get(ctx context.Context, userID string) (*models.UpgradeRecord, error) {
	const query = `
SELECT user_id, upgraded, feedback, willing_to_pay
FROM user_upgrades
WHERE user_id = $1;
`
	var rec models.UpgradeRecord
	err := r.db.DB.QueryRowContext(ctx, query, userID).Scan(
		&rec.UserID,
		&rec.Upgraded,
		&rec.Feedback,
		&rec.WillingToPay,
	)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	return &rec, nil
}
