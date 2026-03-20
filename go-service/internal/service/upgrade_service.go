package service

import (
	"context"
	"fmt"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
)

// UpgradeService handles upgrade record operations.
type UpgradeService struct {
	upgradeRepo *postgres.UpgradeRepository
	userRepo    *postgres.UserRepository
}

// NewUpgradeService creates an UpgradeService.
func NewUpgradeService(upgradeRepo *postgres.UpgradeRepository, userRepo *postgres.UserRepository) *UpgradeService {
	return &UpgradeService{upgradeRepo: upgradeRepo, userRepo: userRepo}
}

// Upsert stores (or updates) the upgrade record for a user.
func (s *UpgradeService) Upsert(ctx context.Context, req models.UpsertUpgradeRequest) (*models.UpgradeRecord, error) {
	userID, err := resolveInternalUserID(ctx, s.userRepo, req.UserID)
	if err != nil {
		return nil, fmt.Errorf("resolve user: %w", err)
	}

	if err := s.upgradeRepo.Upsert(ctx, userID, req.Upgraded, req.Feedback, req.WillingToPay); err != nil {
		return nil, fmt.Errorf("upsert upgrade: %w", err)
	}

	return &models.UpgradeRecord{
		UserID:       userID,
		Upgraded:     req.Upgraded,
		Feedback:     req.Feedback,
		WillingToPay: req.WillingToPay,
	}, nil
}

// Get returns the upgrade record for a user, or nil if none exists yet.
func (s *UpgradeService) Get(ctx context.Context, userID string) (*models.UpgradeRecord, error) {
	resolvedID, err := resolveInternalUserID(ctx, s.userRepo, userID)
	if err != nil {
		return nil, fmt.Errorf("resolve user: %w", err)
	}

	rec, err := s.upgradeRepo.Get(ctx, resolvedID)
	if err != nil {
		return nil, fmt.Errorf("get upgrade: %w", err)
	}
	return rec, nil
}
