package redisrepo

import (
	"context"
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
)

const (
	reqTotalFmt   = "req:%s:total"
	reqDoneFmt    = "req:%s:done"
	reqResultsFmt = "req:%s:results"
	reqTTL        = 5 * time.Minute
)

// RequestStateRepository tracks per-request scrape progress and collects results.
// Keys are req:{id}:total, req:{id}:done, req:{id}:results — all expire after 5 minutes.
type RequestStateRepository struct {
	client *Client
}

func NewRequestStateRepository(client *Client) *RequestStateRepository {
	return &RequestStateRepository{client: client}
}

// Init sets the total job count for a request. Must be called before pushing jobs to the queue.
func (r *RequestStateRepository) Init(ctx context.Context, requestID string, total int) error {
	totalKey := fmt.Sprintf(reqTotalFmt, requestID)
	doneKey := fmt.Sprintf(reqDoneFmt, requestID)

	pipe := r.client.Client.TxPipeline()
	pipe.Set(ctx, totalKey, total, reqTTL)
	pipe.Set(ctx, doneKey, 0, reqTTL)
	_, err := pipe.Exec(ctx)
	return err
}

// IncrDone increments the completed-job counter. Returns the new count.
func (r *RequestStateRepository) IncrDone(ctx context.Context, requestID string) (int, error) {
	doneKey := fmt.Sprintf(reqDoneFmt, requestID)
	n, err := r.client.Client.Incr(ctx, doneKey).Result()
	if err != nil {
		return 0, err
	}
	r.client.Client.Expire(ctx, doneKey, reqTTL)
	return int(n), nil
}

// AppendResults pushes a batch of content items onto the results list for this request.
func (r *RequestStateRepository) AppendResults(ctx context.Context, requestID string, items []models.ContentItem) error {
	if len(items) == 0 {
		return nil
	}
	b, err := json.Marshal(items)
	if err != nil {
		return fmt.Errorf("marshal results: %w", err)
	}
	resultsKey := fmt.Sprintf(reqResultsFmt, requestID)
	pipe := r.client.Client.TxPipeline()
	pipe.LPush(ctx, resultsKey, b)
	pipe.Expire(ctx, resultsKey, reqTTL)
	_, err = pipe.Exec(ctx)
	return err
}

// GetProgress returns (done, total) for a request.
func (r *RequestStateRepository) GetProgress(ctx context.Context, requestID string) (done, total int, err error) {
	totalKey := fmt.Sprintf(reqTotalFmt, requestID)
	doneKey := fmt.Sprintf(reqDoneFmt, requestID)

	vals, err := r.client.Client.MGet(ctx, totalKey, doneKey).Result()
	if err != nil {
		return 0, 0, err
	}

	total = toInt(vals[0])
	done = toInt(vals[1])
	return done, total, nil
}

// GetResults collects all result batches and flattens them into a single slice.
func (r *RequestStateRepository) GetResults(ctx context.Context, requestID string) ([]models.ContentItem, error) {
	resultsKey := fmt.Sprintf(reqResultsFmt, requestID)
	batches, err := r.client.Client.LRange(ctx, resultsKey, 0, -1).Result()
	if err != nil {
		return nil, err
	}

	var all []models.ContentItem
	for _, batch := range batches {
		var items []models.ContentItem
		if err := json.Unmarshal([]byte(batch), &items); err != nil {
			continue
		}
		all = append(all, items...)
	}
	return all, nil
}

func toInt(v any) int {
	if v == nil {
		return 0
	}
	s, ok := v.(string)
	if !ok {
		return 0
	}
	n, _ := strconv.Atoi(s)
	return n
}
