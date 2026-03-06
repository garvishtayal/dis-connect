package redisrepo

import (
	"context"

	"github.com/redis/go-redis/v9"
)

// PreferenceRepository stores lightweight user preferences.
type PreferenceRepository struct {
	client *Client
}

// NewPreferenceRepository creates a PreferenceRepository.
func NewPreferenceRepository(client *Client) *PreferenceRepository {
	return &PreferenceRepository{client: client}
}

// SetPreferences stores preferences as a JSON string.
func (r *PreferenceRepository) SetPreferences(ctx context.Context, userID string, json string) error {
	key := "prefs:" + userID
	return r.client.Client.Set(ctx, key, json, 0).Err()
}

// GetPreferences returns stored preferences if present.
func (r *PreferenceRepository) GetPreferences(ctx context.Context, userID string) (string, bool, error) {
	key := "prefs:" + userID
	res, err := r.client.Client.Get(ctx, key).Result()
	if err != nil {
		if err == redis.Nil {
			return "", false, nil
		}
		return "", false, err
	}
	return res, true, nil
}

