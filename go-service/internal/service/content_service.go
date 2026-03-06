package service

import (
	"context"
	"fmt"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/orchestrator"
)

// ContentService handles content fetching flows.
type ContentService struct {
	orchestrator *orchestrator.Client
}

// NewContentService creates a new ContentService.
func NewContentService(orchestratorClient *orchestrator.Client) *ContentService {
	return &ContentService{orchestrator: orchestratorClient}
}

// GetContent returns a list of content items for the feed.
func (s *ContentService) GetContent(ctx context.Context, req models.ContentRequest) ([]models.ContentItem, error) {
	if s.orchestrator == nil {
		return nil, fmt.Errorf("orchestrator client is not configured")
	}

	orchestratorReq := orchestrator.BuildFetchContentRequest(req)
	items, err := s.orchestrator.FetchContent(ctx, orchestratorReq)
	if err != nil {
		return nil, err
	}
	return items, nil
}
