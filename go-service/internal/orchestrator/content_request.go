package orchestrator

import "github.com/garvishtayal/dis-connect/go-service/internal/models"

// FetchContentRequest is sent to Python orchestrator.
type FetchContentRequest struct {
	UserID      string         `json:"user_id"`
	Limit       int            `json:"limit"`
	Offset      int            `json:"offset"`
	Preferences map[string]any `json:"preferences,omitempty"`
}

// BuildFetchContentRequest maps API request to orchestrator request.
func BuildFetchContentRequest(req models.ContentRequest) FetchContentRequest {
	limit := req.Limit
	if limit <= 0 {
		limit = 20
	}

	return FetchContentRequest{
		UserID: req.UserID,
		Limit:  limit,
		Offset: req.Offset,
	}
}

