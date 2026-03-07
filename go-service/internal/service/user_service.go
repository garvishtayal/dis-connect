package service

import (
	"context"
	"fmt"
	"strings"

	"github.com/garvishtayal/dis-connect/go-service/internal/agent"
	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
)

// UserService handles user creation and profile updates.
type UserService struct {
	userRepo *postgres.UserRepository
	agent    *agent.Client
}

// NewUserService creates a new UserService.
func NewUserService(userRepo *postgres.UserRepository, agentClient *agent.Client) *UserService {
	return &UserService{userRepo: userRepo, agent: agentClient}
}

// CreateUser creates a new user and derives an initial soul.
func (s *UserService) CreateUser(ctx context.Context, firebaseUID string, req models.CreateUserRequest) (*models.CreateUserResponse, error) {
	if s.userRepo == nil {
		return nil, fmt.Errorf("user repository is not configured")
	}

	soul := strings.TrimSpace(req.InitialPrompt)
	if soul == "" {
		return nil, fmt.Errorf("initial prompt is required")
	}

	enhancedProfile := soul
	if s.agent != nil {
		// Derive enhanced profile from the initial prompt via Python agent.
		soulResp, err := s.agent.UnderstandSoul(ctx, agent.UnderstandSoulRequest{
			UserID:        firebaseUID,
			InitialPrompt: soul,
			RecentChats:   []any{},
		})
		if err != nil {
			return nil, fmt.Errorf("understand soul: %w", err)
		}
		if strings.TrimSpace(soulResp.Soul) != "" {
			enhancedProfile = strings.TrimSpace(soulResp.Soul)
		}
	}

	userID, err := s.userRepo.SetInitialPromptByFirebaseUID(ctx, firebaseUID, soul, enhancedProfile)
	if err != nil {
		return nil, err
	}

	return &models.CreateUserResponse{
		UserID:              userID,
		Soul:                enhancedProfile,
		OnboardingCompleted: true,
	}, nil
}
