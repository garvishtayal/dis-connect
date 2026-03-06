package redisrepo

import (
	"context"
)

// DedupRepository tracks which content URLs were shown.
type DedupRepository struct {
	client *Client
}

// NewDedupRepository creates a DedupRepository.
func NewDedupRepository(client *Client) *DedupRepository {
	return &DedupRepository{client: client}
}

// MarkShown marks a URL as shown for a user.
func (r *DedupRepository) MarkShown(ctx context.Context, userID, url string) error {
	key := "shown:" + userID
	return r.client.Client.SAdd(ctx, key, url).Err()
}

// WasShown checks if a URL was already shown for a user.
func (r *DedupRepository) WasShown(ctx context.Context, userID, url string) (bool, error) {
	key := "shown:" + userID
	res, err := r.client.Client.SIsMember(ctx, key, url).Result()
	if err != nil {
		return false, err
	}
	return res, nil
}

