package models

// AuthProvider identifies supported auth providers.
type AuthProvider string

const (
	AuthProviderGoogle AuthProvider = "google"
	AuthProviderApple  AuthProvider = "apple"
)

// AuthRequest represents a sign-in request payload.
type AuthRequest struct {
	IDToken  string       `json:"id_token" binding:"required"`
	Provider AuthProvider `json:"-"`
}

// AuthResponse represents a basic authenticated user.
type AuthResponse struct {
	UserID   string `json:"user_id"`
	Email    string `json:"email,omitempty"`
	Provider string `json:"provider,omitempty"`
}
