package service

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"time"

	"github.com/garvishtayal/dis-connect/go-service/internal/agent"
	"github.com/garvishtayal/dis-connect/go-service/internal/content/aggregator"
	"github.com/garvishtayal/dis-connect/go-service/internal/content/mixer"
	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/content/queue"
	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
	redisrepo "github.com/garvishtayal/dis-connect/go-service/internal/repository/redis"
)

const (
	aggregatorTimeout = 8 * time.Second
	defaultLimit      = 20
)

// ErrContentLimit is returned when the daily content quota is exceeded.
var ErrContentLimit = errors.New("content daily limit reached")

// ContentService orchestrates the content feed:
// LLM queries → cache check → queue dispatch → aggregation → mix/rank/dedup → response.
type ContentService struct {
	agent         *agent.Client
	userRepo      *postgres.UserRepository
	dedupRepo     *redisrepo.DedupRepository
	rateLimitRepo *redisrepo.RateLimitRepository
	queue         *queue.RedisQueue
	cacheRepo     *redisrepo.SearchCacheRepository
	stateRepo     *redisrepo.RequestStateRepository
	agg           *aggregator.Aggregator
}

func NewContentService(
	agentClient *agent.Client,
	userRepo *postgres.UserRepository,
	dedupRepo *redisrepo.DedupRepository,
	rateLimitRepo *redisrepo.RateLimitRepository,
	q *queue.RedisQueue,
	cacheRepo *redisrepo.SearchCacheRepository,
	stateRepo *redisrepo.RequestStateRepository,
	agg *aggregator.Aggregator,
) *ContentService {
	return &ContentService{
		agent:         agentClient,
		userRepo:      userRepo,
		dedupRepo:     dedupRepo,
		rateLimitRepo: rateLimitRepo,
		queue:         q,
		cacheRepo:     cacheRepo,
		stateRepo:     stateRepo,
		agg:           agg,
	}
}

// GetContent is the main entry point for the content feed.
func (s *ContentService) GetContent(ctx context.Context, req models.ContentRequest) ([]models.ContentItem, error) {
	userID, err := resolveInternalUserID(ctx, s.userRepo, req.UserID)
	if err != nil {
		return nil, fmt.Errorf("resolve user id: %w", err)
	}

	if s.rateLimitRepo != nil {
		key := fmt.Sprintf("rl:content:%s:%s", userID, time.Now().UTC().Format("2006-01-02"))
		ok, _, err := s.rateLimitRepo.AllowDaily(ctx, key, 10)
		if err != nil {
			return nil, fmt.Errorf("content rate limit: %w", err)
		}
		if !ok {
			return nil, ErrContentLimit
		}
	}

	profile, err := s.userRepo.GetContentProfileByUserID(ctx, userID)
	if err != nil {
		return nil, fmt.Errorf("get user profile: %w", err)
	}
	if profile == nil {
		return nil, fmt.Errorf("user not found")
	}

	limit := req.Limit
	if limit <= 0 {
		limit = defaultLimit
	}

	// 1. LLM generates platform queries (Python, no scraping).
	queries, err := s.agent.GenerateQueries(ctx, agent.GenerateQueriesRequest{
		UserID:          userID,
		InitialPrompt:   profile.InitialPrompt,
		EnhancedProfile: profile.EnhancedProfile,
		Preferences:     profile.Preferences,
	})
	if err != nil {
		return nil, fmt.Errorf("generate queries: %w", err)
	}

	// 2. Cache check — serve hits immediately, queue misses for scraping.
	requestID := newRequestID()
	var cachedItems []models.ContentItem
	var pendingJobs []queue.ScrapeJob

	for _, q := range queries {
		if items, hit, _ := s.cacheRepo.Get(ctx, q.Platform, q.Query); hit {
			cachedItems = append(cachedItems, items...)
		} else {
			pendingJobs = append(pendingJobs, queue.ScrapeJob{
				RequestID: requestID,
				Platform:  q.Platform,
				Query:     q.Query,
			})
		}
	}

	// 3. Dispatch uncached jobs to worker queues and wait for results.
	var scraped []models.ContentItem
	if len(pendingJobs) > 0 {
		if err := s.stateRepo.Init(ctx, requestID, len(pendingJobs)); err != nil {
			return nil, fmt.Errorf("init request state: %w", err)
		}
		for _, job := range pendingJobs {
			queueName := queue.QueueYouTube
			if job.Platform == "pinterest" {
				queueName = queue.QueuePinterest
			}
			if err := s.queue.Push(ctx, queueName, job); err != nil {
				return nil, fmt.Errorf("push job to queue: %w", err)
			}
		}
		scraped, _ = s.agg.Wait(ctx, requestID, len(pendingJobs), aggregatorTimeout)
	}

	// 4. Load shown URLs for cross-request dedup (degrade gracefully on error).
	var shownURLs map[string]struct{}
	if s.dedupRepo != nil {
		shownURLs, _ = s.dedupRepo.GetShownURLs(ctx, userID)
	}

	// 5. Mix, rank, dedup → final result.
	all := append(cachedItems, scraped...)
	items := mixer.Mix(all, shownURLs, limit)

	// 6. Persist shown URLs so future requests skip them.
	if s.dedupRepo != nil {
		urls := make([]string, 0, len(items))
		for _, it := range items {
			if it.URL != "" {
				urls = append(urls, it.URL)
			}
		}
		_ = s.dedupRepo.MarkShownBatch(ctx, userID, urls)
	}

	return items, nil
}

func newRequestID() string {
	b := make([]byte, 8)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}
