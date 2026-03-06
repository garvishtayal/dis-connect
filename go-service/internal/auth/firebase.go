package auth

import (
	"context"
	"fmt"
	"os"

	firebase "firebase.google.com/go/v4"
	"google.golang.org/api/option"
)

// FirebaseClient wraps the Firebase Auth client.
type FirebaseClient struct {
	auth *firebase.App
}

// NewFirebaseClient creates a Firebase app using a service account file.
func NewFirebaseClient(ctx context.Context) (*FirebaseClient, error) {
	credsPath := os.Getenv("FIREBASE_CREDENTIALS_PATH")
	if credsPath == "" {
		return nil, fmt.Errorf("FIREBASE_CREDENTIALS_PATH is not set")
	}

	opt := option.WithCredentialsFile(credsPath)

	app, err := firebase.NewApp(ctx, nil, opt)
	if err != nil {
		return nil, fmt.Errorf("failed to create firebase app: %w", err)
	}

	return &FirebaseClient{auth: app}, nil
}

