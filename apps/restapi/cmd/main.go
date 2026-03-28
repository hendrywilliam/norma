package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"

	"github.com/hendrywilliam/norma/apps/restapi/internal/container"
)

func main() {
	// Initialize DI Container
	scope := container.NewContainer()
	defer scope.Shutdown()

	// Get config
	cfg := container.GetConfig(scope)

	// Set Gin mode
	gin.SetMode(cfg.Server.Mode)

	// Create router
	router := gin.New()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "healthy",
			"time":   time.Now().Format(time.RFC3339),
		})
	})

	// API routes
	api := router.Group("/api/v1")
	{
		// Register handlers
		peraturanHandler := container.GetPeraturanHandler(scope)
		peraturanHandler.RegisterRoutes(api)
	}

	// Root endpoint
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"name":    "Peraturan REST API",
			"version": "1.0.0",
			"status":  "running",
			"docs":    "/health",
			"endpoints": gin.H{
				"peraturan": "/api/v1/peraturan",
				"search":    "/api/v1/peraturan/search",
			},
		})
	})

	// Start server
	srv := &http.Server{
		Addr:         fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port),
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Graceful shutdown
	go func() {
		quit := make(chan os.Signal, 1)
		signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
		<-quit

		log.Println("Shutting down server...")

		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()

		if err := srv.Shutdown(ctx); err != nil {
			log.Fatal("Server forced to shutdown:", err)
		}
	}()

	log.Printf("Server starting on %s:%d", cfg.Server.Host, cfg.Server.Port)
	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Failed to start server: %v", err)
	}

	log.Println("Server exited")
}
