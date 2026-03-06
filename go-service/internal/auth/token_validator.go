package auth

import (
	"context"
	"fmt"

	fbauth "firebase.google.com/go/v4/auth"
)

// TokenValidator verifies Firebase ID tokens.
type TokenValidator struct {
	client *fbauth.Client
}

// NewTokenValidator creates a validator from a Firebase client.
func NewTokenValidator(ctx context.Context, fb *FirebaseClient) (*TokenValidator, error) {
	authClient, err := fb.auth.Auth(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to create firebase auth client: %w", err)
	}

	return &TokenValidator{client: authClient}, nil
}

// VerifyIDToken validates a token and returns its claims.
func (v *TokenValidator) VerifyIDToken(ctx context.Context, idToken string) (*fbauth.Token, error) {
	if idToken == "" {
		return nil, fmt.Errorf("id token is empty")
	}

	token, err := v.client.VerifyIDToken(ctx, idToken)
	if err != nil {
		return nil, fmt.Errorf("failed to verify id token: %w", err)
	}

	return token, nil
}

