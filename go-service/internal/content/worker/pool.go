// Package worker implements platform-specific scrape worker pools.
//
// YouTube pool: high concurrency (5 workers), no inter-request delay.
// Pinterest pool: low concurrency (2 workers), 1.5 s delay between requests
// to avoid rate-limiting. Each Pinterest worker is sequential — it finishes
// one job before picking up the next.
package worker

import (
	"context"
	"log"
	"time"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/content/queue"
	redisrepo "github.com/garvishtayal/dis-connect/go-service/internal/repository/redis"
	"github.com/garvishtayal/dis-connect/go-service/internal/content/scraper"
)

const (
	youTubeConcurrency   = 5
	pinterestConcurrency = 2
	pinterestDelay       = 1500 * time.Millisecond
	popTimeout           = 2 * time.Second
)

// Pool is a generic worker pool that consumes scrape jobs from a Redis queue.
type Pool struct {
	name        string
	queueName   string
	concurrency int
	delay       time.Duration // inter-request delay (0 = none)
	proxy       string        // static proxy URL for all jobs in this pool (empty = no proxy)
	queue       *queue.RedisQueue
	scraper     *scraper.Client
	stateRepo   *redisrepo.RequestStateRepository
	cacheRepo   *redisrepo.SearchCacheRepository
}

// StartYouTubePool launches 5 goroutines consuming from queue:youtube.
func StartYouTubePool(
	ctx context.Context,
	q *queue.RedisQueue,
	sc *scraper.Client,
	stateRepo *redisrepo.RequestStateRepository,
	cacheRepo *redisrepo.SearchCacheRepository,
) {
	p := &Pool{
		name:        "youtube",
		queueName:   queue.QueueYouTube,
		concurrency: youTubeConcurrency,
		delay:       0,
		queue:       q,
		scraper:     sc,
		stateRepo:   stateRepo,
		cacheRepo:   cacheRepo,
	}
	p.start(ctx)
}

// StartPinterestPool launches 2 sequential goroutines consuming from queue:pinterest.
// proxy is an optional proxy URL; pass "" to scrape without a proxy.
func StartPinterestPool(
	ctx context.Context,
	q *queue.RedisQueue,
	sc *scraper.Client,
	stateRepo *redisrepo.RequestStateRepository,
	cacheRepo *redisrepo.SearchCacheRepository,
	proxy string,
) {
	p := &Pool{
		name:        "pinterest",
		queueName:   queue.QueuePinterest,
		concurrency: pinterestConcurrency,
		delay:       pinterestDelay,
		proxy:       proxy,
		queue:       q,
		scraper:     sc,
		stateRepo:   stateRepo,
		cacheRepo:   cacheRepo,
	}
	p.start(ctx)
}

func (p *Pool) start(ctx context.Context) {
	for i := range p.concurrency {
		go p.runWorker(ctx, i)
	}
	log.Printf("[worker:%s] started %d workers", p.name, p.concurrency)
}

// runWorker loops: pop one job → process it → optional delay → repeat.
// Exits when ctx is cancelled.
func (p *Pool) runWorker(ctx context.Context, id int) {
	for {
		select {
		case <-ctx.Done():
			return
		default:
		}

		job, err := p.queue.Pop(ctx, p.queueName, popTimeout)
		if err != nil {
			log.Printf("[worker:%s#%d] pop error: %v", p.name, id, err)
			continue
		}
		if job == nil {
			continue // timeout — no job available, loop back
		}

		p.processJob(ctx, *job)

		if p.delay > 0 {
			select {
			case <-time.After(p.delay):
			case <-ctx.Done():
				return
			}
		}
	}
}

// processJob calls the appropriate Python scraper, stores results, and updates request state.
func (p *Pool) processJob(ctx context.Context, job queue.ScrapeJob) {
	proxy := job.Proxy
	if proxy == "" {
		proxy = p.proxy
	}

	var items []models.ContentItem
	var err error

	switch job.Platform {
	case "youtube":
		items, err = p.scraper.ScrapeYouTube(ctx, job.Query)
	case "pinterest":
		items, err = p.scraper.ScrapePinterest(ctx, job.Query, proxy)
	default:
		log.Printf("[worker:%s] unknown platform %q — skipping job", p.name, job.Platform)
		p.completeDone(ctx, job.RequestID)
		return
	}

	if err != nil {
		log.Printf("[worker:%s] scrape failed (req=%s platform=%s query=%q): %v",
			p.name, job.RequestID, job.Platform, job.Query, err)
	} else if len(items) > 0 {
		// Persist in search cache so the next request is a cache hit.
		_ = p.cacheRepo.Set(ctx, job.Platform, job.Query, items)
		// Append to this request's result list.
		if err := p.stateRepo.AppendResults(ctx, job.RequestID, items); err != nil {
			log.Printf("[worker:%s] append results error (req=%s): %v", p.name, job.RequestID, err)
		}
	}

	p.completeDone(ctx, job.RequestID)
}

func (p *Pool) completeDone(ctx context.Context, requestID string) {
	if _, err := p.stateRepo.IncrDone(ctx, requestID); err != nil {
		log.Printf("[worker:%s] incr done error (req=%s): %v", p.name, requestID, err)
	}
}
