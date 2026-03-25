// Package mixer applies type-ratio mixing, API-relevance ranking, and cross-request dedup
// to a flat pool of content items before returning them to the client.
package mixer

import "github.com/garvishtayal/dis-connect/go-service/internal/models"

// Mix selects up to limit items from items using:
//   - Ratio: 40% Pinterest images | 40% YouTube shorts | 20% YouTube videos
//   - Ranking: YouTube API order preserved (API returns results ranked by relevance)
//   - Dedup: within-batch URL dedup; up to 40% already-shown (old) content allowed
func Mix(items []models.ContentItem, shownURLs map[string]struct{}, limit int) []models.ContentItem {
	// Bucket by type, dedup within batch.
	seenURL := make(map[string]struct{}, len(items))
	var images, shorts, videos []models.ContentItem
	for _, it := range items {
		if it.URL == "" {
			continue
		}
		if _, dup := seenURL[it.URL]; dup {
			continue
		}
		seenURL[it.URL] = struct{}{}
		switch it.Type {
		case "short":
			shorts = append(shorts, it)
		case "video":
			videos = append(videos, it)
		default: // "image" — Pinterest
			images = append(images, it)
		}
	}

	// Target counts per type; videos absorb rounding remainder (~20%).
	nImages := (limit * 40) / 100
	nShorts := (limit * 40) / 100
	nVideos := limit - nImages - nShorts

	// Candidates in ratio order; bucket order == relevance ranking for YouTube.
	candidates := make([]models.ContentItem, 0, limit)
	candidates = append(candidates, take(images, nImages)...)
	candidates = append(candidates, take(shorts, nShorts)...)
	candidates = append(candidates, take(videos, nVideos)...)

	// Separate fresh vs. already-shown.
	var fresh, old []models.ContentItem
	for _, it := range candidates {
		if _, seen := shownURLs[it.URL]; seen {
			old = append(old, it)
		} else {
			fresh = append(fresh, it)
		}
	}

	// Fresh items first; pad with old up to 40% of limit.
	maxOld := (limit * 40) / 100
	out := make([]models.ContentItem, 0, limit)
	out = append(out, fresh...)
	for i := 0; i < len(old) && i < maxOld; i++ {
		out = append(out, old[i])
	}
	if len(out) > limit {
		out = out[:limit]
	}
	return out
}

// take returns the first n items of s, or all of s when len(s) <= n.
func take(s []models.ContentItem, n int) []models.ContentItem {
	if n <= 0 || len(s) == 0 {
		return nil
	}
	if len(s) <= n {
		return s
	}
	return s[:n]
}
