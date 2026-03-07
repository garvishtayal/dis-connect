package models

// ContentItem represents a single content card.
type ContentItem struct {
	ID       string         `json:"id"`
	Type     string         `json:"type"`
	Platform string         `json:"platform"`
	URL      string         `json:"url"`
	Title    string         `json:"title"`
	Score    float64        `json:"score,omitempty"`
	Metadata map[string]any `json:"metadata,omitempty"`
}

// ContentRequest is the payload for GET /api/content.
type ContentRequest struct {
	UserID string `form:"user_id" binding:"required"`
	Limit  int    `form:"limit"`
	Offset int    `form:"offset"`
}
