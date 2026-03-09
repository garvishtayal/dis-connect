package service

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/garvishtayal/dis-connect/go-service/internal/agent"
	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
	redisrepo "github.com/garvishtayal/dis-connect/go-service/internal/repository/redis"
)

// ContentService handles content fetching by calling the Python agent generate-content API.
type ContentService struct {
	agent         *agent.Client
	userRepo      *postgres.UserRepository
	dedupRepo     *redisrepo.DedupRepository
	rateLimitRepo *redisrepo.RateLimitRepository
}

// ErrContentLimit is returned when daily content quota is exceeded.
var ErrContentLimit = errors.New("content daily limit reached")

// NewContentService creates a new ContentService.
func NewContentService(
	agentClient *agent.Client,
	userRepo *postgres.UserRepository,
	dedupRepo *redisrepo.DedupRepository,
	rateLimitRepo *redisrepo.RateLimitRepository,
) *ContentService {
	return &ContentService{
		agent:         agentClient,
		userRepo:      userRepo,
		dedupRepo:     dedupRepo,
		rateLimitRepo: rateLimitRepo,
	}
}

// GetContent returns a list of content items for the feed by calling the Python agent /agent/generate-content.
func (s *ContentService) GetContent(ctx context.Context, req models.ContentRequest) ([]models.ContentItem, error) {
	if s.agent == nil {
		return nil, fmt.Errorf("agent client is not configured")
	}
	if s.userRepo == nil {
		return nil, fmt.Errorf("user repository is not configured")
	}

	// Enforce daily per-user content quota (shared with chat).
	if s.rateLimitRepo != nil {
		key := fmt.Sprintf("rl:content:%s:%s", req.UserID, time.Now().UTC().Format("2006-01-02"))
		ok, _, err := s.rateLimitRepo.AllowDaily(ctx, key, 10)
		if err != nil {
			return nil, fmt.Errorf("content rate limit: %w", err)
		}
		if !ok {
			return nil, ErrContentLimit
		}
	}

	profile, err := s.userRepo.GetContentProfileByUserID(ctx, req.UserID)
	if err != nil {
		return nil, fmt.Errorf("get user profile: %w", err)
	}
	if profile == nil {
		return nil, fmt.Errorf("user not found")
	}

	limit := req.Limit
	if limit <= 0 {
		limit = 20
	}

	agentReq := agent.GenerateContentRequest{
		UserID:          req.UserID,
		InitialPrompt:   profile.InitialPrompt,
		EnhancedProfile: profile.EnhancedProfile,
		Preferences:     profile.Preferences,
		RecentChats:     nil,
		Limit:           limit,
	}

	resp, err := s.agent.GenerateContent(ctx, agentReq)
	if err != nil {
		return nil, fmt.Errorf("agent generate-content: %w", err)
	}

	items := resp.Items
	if resp.Items == nil {
		items = []models.ContentItem{}
	}

	// Mark shown in Redis (user:{id}:shown SET of URLs). Python get_shown_urls() reads this for dedup.
	if s.dedupRepo != nil {
		urls := make([]string, 0, len(items))
		for _, it := range items {
			if it.URL != "" {
				urls = append(urls, it.URL)
			}
		}
		_ = s.dedupRepo.MarkShownBatch(ctx, req.UserID, urls)
	}

	// Apply offset client-side (Python API supports limit only).
	if req.Offset > 0 && len(items) > req.Offset {
		items = items[req.Offset:]
	} else if req.Offset > 0 {
		items = []models.ContentItem{}
	}

	return items, nil
}
