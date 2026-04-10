# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install bun
RUN npm install -g bun

# Copy package files
COPY package.json bun.lock ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source code
COPY . .

# Build with build-time environment variables
# These act as defaults, can be overridden at runtime
ARG NEXT_PUBLIC_API_URL=http://localhost:8080
ARG NEXT_PUBLIC_APP_URL=http://localhost:3000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_APP_URL=$NEXT_PUBLIC_APP_URL

# Build the application
RUN bun run build

# Final stage
FROM node:20-alpine AS runner

WORKDIR /app

# Copy built files from builder
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=production
ENV HOSTNAME="0.0.0.0"

# Run the application
CMD ["node", "server.js"]