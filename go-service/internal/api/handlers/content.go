package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/service"
)

// ContentHandler exposes content-related endpoints.
type ContentHandler struct {
	contentService *service.ContentService
}

// NewContentHandler creates a new ContentHandler.
func NewContentHandler(contentService *service.ContentService) *ContentHandler {
	return &ContentHandler{contentService: contentService}
}

// GetContent handles GET /api/content.
func (h *ContentHandler) GetContent(c *gin.Context) {
	var req models.ContentRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request"})
		return
	}

	items, err := h.contentService.GetContent(c.Request.Context(), req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to fetch content", "detail": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"items": items})
}

