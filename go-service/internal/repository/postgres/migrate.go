package postgres

import (
	"database/sql"
	"embed"
	"errors"
	"fmt"

	"github.com/golang-migrate/migrate/v4"
	pgmigrate "github.com/golang-migrate/migrate/v4/database/postgres"
	"github.com/golang-migrate/migrate/v4/source/iofs"
	_ "github.com/lib/pq"
)

//go:embed migrations
var migrationsFS embed.FS

// upMigrations runs SQL migrations on a dedicated connection. golang-migrate's
// Close() closes the *sql.DB passed to WithInstance; that pool must not be the
// application pool, or all later queries fail with "sql: database is closed".
func upMigrations(databaseURL string) error {
	migrateDB, err := sql.Open("postgres", databaseURL)
	if err != nil {
		return fmt.Errorf("migrate open postgres: %w", err)
	}
	if err := migrateDB.Ping(); err != nil {
		_ = migrateDB.Close()
		return fmt.Errorf("migrate ping postgres: %w", err)
	}

	driver, err := pgmigrate.WithInstance(migrateDB, &pgmigrate.Config{})
	if err != nil {
		_ = migrateDB.Close()
		return fmt.Errorf("migrate postgres driver: %w", err)
	}
	src, err := iofs.New(migrationsFS, "migrations")
	if err != nil {
		_ = migrateDB.Close()
		return fmt.Errorf("migrate iofs source: %w", err)
	}
	m, err := migrate.NewWithInstance("iofs", src, "postgres", driver)
	if err != nil {
		_ = migrateDB.Close()
		return fmt.Errorf("migrate: %w", err)
	}
	defer func() { _, _ = m.Close() }()

	if err := m.Up(); err != nil && !errors.Is(err, migrate.ErrNoChange) {
		return err
	}
	return nil
}
