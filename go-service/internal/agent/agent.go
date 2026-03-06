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
)

const (
	pathUnderstandSoul  = "/agent/understand-soul"
	pathGenerateQueries = "/agent/generate-queries"
	pathRank            = "/agent/rank"
	pathChat            = "/agent/chat"
)

// Types: shared contract models and client state.

// Query represents one generated platform query.
type Query struct {
	Platform string `json:"platform"`
	Query    string `json:"query"`
}

// RankedItem represents one ranked content item from agent.
type RankedItem struct {
	ID                string  `json:"id"`
	Type              string  `json:"type"`
	Platform          string  `json:"platform"`
	URL               string  `json:"url"`
	Title             string  `json:"title"`
	ManifestationNote string  `json:"manifestation_note"`
	Score             float64 `json:"score"`
}

// UnderstandGoalRequest is the /agent/understand-soul request payload.
type UnderstandGoalRequest struct {
	UserID        string `json:"user_id"`
	InitialPrompt string `json:"initial_prompt"`
}

// UnderstandGoalResponse is the /agent/understand-soul response payload.
type UnderstandGoalResponse struct {
	UserID string `json:"user_id"`
	Soul   string `json:"soul"`
}

// GenerateQueriesRequest is the /agent/generate-queries request payload.
type GenerateQueriesRequest struct {
	UserID      string         `json:"user_id"`
	UserGoal    string         `json:"user_goal"`
	UserProfile map[string]any `json:"user_profile"`
	RecentChats []any          `json:"recent_chats"`
}

// GenerateQueriesResponse is the /agent/generate-queries response payload.
type GenerateQueriesResponse struct {
	Queries []Query `json:"queries"`
}

// RankRequest is the /agent/rank request payload.
type RankRequest struct {
	UserID      string         `json:"user_id"`
	UserGoal    string         `json:"user_goal"`
	UserProfile map[string]any `json:"user_profile"`
	RawResults  []any          `json:"raw_results"`
}

// RankResponse is the /agent/rank response payload.
type RankResponse struct {
	Items []RankedItem `json:"items"`
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
	ChatResponse     string  `json:"chat_response"`
	NeedsNewContent  bool    `json:"needs_new_content"`
	ManifestationTip string  `json:"manifestation_tip"`
	SearchQueries    []Query `json:"search_queries"`
}

// Client wraps Node agent API calls.
type Client struct {
	baseURL string
	http    *http.Client
}

// Functions: constructors, endpoint methods, and helpers.

// NewClient builds an agent client with a default timeout.
func NewClient(baseURL string) *Client {
	return &Client{
		baseURL: strings.TrimRight(baseURL, "/"),
		http: &http.Client{
			Timeout: 15 * time.Second,
		},
	}
}

// UnderstandGoal calls /agent/understand-soul.
func (c *Client) UnderstandGoal(ctx context.Context, req UnderstandGoalRequest) (*UnderstandGoalResponse, error) {
	var resp UnderstandGoalResponse
	if err := c.postJSON(ctx, pathUnderstandSoul, req, &resp); err != nil {
		return nil, err
	}
	return &resp, nil
}

// GenerateQueries calls /agent/generate-queries.
func (c *Client) GenerateQueries(ctx context.Context, req GenerateQueriesRequest) (*GenerateQueriesResponse, error) {
	var resp GenerateQueriesResponse
	if err := c.postJSON(ctx, pathGenerateQueries, req, &resp); err != nil {
		return nil, err
	}
	return &resp, nil
}

// Rank calls /agent/rank.
func (c *Client) Rank(ctx context.Context, req RankRequest) (*RankResponse, error) {
	var resp RankResponse
	if err := c.postJSON(ctx, pathRank, req, &resp); err != nil {
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
