package postgres

import (
	"database/sql"

	"github.com/garvishtayal/dis-connect/go-service/internal/config"
)

// Client wraps a PostgreSQL connection.
type Client struct {
	DB *sql.DB
}

// NewClient creates a PostgreSQL client from app config.
func NewClient(cfg *config.AppConfig) (*Client, error) {
	db, err := config.NewPostgresDB(cfg)
	if err != nil {
		return nil, err
	}
	return &Client{DB: db}, nil
}

