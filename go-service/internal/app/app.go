package app

import (
	"context"
	"fmt"
	"os"
	"sync"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"

	"github.com/garvishtayal/dis-connect/go-service/internal/content/aggregator"
	"github.com/garvishtayal/dis-connect/go-service/internal/api"
	"github.com/garvishtayal/dis-connect/go-service/internal/api/handlers"
	"github.com/garvishtayal/dis-connect/go-service/internal/api/middleware"
	agentclient "github.com/garvishtayal/dis-connect/go-service/internal/agent"
	"github.com/garvishtayal/dis-connect/go-service/internal/auth"
	"github.com/garvishtayal/dis-connect/go-service/internal/config"
	"github.com/garvishtayal/dis-connect/go-service/internal/content/queue"
	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
	redisrepo "github.com/garvishtayal/dis-connect/go-service/internal/repository/redis"
	"github.com/garvishtayal/dis-connect/go-service/internal/content/scraper"
	"github.com/garvishtayal/dis-connect/go-service/internal/service"
	"github.com/garvishtayal/dis-connect/go-service/internal/content/worker"
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

	// Postgres repositories.
	userRepo := postgres.NewUserRepository(pgClient)
	chatRepo := postgres.NewChatRepository(pgClient)
	preferenceRepo := postgres.NewPreferenceRepository(pgClient)
	upgradeRepo := postgres.NewUpgradeRepository(pgClient)

	// Redis repositories.
	redisClient := redisrepo.NewClient(cfg)
	dedupRepo := redisrepo.NewDedupRepository(redisClient)
	rateLimitRepo := redisrepo.NewRateLimitRepository(redisClient)
	stateRepo := redisrepo.NewRequestStateRepository(redisClient)
	cacheRepo := redisrepo.NewSearchCacheRepository(redisClient)

	// Queue + scraper client (both talk to the Python service).
	q := queue.NewRedisQueue(redisClient.Client)
	scraperClient := scraper.NewClient(cfg.AgentBaseURL)
	agg := aggregator.New(stateRepo)

	// Start background worker pools (run for the lifetime of the process).
	workerCtx := context.Background()
	worker.StartYouTubePool(workerCtx, q, scraperClient, stateRepo, cacheRepo)
	worker.StartPinterestPool(workerCtx, q, scraperClient, stateRepo, cacheRepo, cfg.PinterestProxyURL)

	// Gin engine + global middleware.
	router := gin.New()
	router.Use(middleware.Logger())
	router.Use(middleware.CORS())

	// Service layer.
	agentSvc := agentclient.NewClient(cfg.AgentBaseURL)
	authSvc := service.NewAuthService(tokenValidator, userRepo)
	userSvc := service.NewUserService(userRepo, agentSvc)
	contentSvc := service.NewContentService(agentSvc, userRepo, dedupRepo, rateLimitRepo, q, cacheRepo, stateRepo, agg)
	chatSvc := service.NewChatService(agentSvc, contentSvc, userRepo, chatRepo, preferenceRepo, rateLimitRepo)
	upgradeSvc := service.NewUpgradeService(upgradeRepo, userRepo)

	firebaseAuth := middleware.FirebaseAuth(tokenValidator)
	onboardingRequired := middleware.OnboardingRequired(userRepo)

	// Handlers.
	authHandler := handlers.NewAuthHandler(authSvc)
	userHandler := handlers.NewUserHandler(userSvc)
	chatHandler := handlers.NewChatHandler(chatSvc)
	contentHandler := handlers.NewContentHandler(contentSvc)
	upgradeHandler := handlers.NewUpgradeHandler(upgradeSvc)
	healthHandler := handlers.NewHealthHandler()

	// Routes.
	apiRouter := api.NewRouter(
		authHandler,
		userHandler,
		chatHandler,
		contentHandler,
		upgradeHandler,
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
