package handlers

import (
	"errors"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/garvishtayal/dis-connect/go-service/internal/models"
	"github.com/garvishtayal/dis-connect/go-service/internal/service"
)

// ChatHandler exposes chat-related endpoints.
type ChatHandler struct {
	chatService *service.ChatService
}

// NewChatHandler creates a new ChatHandler.
func NewChatHandler(chatService *service.ChatService) *ChatHandler {
	return &ChatHandler{chatService: chatService}
}

// HandleChat handles POST /api/chat.
func (h *ChatHandler) HandleChat(c *gin.Context) {
	var req models.ChatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request"})
		return
	}

	resp, err := h.chatService.HandleChat(c.Request.Context(), req)
	if err != nil {
		if errors.Is(err, service.ErrChatLimit) {
			c.JSON(http.StatusTooManyRequests, gin.H{"error": "daily chat limit reached"})
			return
		}
		// Include underlying error so the frontend can display a useful message.
		// (This helps debug issues like user_id mismatches after logout/login.)
		c.JSON(
			http.StatusInternalServerError,
			gin.H{"error": fmt.Sprintf("failed to handle chat: %v", err)},
		)
		return
	}

	c.JSON(http.StatusOK, resp)
}
