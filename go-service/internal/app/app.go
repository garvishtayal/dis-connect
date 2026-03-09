package app

import (
	"context"
	"fmt"
	"os"
	"sync"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"

	"github.com/garvishtayal/dis-connect/go-service/internal/api"
	"github.com/garvishtayal/dis-connect/go-service/internal/api/handlers"
	"github.com/garvishtayal/dis-connect/go-service/internal/api/middleware"
	agentclient "github.com/garvishtayal/dis-connect/go-service/internal/agent"
	"github.com/garvishtayal/dis-connect/go-service/internal/auth"
	"github.com/garvishtayal/dis-connect/go-service/internal/config"
	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
	redisrepo "github.com/garvishtayal/dis-connect/go-service/internal/repository/redis"
	"github.com/garvishtayal/dis-connect/go-service/internal/service"
)

var loadEnvOnce sync.Once

// BuildRouter wires middleware, services, handlers, and routes.
func BuildRouter() (*gin.Engine, error) {
	loadEnv()

	cfg := config.LoadAppConfig()
	if cfg.FirebaseCredentialsPath == "" {
		return nil, fmt.Errorf("FIREBASE_CREDENTIALS_PATH is required")
	}
	file, err := os.Open(cfg.FirebaseCredentialsPath)
	if err != nil {
		return nil, fmt.Errorf("firebase credentials file not readable: %w", err)
	}
	_ = file.Close()

	firebaseClient, err := auth.NewFirebaseClient(context.Background())
	if err != nil {
		return nil, err
	}
	tokenValidator, err := auth.NewTokenValidator(context.Background(), firebaseClient)
	if err != nil {
		return nil, err
	}
	pgClient, err := postgres.NewClient(cfg)
	if err != nil {
		return nil, err
	}
	userRepo := postgres.NewUserRepository(pgClient)
	redisClient := redisrepo.NewClient(cfg)
	dedupRepo := redisrepo.NewDedupRepository(redisClient)

	router := gin.New()

	// Attach global HTTP middleware.
	router.Use(middleware.Logger())
	router.Use(middleware.CORS())

	// Build service layer dependencies.
	agentSvc := agentclient.NewClient(cfg.AgentBaseURL)
	authSvc := service.NewAuthService(tokenValidator, userRepo)
	userSvc := service.NewUserService(userRepo, agentSvc)
	contentSvc := service.NewContentService(agentSvc, userRepo, dedupRepo)
	chatSvc := service.NewChatService(agentSvc, contentSvc)
	preferenceSvc := service.NewPreferenceService()
	firebaseAuth := middleware.FirebaseAuth(tokenValidator)
	onboardingRequired := middleware.OnboardingRequired(userRepo)

	// Bind handlers to services.
	authHandler := handlers.NewAuthHandler(authSvc)
	userHandler := handlers.NewUserHandler(userSvc)
	chatHandler := handlers.NewChatHandler(chatSvc)
	contentHandler := handlers.NewContentHandler(contentSvc)
	preferencesHandler := handlers.NewPreferencesHandler(preferenceSvc)
	healthHandler := handlers.NewHealthHandler()

	// Register all API routes.
	apiRouter := api.NewRouter(
		authHandler,
		userHandler,
		chatHandler,
		contentHandler,
		preferencesHandler,
		healthHandler,
		firebaseAuth,
		onboardingRequired,
	)
	apiRouter.RegisterRoutes(router)

	return router, nil
}

// ResolvePort returns the HTTP port with a default fallback.
func ResolvePort() string {
	loadEnv()
	return config.LoadAppConfig().Port
}

// loadEnv reads .env once when present.
func loadEnv() {
	loadEnvOnce.Do(func() {
		_ = godotenv.Load()
	})
}
