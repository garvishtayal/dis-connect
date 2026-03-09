package redisrepo

import (
	"context"
	"fmt"
	"time"
)

// Key format matches Python app/redis/client.py: user:{user_id}:shown (SET of URLs).
const keyShownFmt = "user:%s:shown"

// TTL for shown set; matches Python TTL_SHOWN_DAYS = 7.
const ttlShown = 7 * 24 * time.Hour

// DedupRepository tracks which content URLs were shown. Python reads this set for dedup.
type DedupRepository struct {
	client *Client
}

// NewDedupRepository creates a DedupRepository.
func NewDedupRepository(client *Client) *DedupRepository {
	return &DedupRepository{client: client}
}

func shownKey(userID string) string {
	return fmt.Sprintf(keyShownFmt, userID)
}

// MarkShown marks a URL as shown for a user.
func (r *DedupRepository) MarkShown(ctx context.Context, userID, url string) error {
	key := shownKey(userID)
	if err := r.client.Client.SAdd(ctx, key, url).Err(); err != nil {
		return err
	}
	return r.client.Client.Expire(ctx, key, ttlShown).Err()
}

// MarkShownBatch adds all URLs to the user's shown set and sets TTL. Use after returning content to client.
func (r *DedupRepository) MarkShownBatch(ctx context.Context, userID string, urls []string) error {
	if len(urls) == 0 {
		return nil
	}
	key := shownKey(userID)
	members := make([]interface{}, len(urls))
	for i, u := range urls {
		members[i] = u
	}
	if err := r.client.Client.SAdd(ctx, key, members...).Err(); err != nil {
		return err
	}
	return r.client.Client.Expire(ctx, key, ttlShown).Err()
}

// WasShown checks if a URL was already shown for a user.
func (r *DedupRepository) WasShown(ctx context.Context, userID, url string) (bool, error) {
	res, err := r.client.Client.SIsMember(ctx, shownKey(userID), url).Result()
	if err != nil {
		return false, err
	}
	return res, nil
}

