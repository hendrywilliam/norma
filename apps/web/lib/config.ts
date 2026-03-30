// Environment configuration

export const config = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
    timeout: 30000, // 30 seconds
  },
  app: {
    name: "Norma",
    description: "Database Peraturan Indonesia",
    url: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  },
} as const;