package queue

// ScrapeJob is pushed onto a platform queue and consumed by a worker.
type ScrapeJob struct {
	RequestID string `json:"request_id"`
	Platform  string `json:"platform"`
	Query     string `json:"query"`
	// Proxy is an optional HTTP proxy URL attached by the worker pool config (Pinterest only).
	Proxy string `json:"proxy,omitempty"`
}
