package service

import (
	"context"
	"fmt"
	"strings"

	firebaseauth "firebase.google.com/go/v4/auth"
	"github.com/garvishtayal/dis-connect/go-service/internal/auth"
	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
)

// AuthService handles Gmail and Apple sign-in flows.
type AuthService struct {
	validator *auth.TokenValidator
	userRepo  *postgres.UserRepository
}

// NewAuthService creates a new AuthService.
func NewAuthService(validator *auth.TokenValidator, userRepo *postgres.UserRepository) *AuthService {
	return &AuthService{
		validator: validator,
		userRepo:  userRepo,
	}
}

// SignInWithGoogle verifies a Google ID token and returns a user.
func (s *AuthService) SignInWithGoogle(ctx context.Context, req models.AuthRequest) (*models.AuthResponse, error) {
	return s.signIn(ctx, req, models.AuthProviderGoogle)
}

// SignInWithApple verifies an Apple ID token and returns a user.
func (s *AuthService) SignInWithApple(ctx context.Context, req models.AuthRequest) (*models.AuthResponse, error) {
	return s.signIn(ctx, req, models.AuthProviderApple)
}

// signIn verifies a Firebase ID token and builds an auth response.
func (s *AuthService) signIn(ctx context.Context, req models.AuthRequest, expectedProvider models.AuthProvider) (*models.AuthResponse, error) {
	if s.validator == nil {
		return nil, fmt.Errorf("token validator is not configured")
	}

	token, err := s.validator.VerifyIDToken(ctx, req.IDToken)
	if err != nil {
		return nil, err
	}

	provider := extractSignInProvider(token)
	if !matchesProvider(expectedProvider, provider) {
		return nil, fmt.Errorf("invalid provider: expected %s, got %s", expectedProvider, provider)
	}
	provider = normalizeProvider(expectedProvider, provider)

	if s.userRepo != nil {
		// Persist or update the user row on successful Firebase sign-in.
		initialPrompt := "Manifest your next big role"
		_, err = s.userRepo.UpsertAuthUser(ctx, &models.User{
			FirebaseUID:   token.UID,
			Email:         extractEmail(token),
			DisplayName:   extractDisplayName(token),
			PhotoURL:      extractPhotoURL(token),
			Provider:      provider,
			InitialPrompt: initialPrompt,
		})
		if err != nil {
			return nil, fmt.Errorf("upsert auth user: %w", err)
		}
	}

	return &models.AuthResponse{
		UserID:   token.UID,
		Email:    extractEmail(token),
		Provider: provider,
	}, nil
}

// extractEmail returns email from token claims when present.
func extractEmail(token *firebaseauth.Token) string {
	email, _ := token.Claims["email"].(string)
	return email
}

// extractDisplayName returns display name from token claims when present.
func extractDisplayName(token *firebaseauth.Token) string {
	name, _ := token.Claims["name"].(string)
	return name
}

// extractPhotoURL returns photo URL from token claims when present.
func extractPhotoURL(token *firebaseauth.Token) string {
	picture, _ := token.Claims["picture"].(string)
	return picture
}

// extractSignInProvider returns Firebase sign_in_provider from claims.
func extractSignInProvider(token *firebaseauth.Token) string {
	firebaseClaim, ok := token.Claims["firebase"].(map[string]any)
	if !ok {
		return ""
	}
	provider, _ := firebaseClaim["sign_in_provider"].(string)
	return provider
}

// matchesProvider checks whether Firebase provider aligns with endpoint provider.
func matchesProvider(expected models.AuthProvider, actual string) bool {
	switch expected {
	case models.AuthProviderGoogle:
		return actual == "" || actual == "google.com"
	case models.AuthProviderApple:
		return actual == "" || actual == "apple.com"
	default:
		return strings.EqualFold(string(expected), actual)
	}
}

// normalizeProvider fills provider when Firebase returns an empty sign_in_provider.
func normalizeProvider(expected models.AuthProvider, actual string) string {
	if actual != "" {
		return actual
	}
	switch expected {
	case models.AuthProviderGoogle:
		return "google.com"
	case models.AuthProviderApple:
		return "apple.com"
	default:
		return actual
	}
}
