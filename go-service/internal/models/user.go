package models

// User represents a basic user profile.
type User struct {
	ID                  string `json:"id"`
	FirebaseUID         string `json:"firebase_uid,omitempty"`
	Email               string `json:"email,omitempty"`
	DisplayName         string `json:"display_name,omitempty"`
	PhotoURL            string `json:"photo_url,omitempty"`
	Provider            string `json:"provider,omitempty"`
	InitialPrompt       string `json:"initial_prompt"`
	OnboardingCompleted bool   `json:"onboarding_completed"`
	Soul                string `json:"soul,omitempty"`
}

// CreateUserRequest is the payload for creating a user.
type CreateUserRequest struct {
	InitialPrompt string `json:"initial_prompt" binding:"required"`
}

// CreateUserResponse is returned after user creation.
type CreateUserResponse struct {
	UserID              string `json:"user_id"`
	Soul                string `json:"soul"`
	OnboardingCompleted bool   `json:"onboarding_completed"`
}
