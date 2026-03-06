package models

// ChatMessage represents a single chat message.
type ChatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// ChatRequest is the payload for POST /api/chat.
type ChatRequest struct {
	UserID  string `json:"user_id" binding:"required"`
	Message string `json:"message" binding:"required"`
}

// ChatResponse represents chat + optional content.
type ChatResponse struct {
	ChatResponse     string        `json:"chat_response"`
	NeedsNewContent  bool          `json:"needs_new_content"`
	NewContent       []ContentItem `json:"new_content,omitempty"`
	ManifestationTip string        `json:"manifestation_tip,omitempty"`
}

