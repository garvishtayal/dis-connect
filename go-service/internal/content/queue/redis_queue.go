package queue

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

const (
	QueueYouTube   = "queue:youtube"
	QueuePinterest = "queue:pinterest"
)

// RedisQueue is a simple FIFO job queue backed by Redis lists.
// Push uses LPUSH; Pop uses BRPOP so workers block until a job arrives.
type RedisQueue struct {
	client *redis.Client
}

func NewRedisQueue(client *redis.Client) *RedisQueue {
	return &RedisQueue{client: client}
}

// Push enqueues a job onto the named queue.
func (q *RedisQueue) Push(ctx context.Context, queueName string, job ScrapeJob) error {
	b, err := json.Marshal(job)
	if err != nil {
		return fmt.Errorf("marshal job: %w", err)
	}
	return q.client.LPush(ctx, queueName, b).Err()
}

// Pop blocks until a job is available or timeout elapses.
// Returns nil, nil on timeout (no job available).
func (q *RedisQueue) Pop(ctx context.Context, queueName string, timeout time.Duration) (*ScrapeJob, error) {
	result, err := q.client.BRPop(ctx, timeout, queueName).Result()
	if err == redis.Nil {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("brpop %s: %w", queueName, err)
	}
	// BRPop returns [queueName, value]
	if len(result) < 2 {
		return nil, nil
	}
	var job ScrapeJob
	if err := json.Unmarshal([]byte(result[1]), &job); err != nil {
		return nil, fmt.Errorf("unmarshal job: %w", err)
	}
	return &job, nil
}
