package redisrepo

import (
	"github.com/garvishtayal/dis-connect/go-service/internal/config"
	"github.com/redis/go-redis/v9"
)

// Client wraps a Redis client.
type Client struct {
	Client *redis.Client
}

// NewClient creates a Redis client from app config.
func NewClient(cfg *config.AppConfig) *Client {
	return &Client{
		Client: config.NewRedisClient(cfg),
	}
}

