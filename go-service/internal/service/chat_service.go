package service

import (
	"context"
	"fmt"

	"github.com/garvishtayal/dis-connect/go-service/internal/agent"
	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
)

// ChatService handles chat flows via the Python agent and content service.
type ChatService struct {
	agent          *agent.Client
	contentService *ContentService
	userRepo       *postgres.UserRepository
}

// NewChatService creates a new ChatService.
func NewChatService(agentClient *agent.Client, contentService *ContentService, userRepo *postgres.UserRepository) *ChatService {
	return &ChatService{
		agent:          agentClient,
		contentService: contentService,
		userRepo:       userRepo,
	}
}

// HandleChat calls Python /agent/chat and, when requested, fetches new content.
func (s *ChatService) HandleChat(ctx context.Context, req models.ChatRequest) (*models.ChatResponse, error) {
	if s.agent == nil {
		return nil, fmt.Errorf("agent client is not configured")
	}

	if s.userRepo == nil {
		return nil, fmt.Errorf("user repository is not configured")
	}

	// Load user profile once so chat has the same context as content.
	profile, err := s.userRepo.GetContentProfileByUserID(ctx, req.UserID)
	if err != nil {
		return nil, fmt.Errorf("get user profile: %w", err)
	}
	if profile == nil {
		return nil, fmt.Errorf("user not found")
	}

	agentReq := agent.ChatRequest{
		UserID:          req.UserID,
		Message:         req.Message,
		InitialPrompt:   profile.InitialPrompt,
		EnhancedProfile: profile.EnhancedProfile,
		Preferences:     profile.Preferences,
		RecentChats:     nil,
	}

	agentResp, err := s.agent.Chat(ctx, agentReq)
	if err != nil {
		return nil, fmt.Errorf("agent chat: %w", err)
	}

	result := &models.ChatResponse{
		ChatResponse:    agentResp.ChatResponse,
		NeedsNewContent: agentResp.NeedsNewContent,
	}

	if !agentResp.NeedsNewContent || s.contentService == nil {
		return result, nil
	}

	contentReq := models.ContentRequest{
		UserID: req.UserID,
		Limit:  20,
		Offset: 0,
	}

	items, err := s.contentService.GetContent(ctx, contentReq)
	if err != nil {
		return nil, fmt.Errorf("fetch content: %w", err)
	}

	result.NewContent = items
	return result, nil
}
