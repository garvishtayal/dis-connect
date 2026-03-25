package redisrepo

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"time"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
)

const (
	searchCacheKeyFmt = "search:%s"
	searchCacheTTL    = 1 * time.Hour
)

// SearchCacheRepository caches raw scrape results per (platform, query).
// Key format matches Python: search:{sha256("platform:query:")[:16 hex chars]}.
type SearchCacheRepository struct {
	client *Client
}

func NewSearchCacheRepository(client *Client) *SearchCacheRepository {
	return &SearchCacheRepository{client: client}
}

// Get returns cached items for (platform, query). Returns (nil, false, nil) on a cache miss.
func (r *SearchCacheRepository) Get(ctx context.Context, platform, query string) ([]models.ContentItem, bool, error) {
	key := searchCacheKey(platform, query)
	data, err := r.client.Client.Get(ctx, key).Result()
	if err != nil {
		// redis.Nil is a cache miss — not an error for the caller
		return nil, false, nil
	}
	var items []models.ContentItem
	if err := json.Unmarshal([]byte(data), &items); err != nil {
		return nil, false, nil
	}
	return items, true, nil
}

// Set stores items in the cache with a 1-hour TTL.
func (r *SearchCacheRepository) Set(ctx context.Context, platform, query string, items []models.ContentItem) error {
	if len(items) == 0 {
		return nil
	}
	b, err := json.Marshal(items)
	if err != nil {
		return fmt.Errorf("marshal cache items: %w", err)
	}
	return r.client.Client.Set(ctx, searchCacheKey(platform, query), b, searchCacheTTL).Err()
}

// searchCacheKey mirrors Python's _search_hash:
//
//	sha256(f"{platform}:{query}:".encode()).hexdigest()[:16]
func searchCacheKey(platform, query string) string {
	raw := fmt.Sprintf("%s:%s:", platform, query)
	h := sha256.Sum256([]byte(raw))
	return fmt.Sprintf(searchCacheKeyFmt, fmt.Sprintf("%x", h[:8]))
}
