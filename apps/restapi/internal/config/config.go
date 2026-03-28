package config

import (
	"os"
	"path/filepath"
	"runtime"
	"strconv"

	"github.com/joho/godotenv"
)

type Config struct {
	Server   ServerConfig
	Database DatabaseConfig
}

type ServerConfig struct {
	Host string
	Port int
	Mode string
}

type DatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	Name     string
	SSLMode  string
}

func Load() *Config {
	// Try to load .env from multiple locations
	loadEnv()

	return &Config{
		Server: ServerConfig{
			Host: getEnv("SERVER_HOST", "0.0.0.0"),
			Port: getEnvAsInt("SERVER_PORT", 8080),
			Mode: getEnv("GIN_MODE", "debug"),
		},
		Database: DatabaseConfig{
			Host:     getEnv("DB_HOST", "localhost"),
			Port:     getEnvAsInt("DB_PORT", 5432),
			User:     getEnv("DB_USER", "postgres"),
			Password: getEnv("DB_PASSWORD", "postgres"),
			Name:     getEnv("DB_NAME", "peraturan_db"),
			SSLMode:  getEnv("DB_SSLMODE", "disable"),
		},
	}
}

// loadEnv tries to load .env from multiple locations
func loadEnv() {
	// Priority:
	// 1. Current working directory
	// 2. Executable directory
	// 3. Project root (relative to this file)
	// 4. Common relative paths

	// Try current working directory (most common case)
	if err := godotenv.Load(); err == nil {
		return
	}

	// Try executable directory
	if exePath, err := os.Executable(); err == nil {
		exeDir := filepath.Dir(exePath)
		if err := godotenv.Load(filepath.Join(exeDir, ".env")); err == nil {
			return
		}
	}

	// Try project root using runtime.Caller
	// This file is at: apps/restapi/internal/config/config.go
	// We want: apps/restapi/.env
	_, filename, _, ok := runtime.Caller(0)
	if ok {
		// Go up 3 levels: config -> internal -> restapi
		projectRoot := filepath.Dir(filepath.Dir(filepath.Dir(filename)))
		if err := godotenv.Load(filepath.Join(projectRoot, ".env")); err == nil {
			return
		}
	}

	// Try common relative paths (for different execution contexts)
	relativePaths := []string{
		".env",
		"./.env",
		"./apps/restapi/.env",
		"../.env",
		"../../.env",
		"../../../.env",
	}

	for _, path := range relativePaths {
		if err := godotenv.Load(path); err == nil {
			return
		}
	}

	// If not found, rely on system environment variables
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	valueStr := os.Getenv(key)
	if value, err := strconv.Atoi(valueStr); err == nil {
		return value
	}
	return defaultValue
}
