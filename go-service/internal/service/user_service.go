package service

import (
	"context"
	"fmt"
	"strings"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
)

// UserService handles user creation and profile updates.
type UserService struct {
	userRepo *postgres.UserRepository
}

// NewUserService creates a new UserService.
func NewUserService(userRepo *postgres.UserRepository) *UserService {
	return &UserService{userRepo: userRepo}
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

	userID, err := s.userRepo.SetInitialPromptByFirebaseUID(ctx, firebaseUID, soul)
	if err != nil {
		return nil, err
	}

	return &models.CreateUserResponse{
		UserID:              userID,
		Soul:                soul,
		OnboardingCompleted: true,
	}, nil
}
