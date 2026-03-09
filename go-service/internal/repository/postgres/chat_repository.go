package postgres

import (
	"context"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
)

// ChatRepository persists and loads chat messages.
type ChatRepository struct {
	db *Client
}

// NewChatRepository creates a ChatRepository.
func NewChatRepository(db *Client) *ChatRepository {
	return &ChatRepository{db: db}
}

// SaveMessage stores a single chat message.
func (r *ChatRepository) SaveMessage(ctx context.Context, userID, role, content string) error {
	const query = `
INSERT INTO chat_messages (user_id, role, content)
VALUES ($1, $2, $3);
`
	_, err := r.db.DB.ExecContext(ctx, query, userID, role, content)
	return err
}

// CountMessages returns the total number of messages for a user.
func (r *ChatRepository) CountMessages(ctx context.Context, userID string) (int, error) {
	const query = `
SELECT COUNT(*)
FROM chat_messages
WHERE user_id = $1;
`
	var n int
	if err := r.db.DB.QueryRowContext(ctx, query, userID).Scan(&n); err != nil {
		return 0, err
	}
	return n, nil
}

// ListMessages returns recent chat messages for a user.
func (r *ChatRepository) ListMessages(ctx context.Context, userID string, limit int) ([]models.ChatMessage, error) {
	const query = `
SELECT role, content
FROM chat_messages
WHERE user_id = $1
ORDER BY created_at DESC
LIMIT $2;
`
	rows, err := r.db.DB.QueryContext(ctx, query, userID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var messages []models.ChatMessage
	for rows.Next() {
		var msg models.ChatMessage
		if err := rows.Scan(&msg.Role, &msg.Content); err != nil {
			return nil, err
		}
		messages = append(messages, msg)
	}
	return messages, rows.Err()
}

