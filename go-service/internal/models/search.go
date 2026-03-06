package models

// SearchQuery represents a platform-specific search term.
type SearchQuery struct {
	Platform string `json:"platform"`
	Query    string `json:"query"`
}

