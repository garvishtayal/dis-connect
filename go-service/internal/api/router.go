package api

import (
	"github.com/gin-gonic/gin"

	"github.com/garvishtayal/dis-connect/go-service/internal/api/handlers"
)

// Router holds all HTTP handlers.
type Router struct {
	auth         *handlers.AuthHandler
	user         *handlers.UserHandler
	chat         *handlers.ChatHandler
	content      *handlers.ContentHandler
	health       *handlers.HealthHandler
	firebaseAuth gin.HandlerFunc
	onboarding   gin.HandlerFunc
}

// NewRouter wires handlers into a Router.
func NewRouter(
	auth *handlers.AuthHandler,
	user *handlers.UserHandler,
	chat *handlers.ChatHandler,
	content *handlers.ContentHandler,
	health *handlers.HealthHandler,
	firebaseAuth gin.HandlerFunc,
	onboarding gin.HandlerFunc,
) *Router {
	return &Router{
		auth:         auth,
		user:         user,
		chat:         chat,
		content:      content,
		health:       health,
		firebaseAuth: firebaseAuth,
		onboarding:   onboarding,
	}
}

// RegisterRoutes attaches all routes to Gin.
func (r *Router) RegisterRoutes(engine *gin.Engine) {
	engine.GET("/healthz", r.health.Health)

	apiGroup := engine.Group("/api")

	authGroup := apiGroup.Group("/auth")
	{
		authGroup.POST("/google", r.auth.SignInWithGoogle)
		authGroup.POST("/apple", r.auth.SignInWithApple)
	}

	protectedGroup := apiGroup.Group("")
	protectedGroup.Use(r.firebaseAuth)

	userGroup := protectedGroup.Group("/users")
	{
		userGroup.POST("", r.user.CreateUser)
	}

	onboardedGroup := protectedGroup.Group("")
	onboardedGroup.Use(r.onboarding)

	// Protected content and chat endpoints (Firebase + onboarding).
	onboardedGroup.GET("/content", r.content.GetContent)
	onboardedGroup.POST("/chat", r.chat.HandleChat)
}
