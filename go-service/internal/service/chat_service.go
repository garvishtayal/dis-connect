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

// ChatService handles chat flows via the Python agent and content service.
type ChatService struct {
	agent              *agent.Client
	contentService     *ContentService
	userRepo           *postgres.UserRepository
	chatRepo           *postgres.ChatRepository
	preferenceRepo     *postgres.PreferenceRepository
	preferencesEnabled bool
	rateLimitRepo      *redisrepo.RateLimitRepository
}

// ErrChatLimit is returned when daily chat quota is exceeded.
var ErrChatLimit = errors.New("chat daily limit reached")

// NewChatService creates a new ChatService.
func NewChatService(agentClient *agent.Client, contentService *ContentService, userRepo *postgres.UserRepository, chatRepo *postgres.ChatRepository, preferenceRepo *postgres.PreferenceRepository, rateLimitRepo *redisrepo.RateLimitRepository) *ChatService {
	return &ChatService{
		agent:              agentClient,
		contentService:     contentService,
		userRepo:           userRepo,
		chatRepo:           chatRepo,
		preferenceRepo:     preferenceRepo,
		rateLimitRepo:      rateLimitRepo,
		preferencesEnabled: chatRepo != nil && preferenceRepo != nil,
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

	// Enforce daily per-user chat quota.
	if s.rateLimitRepo != nil {
		key := fmt.Sprintf("rl:chat:%s:%s", req.UserID, time.Now().UTC().Format("2006-01-02"))
		ok, _, err := s.rateLimitRepo.AllowDaily(ctx, key, 20)
		if err != nil {
			return nil, fmt.Errorf("chat rate limit: %w", err)
		}
		if !ok {
			return nil, ErrChatLimit
		}
	}

	// Load user profile once so chat has the same context as content.
	profile, err := s.userRepo.GetContentProfileByUserID(ctx, req.UserID)
	if err != nil {
		return nil, fmt.Errorf("get user profile: %w", err)
	}
	if profile == nil {
		return nil, fmt.Errorf("user not found")
	}

	// Optional: load last few chats so chat has context.
	var recentChats []any
	if s.chatRepo != nil {
		msgs, err := s.chatRepo.ListMessages(ctx, req.UserID, 5)
		if err == nil {
			for _, m := range msgs {
				recentChats = append(recentChats, map[string]any{
					"role":    m.Role,
					"content": m.Content,
				})
			}
		}
	}

	agentReq := agent.ChatRequest{
		UserID:          req.UserID,
		Message:         req.Message,
		InitialPrompt:   profile.InitialPrompt,
		EnhancedProfile: profile.EnhancedProfile,
		Preferences:     profile.Preferences,
		RecentChats:     recentChats,
	}

	agentResp, err := s.agent.Chat(ctx, agentReq)
	if err != nil {
		return nil, fmt.Errorf("agent chat: %w", err)
	}

	result := &models.ChatResponse{
		ChatResponse:    agentResp.ChatResponse,
		NeedsNewContent: agentResp.NeedsNewContent,
	}

	// Store the user and agent messages for history/counting. Ignore errors to keep chat responsive.
	if s.chatRepo != nil {
		_ = s.chatRepo.SaveMessage(ctx, req.UserID, "user", req.Message)
		_ = s.chatRepo.SaveMessage(ctx, req.UserID, "agent", agentResp.ChatResponse)
	}

	// After every 5th user chat, trigger a background preferences update.
	if s.preferencesEnabled && s.chatRepo != nil {
		if count, err := s.chatRepo.CountMessages(ctx, req.UserID); err == nil && count > 0 && count%5 == 0 {
			go s.updatePreferencesInBackground(req.UserID, profile.Preferences)
		}
	}

	if !agentResp.NeedsNewContent || s.contentService == nil {
		return result, nil
	}

	// Enforce shared daily content quota for chat-triggered content.
	if s.rateLimitRepo != nil {
		key := fmt.Sprintf("rl:content:%s:%s", req.UserID, time.Now().UTC().Format("2006-01-02"))
		ok, _, err := s.rateLimitRepo.AllowDaily(ctx, key, 10)
		if err != nil {
			return result, nil
		}
		if !ok {
			result.NeedsNewContent = false
			return result, nil
		}
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

// updatePreferencesInBackground calls the Python preferences endpoint and persists
// any updated preferences without blocking the main chat request.
func (s *ChatService) updatePreferencesInBackground(userID string, currentPrefs map[string]any) {
	if s.agent == nil || s.chatRepo == nil || s.preferenceRepo == nil {
		return
	}

	ctx := context.Background()

	// Reload the last few chats (including the most recent ones) for context.
	msgs, err := s.chatRepo.ListMessages(ctx, userID, 5)
	if err != nil {
		return
	}

	var recentChats []any
	for _, m := range msgs {
		recentChats = append(recentChats, map[string]any{
			"role":    m.Role,
			"content": m.Content,
		})
	}

	prefReq := agent.PreferencesRequest{
		UserID:      userID,
		Preferences: currentPrefs,
		RecentChats: recentChats,
	}

	prefResp, err := s.agent.Preferences(ctx, prefReq)
	if err != nil || prefResp == nil || prefResp.Preferences == nil {
		return
	}

	_ = s.preferenceRepo.UpdatePreferences(ctx, userID, prefResp.Preferences)
}
