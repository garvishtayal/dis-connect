package api

import (
	"github.com/gin-gonic/gin"

	"github.com/garvishtayal/dis-connect/go-service/internal/api/handlers"
	"github.com/garvishtayal/dis-connect/go-service/internal/api/middleware"
)

// Router holds all HTTP handlers.
type Router struct {
	auth         *handlers.AuthHandler
	user         *handlers.UserHandler
	chat         *handlers.ChatHandler
	content      *handlers.ContentHandler
	preferences  *handlers.PreferencesHandler
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
	preferences *handlers.PreferencesHandler,
	health *handlers.HealthHandler,
	firebaseAuth gin.HandlerFunc,
	onboarding gin.HandlerFunc,
) *Router {
	return &Router{
		auth:         auth,
		user:         user,
		chat:         chat,
		content:      content,
		preferences:  preferences,
		health:       health,
		firebaseAuth: firebaseAuth,
		onboarding:   onboarding,
	}
}

// RegisterRoutes attaches all routes to Gin.
func (r *Router) RegisterRoutes(engine *gin.Engine) {
	engine.GET("/healthz", r.health.Health)

	apiGroup := engine.Group("/api")
	apiGroup.Use(middleware.RateLimit())

	authGroup := apiGroup.Group("/auth")
	{
		authGroup.POST("/google", r.auth.SignInWithGoogle)
		authGroup.POST("/apple", r.auth.SignInWithApple)
	}

	// Content: no auth/onboarding for testing linking to Python service.
	apiGroup.GET("/content", r.content.GetContent)

	protectedGroup := apiGroup.Group("")
	protectedGroup.Use(r.firebaseAuth)

	userGroup := protectedGroup.Group("/users")
	{
		userGroup.POST("", r.user.CreateUser)
	}

	onboardedGroup := protectedGroup.Group("")
	onboardedGroup.Use(r.onboarding)

	chatGroup := onboardedGroup.Group("/chat")
	{
		chatGroup.POST("", r.chat.HandleChat)
	}

	prefGroup := onboardedGroup.Group("/preferences")
	{
		prefGroup.POST("", r.preferences.UpdatePreferences)
	}
}
