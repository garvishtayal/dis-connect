package orchestrator

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
)

const pathFetchContent = "/orchestrator/fetch-content"

// Client is a thin HTTP client for Python orchestrator APIs.
type Client struct {
	baseURL string
	http    *http.Client
}

// NewClient creates a new orchestrator client.
func NewClient(baseURL string) *Client {
	return &Client{
		baseURL: strings.TrimRight(baseURL, "/"),
		http: &http.Client{
			Timeout: 20 * time.Second,
		},
	}
}

// FetchContent asks Python service to fetch and rank content.
func (c *Client) FetchContent(ctx context.Context, req FetchContentRequest) ([]models.ContentItem, error) {
	var resp FetchContentResponse
	if err := c.postJSON(ctx, pathFetchContent, req, &resp); err != nil {
		return nil, err
	}
	return NormalizeFetchContentResponse(&resp), nil
}

// postJSON sends JSON POST and decodes JSON response.
func (c *Client) postJSON(ctx context.Context, path string, in any, out any) error {
	body, err := json.Marshal(in)
	if err != nil {
		return fmt.Errorf("marshal request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, c.buildURL(path), bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("build request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	httpResp, err := c.http.Do(httpReq)
	if err != nil {
		return fmt.Errorf("send request: %w", err)
	}
	defer httpResp.Body.Close()

	if httpResp.StatusCode < 200 || httpResp.StatusCode >= 300 {
		respBody, _ := io.ReadAll(httpResp.Body)
		return fmt.Errorf("orchestrator status %d: %s", httpResp.StatusCode, strings.TrimSpace(string(respBody)))
	}

	if err := json.NewDecoder(httpResp.Body).Decode(out); err != nil {
		return fmt.Errorf("decode response: %w", err)
	}

	return nil
}

func (c *Client) buildURL(path string) string {
	if strings.HasPrefix(path, "/") {
		return c.baseURL + path
	}
	return c.baseURL + "/" + path
}

