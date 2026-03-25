// Package scraper is a thin HTTP client that calls the Python /scraper/* endpoints.
// Python owns all scraping logic; Go workers only call this client.
package scraper

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
	pathScrapeYouTube   = "/scraper/youtube"
	pathScrapePinterest = "/scraper/pinterest"
	scraperTimeout      = 45 * time.Second
)

type youtubeReq struct {
	Query string `json:"query"`
}

type pinterestReq struct {
	Query string `json:"query"`
	Proxy string `json:"proxy,omitempty"`
}

// Client calls Python scraper endpoints.
type Client struct {
	baseURL string
	http    *http.Client
}

func NewClient(baseURL string) *Client {
	return &Client{
		baseURL: strings.TrimRight(baseURL, "/"),
		http:    &http.Client{Timeout: scraperTimeout},
	}
}

// ScrapeYouTube fetches YouTube results for a query from Python.
func (c *Client) ScrapeYouTube(ctx context.Context, query string) ([]models.ContentItem, error) {
	return c.post(ctx, pathScrapeYouTube, youtubeReq{Query: query})
}

// ScrapePinterest fetches Pinterest results for a query from Python.
// proxy is optional; pass "" when not using a proxy.
func (c *Client) ScrapePinterest(ctx context.Context, query, proxy string) ([]models.ContentItem, error) {
	return c.post(ctx, pathScrapePinterest, pinterestReq{Query: query, Proxy: proxy})
}

func (c *Client) post(ctx context.Context, path string, body any) ([]models.ContentItem, error) {
	b, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("marshal scrape request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL+path, bytes.NewReader(b))
	if err != nil {
		return nil, fmt.Errorf("build scrape request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.http.Do(req)
	if err != nil {
		return nil, fmt.Errorf("scrape request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		raw, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("scraper returned %d: %s", resp.StatusCode, strings.TrimSpace(string(raw)))
	}

	var items []models.ContentItem
	if err := json.NewDecoder(resp.Body).Decode(&items); err != nil {
		return nil, fmt.Errorf("decode scrape response: %w", err)
	}
	return items, nil
}
