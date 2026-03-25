// Package aggregator polls Redis until all scrape jobs for a request are complete,
// then collects and returns the results. Returns whatever is available on timeout.
package aggregator

import (
	"context"
	"time"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	redisrepo "github.com/garvishtayal/dis-connect/go-service/internal/repository/redis"
)

const pollInterval = 300 * time.Millisecond

// Aggregator waits for all workers to finish a request and collects results.
type Aggregator struct {
	stateRepo *redisrepo.RequestStateRepository
}

func New(stateRepo *redisrepo.RequestStateRepository) *Aggregator {
	return &Aggregator{stateRepo: stateRepo}
}

// Wait blocks until all totalJobs are done OR timeout elapses.
// On timeout it returns whatever partial results are available — never an error.
func (a *Aggregator) Wait(ctx context.Context, requestID string, totalJobs int, timeout time.Duration) ([]models.ContentItem, error) {
	if totalJobs == 0 {
		return nil, nil
	}

	deadline := time.Now().Add(timeout)
	ticker := time.NewTicker(pollInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			done, _, err := a.stateRepo.GetProgress(ctx, requestID)
			if err != nil || done >= totalJobs || time.Now().After(deadline) {
				return a.stateRepo.GetResults(ctx, requestID)
			}
		case <-ctx.Done():
			return a.stateRepo.GetResults(ctx, requestID)
		}
	}
}
