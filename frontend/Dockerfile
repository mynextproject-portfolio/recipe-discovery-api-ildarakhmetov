# Multi-stage build for SvelteKit with Node.js adapter
FROM node:22-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the SvelteKit application
RUN npm run build

# Production stage
FROM node:22-alpine AS production

# Set working directory
WORKDIR /app

# Copy built application and package.json
COPY --from=builder /app/build build/
COPY --from=builder /app/node_modules node_modules/
COPY --from=builder /app/package.json .

# Expose port
EXPOSE 3000

# Set environment for production
ENV NODE_ENV=production

# Run the application
CMD ["node", "build"]
