package redisrepo

import (
	"context"
	"time"

	"github.com/redis/go-redis/v9"
)

// RateLimitRepository tracks per-key daily usage.
type RateLimitRepository struct {
	client *Client
}

// NewRateLimitRepository creates a RateLimitRepository.
func NewRateLimitRepository(client *Client) *RateLimitRepository {
	return &RateLimitRepository{client: client}
}

// AllowDaily increments usage for key and enforces a daily limit.
func (r *RateLimitRepository) AllowDaily(ctx context.Context, key string, limit int) (bool, int, error) {
	now := time.Now().UTC()
	end := time.Date(now.Year(), now.Month(), now.Day()+1, 0, 0, 0, 0, time.UTC)
	ttl := time.Until(end)

	pipe := r.client.Client.TxPipeline()
	incr := pipe.Incr(ctx, key)
	pipe.Expire(ctx, key, ttl)
	_, err := pipe.Exec(ctx)
	if err != nil && err != redis.Nil {
		return false, 0, err
	}

	n, err := incr.Result()
	if err != nil {
		return false, 0, err
	}
	return int(n) <= limit, int(n), nil
}

