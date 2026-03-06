package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/garvishtayal/dis-connect/go-service/internal/service"
)

// PreferencesHandler exposes user preference endpoints.
type PreferencesHandler struct {
	preferenceService *service.PreferenceService
}

// NewPreferencesHandler creates a new PreferencesHandler.
func NewPreferencesHandler(preferenceService *service.PreferenceService) *PreferencesHandler {
	return &PreferencesHandler{preferenceService: preferenceService}
}

// UpdatePreferences handles POST /api/preferences.
func (h *PreferencesHandler) UpdatePreferences(c *gin.Context) {
	userID := c.Query("user_id")
	if userID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "user_id is required"})
		return
	}

	var body map[string]any
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request"})
		return
	}

	if err := h.preferenceService.UpdatePreferences(c.Request.Context(), userID, body); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to update preferences"})
		return
	}

	c.Status(http.StatusNoContent)
}

