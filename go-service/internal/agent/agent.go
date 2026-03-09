package agent

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

const (
	pathUnderstandSoul  = "/agent/understand-soul"
	pathGenerateContent = "/agent/generate-content"
	pathChat            = "/agent/chat"
)

// Types: shared contract models and client state.

// Query represents one generated platform query.
type Query struct {
	Platform string `json:"platform"`
	Query    string `json:"query"`
}

// UnderstandSoulRequest is the /agent/understand-soul request payload.
type UnderstandSoulRequest struct {
	UserID        string `json:"user_id"`
	InitialPrompt string `json:"initial_prompt"`
	RecentChats   []any  `json:"recent_chats"`
}

// UnderstandSoulResponse is the /agent/understand-soul response payload.
type UnderstandSoulResponse struct {
	UserID string `json:"user_id"`
	Soul   string `json:"soul"`
}

// GenerateContentRequest is the /agent/generate-content request payload.
type GenerateContentRequest struct {
	UserID          string         `json:"user_id"`
	InitialPrompt   string         `json:"initial_prompt"`
	EnhancedProfile string         `json:"enhanced_profile"`
	Preferences     map[string]any `json:"preferences"`
	RecentChats     []any          `json:"recent_chats"`
	Limit           int            `json:"limit"`
}

// GenerateContentResponse is the /agent/generate-content response payload.
type GenerateContentResponse struct {
	Items []models.ContentItem `json:"items"`
}

// ChatRequest is the /agent/chat request payload.
type ChatRequest struct {
	UserID            string         `json:"user_id"`
	Message           string         `json:"message"`
	UserGoal          string         `json:"user_goal"`
	UserProfile       map[string]any `json:"user_profile"`
	ChatHistory       []any          `json:"chat_history"`
	CurrentContentIDs []string       `json:"current_content_ids"`
}

// ChatResponse is the /agent/chat response payload.
type ChatResponse struct {
	ChatResponse    string `json:"chat_response"`
	NeedsNewContent bool   `json:"needs_new_content"`
}

// Client wraps Python agent API calls.
type Client struct {
	baseURL string
	http    *http.Client
}

// Functions: constructors, endpoint methods, and helpers.

// Default timeout for agent HTTP calls. Generate-content (scrape + rank) can take a minute or more.
const defaultAgentTimeout = 90 * time.Second

// NewClient builds an agent client with a timeout suitable for long-running generate-content.
func NewClient(baseURL string) *Client {
	return &Client{
		baseURL: strings.TrimRight(baseURL, "/"),
		http: &http.Client{
			Timeout: defaultAgentTimeout,
		},
	}
}

// UnderstandSoul calls /agent/understand-soul.
func (c *Client) UnderstandSoul(ctx context.Context, req UnderstandSoulRequest) (*UnderstandSoulResponse, error) {
	var resp UnderstandSoulResponse
	if err := c.postJSON(ctx, pathUnderstandSoul, req, &resp); err != nil {
		return nil, err
	}
	return &resp, nil
}

// GenerateContent calls /agent/generate-content.
func (c *Client) GenerateContent(ctx context.Context, req GenerateContentRequest) (*GenerateContentResponse, error) {
	var resp GenerateContentResponse
	if err := c.postJSON(ctx, pathGenerateContent, req, &resp); err != nil {
		return nil, err
	}
	return &resp, nil
}

// Chat calls /agent/chat.
func (c *Client) Chat(ctx context.Context, req ChatRequest) (*ChatResponse, error) {
	var resp ChatResponse
	if err := c.postJSON(ctx, pathChat, req, &resp); err != nil {
		return nil, err
	}
	return &resp, nil
}

// postJSON sends a JSON POST request and decodes the JSON response.
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
		return fmt.Errorf("agent status %d: %s", httpResp.StatusCode, strings.TrimSpace(string(respBody)))
	}

	if err := json.NewDecoder(httpResp.Body).Decode(out); err != nil {
		return fmt.Errorf("decode response: %w", err)
	}

	return nil
}

// buildURL joins base URL and endpoint path safely.
func (c *Client) buildURL(path string) string {
	if strings.HasPrefix(path, "/") {
		return c.baseURL + path
	}
	return c.baseURL + "/" + path
}
