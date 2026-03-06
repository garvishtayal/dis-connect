package service

import (
	"context"

	"github.com/google/uuid"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
)

// UserService handles user creation and profile updates.
type UserService struct{}

// NewUserService creates a new UserService.
func NewUserService() *UserService {
	return &UserService{}
}

// CreateUser creates a new user and derives an initial soul.
func (s *UserService) CreateUser(ctx context.Context, req models.CreateUserRequest) (*models.CreateUserResponse, error) {
	userID := uuid.NewString()

	soul := req.InitialPrompt
	if soul == "" {
		soul = "Manifest your next big role"
	}

	return &models.CreateUserResponse{
		UserID: userID,
		Soul:   soul,
	}, nil
}
