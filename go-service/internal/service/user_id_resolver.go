package service

import (
	"context"
	"fmt"
	"regexp"

	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
)

var uuidRegex = regexp.MustCompile(`^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$`)

// resolveInternalUserID normalizes incoming user id values:
// - if already a UUID (internal users.id), return as-is
// - otherwise treat it as Firebase UID and map to internal users.id
func resolveInternalUserID(ctx context.Context, userRepo *postgres.UserRepository, rawUserID string) (string, error) {
	if rawUserID == "" {
		return "", fmt.Errorf("user id is required")
	}
	if uuidRegex.MatchString(rawUserID) {
		return rawUserID, nil
	}
	if userRepo == nil {
		return "", fmt.Errorf("user repository is not configured")
	}

	userID, err := userRepo.GetUserIDByFirebaseUID(ctx, rawUserID)
	if err != nil {
		return "", fmt.Errorf("resolve firebase uid: %w", err)
	}
	if userID == "" {
		return "", fmt.Errorf("user not found")
	}
	return userID, nil
}

