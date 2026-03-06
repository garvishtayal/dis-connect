package config

import (
	"database/sql"
	"fmt"
	"os"
	"time"

	_ "github.com/lib/pq"
	"github.com/redis/go-redis/v9"
)

// AppConfig holds environment-driven configuration.
type AppConfig struct {
	Port                   string
	DatabaseURL            string
	RedisAddr              string
	AgentBaseURL           string
	FirebaseCredentialsPath string
}

// LoadAppConfig reads configuration from environment with sane defaults.
func LoadAppConfig() *AppConfig {
	port := getEnv("PORT", "8080")
	dbURL := getEnv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/dis_connect?sslmode=disable")
	redisAddr := getEnv("REDIS_ADDR", "localhost:6379")
	agentBaseURL := getEnv("AGENT_BASE_URL", "http://localhost:3000")
	firebasePath := getEnv("FIREBASE_CREDENTIALS_PATH", "")

	return &AppConfig{
		Port:                   port,
		DatabaseURL:            dbURL,
		RedisAddr:              redisAddr,
		AgentBaseURL:           agentBaseURL,
		FirebaseCredentialsPath: firebasePath,
	}
}

// NewPostgresDB creates a PostgreSQL connection from config.
func NewPostgresDB(cfg *AppConfig) (*sql.DB, error) {
	db, err := sql.Open("postgres", cfg.DatabaseURL)
	if err != nil {
		return nil, fmt.Errorf("open postgres: %w", err)
	}

	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(30 * time.Minute)

	if err := db.Ping(); err != nil {
		_ = db.Close()
		return nil, fmt.Errorf("ping postgres: %w", err)
	}

	return db, nil
}

// NewRedisClient creates a Redis client from config.
func NewRedisClient(cfg *AppConfig) *redis.Client {
	return redis.NewClient(&redis.Options{
		Addr: cfg.RedisAddr,
	})
}

// getEnv returns an env var or a default value.
func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

