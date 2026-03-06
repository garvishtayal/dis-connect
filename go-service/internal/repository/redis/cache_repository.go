package redisrepo

import (
	"context"
	"time"

	"github.com/redis/go-redis/v9"
)

// CacheRepository stores short-lived cached payloads.
type CacheRepository struct {
	client *Client
}

// NewCacheRepository creates a CacheRepository.
func NewCacheRepository(client *Client) *CacheRepository {
	return &CacheRepository{client: client}
}

// Set stores a value with a TTL.
func (r *CacheRepository) Set(ctx context.Context, key string, value string, ttl time.Duration) error {
	return r.client.Client.Set(ctx, key, value, ttl).Err()
}

// Get retrieves a cached value if present.
func (r *CacheRepository) Get(ctx context.Context, key string) (string, bool, error) {
	res, err := r.client.Client.Get(ctx, key).Result()
	if err != nil {
		if err == redis.Nil {
			return "", false, nil
		}
		return "", false, err
	}
	return res, true, nil
}

