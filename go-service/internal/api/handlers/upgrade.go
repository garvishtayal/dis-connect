package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/service"
)

// UpgradeHandler exposes upgrade-related endpoints.
type UpgradeHandler struct {
	upgradeService *service.UpgradeService
}

// NewUpgradeHandler creates an UpgradeHandler.
func NewUpgradeHandler(upgradeService *service.UpgradeService) *UpgradeHandler {
	return &UpgradeHandler{upgradeService: upgradeService}
}

// UpsertUpgrade handles POST /api/upgrade.
func (h *UpgradeHandler) UpsertUpgrade(c *gin.Context) {
	var req models.UpsertUpgradeRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request"})
		return
	}

	rec, err := h.upgradeService.Upsert(c.Request.Context(), req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, rec)
}

// GetUpgrade handles GET /api/upgrade?user_id=...
func (h *UpgradeHandler) GetUpgrade(c *gin.Context) {
	userID := c.Query("user_id")
	if userID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "user_id is required"})
		return
	}

	rec, err := h.upgradeService.Get(c.Request.Context(), userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	if rec == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "no upgrade record found"})
		return
	}

	c.JSON(http.StatusOK, rec)
}
