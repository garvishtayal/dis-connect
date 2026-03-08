package service

import (
	"context"
	"fmt"

	"github.com/garvishtayal/dis-connect/go-service/internal/agent"
	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
)

// ContentService handles content fetching by calling the Python agent generate-content API.
type ContentService struct {
	agent    *agent.Client
	userRepo *postgres.UserRepository
}

// NewContentService creates a new ContentService.
func NewContentService(agentClient *agent.Client, userRepo *postgres.UserRepository) *ContentService {
	return &ContentService{
		agent:    agentClient,
		userRepo: userRepo,
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

	// Apply offset client-side (Python API supports limit only).
	if req.Offset > 0 && len(items) > req.Offset {
		items = items[req.Offset:]
	} else if req.Offset > 0 {
		items = []models.ContentItem{}
	}

	return items, nil
}
