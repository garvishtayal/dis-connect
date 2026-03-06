package main

import (
	"github.com/garvishtayal/dis-connect/go-service/internal/app"
	"log"
)

// main starts the HTTP server.
func main() {
	port := app.ResolvePort()
	engine, err := app.BuildRouter()
	if err != nil {
		log.Fatalf("server bootstrap failed: %v", err)
	}

	if err := engine.Run(":" + port); err != nil {
		log.Fatalf("server failed: %v", err)
	}
}
