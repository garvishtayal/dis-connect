package orchestrator

import "github.com/garvishtayal/dis-connect/go-service/internal/models"

// FetchContentResponse is received from Python orchestrator.
type FetchContentResponse struct {
	Items []models.ContentItem `json:"items"`
}

// NormalizeFetchContentResponse returns a safe items slice.
func NormalizeFetchContentResponse(resp *FetchContentResponse) []models.ContentItem {
	if resp == nil || resp.Items == nil {
		return []models.ContentItem{}
	}
	return resp.Items
}

