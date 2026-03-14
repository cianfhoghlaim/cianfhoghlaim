---
name: docker-compose
description: Expert assistance for Docker Compose container orchestration. Use when users need multi-container deployments, service networking, volume management, environment configuration, or local development environments.
---

# Docker Compose - Container Orchestration

**Version:** 2.x | **Last Updated:** 2025-01

## Overview

Docker Compose enables multi-container application orchestration:

- **Declarative Configuration**: YAML-based service definitions
- **Service Networking**: Automatic DNS and network creation
- **Volume Management**: Persistent and shared storage
- **Environment Configuration**: Variable substitution and secrets
- **Development Workflows**: Hot reloading and debugging support

**Documentation**: https://docs.docker.com/compose/

## When to Use This Skill

Activate when users need:

- "Set up a multi-container application"
- "Configure Docker Compose services"
- "Connect containers to networks"
- "Manage container volumes and storage"
- "Create development environments"

## Core Concepts

### 1. Basic Compose File

```yaml
# compose.yaml (or docker-compose.yml)
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    depends_on:
      - api
    networks:
      - frontend

  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgres://db:5432/app
    depends_on:
      db:
        condition: service_healthy
    networks:
      - frontend
      - backend

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: app
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

networks:
  frontend:
  backend:

volumes:
  postgres-data:
```

### 2. Environment Variables

```yaml
services:
  app:
    image: my-app:latest
    environment:
      # Direct values
      NODE_ENV: production
      PORT: "3000"

      # From .env file (auto-loaded)
      DATABASE_URL: ${DATABASE_URL}

      # With defaults
      LOG_LEVEL: ${LOG_LEVEL:-info}

      # Required (fails if missing)
      API_KEY: ${API_KEY:?API_KEY is required}

    # Or use env_file
    env_file:
      - .env
      - .env.local
```

**.env file:**
```bash
# .env
DATABASE_URL=postgres://user:pass@db:5432/app
API_KEY=secret123
LOG_LEVEL=debug
```

### 3. Networking

```yaml
services:
  frontend:
    image: nginx
    networks:
      - public
    ports:
      - "80:80"

  api:
    image: api:latest
    networks:
      - public
      - internal
    # Accessible as 'api' from other containers

  database:
    image: postgres
    networks:
      internal:
        aliases:
          - db
          - postgres
    # Not accessible from public network

networks:
  public:
    driver: bridge
  internal:
    driver: bridge
    internal: true  # No external access
```

### 4. Volumes and Storage

```yaml
services:
  app:
    image: my-app
    volumes:
      # Named volume
      - app-data:/app/data

      # Bind mount (host path)
      - ./config:/app/config:ro

      # Anonymous volume
      - /app/temp

      # tmpfs (memory)
      - type: tmpfs
        target: /app/cache
        tmpfs:
          size: 100000000  # 100MB

  backup:
    image: backup-tool
    volumes:
      - app-data:/data:ro  # Read-only access to same volume

volumes:
  app-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/storage/app-data
```

### 5. Health Checks

```yaml
services:
  web:
    image: nginx
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 6. Dependencies and Ordering

```yaml
services:
  app:
    image: my-app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
      migrations:
        condition: service_completed_successfully

  db:
    image: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]

  redis:
    image: redis

  migrations:
    image: my-app
    command: ["npm", "run", "migrate"]
    depends_on:
      db:
        condition: service_healthy
```

### 7. Build Configuration

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        NODE_VERSION: "20"
        BUILD_ENV: production
      target: production
      cache_from:
        - my-app:cache
      labels:
        - "com.example.version=1.0"

  dev:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/node_modules
    command: npm run dev
```

### 8. Resource Limits

```yaml
services:
  app:
    image: my-app
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
        reservations:
          cpus: "0.5"
          memory: 512M
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
```

### 9. Override Files

```yaml
# compose.yaml (base)
services:
  app:
    image: my-app:latest
    environment:
      NODE_ENV: production

# compose.override.yaml (auto-loaded in development)
services:
  app:
    build: .
    volumes:
      - .:/app
    environment:
      NODE_ENV: development
      DEBUG: "true"
    ports:
      - "3000:3000"
      - "9229:9229"  # Debugger

# compose.prod.yaml (production)
services:
  app:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
```

### 10. Common Service Patterns

```yaml
# Database with initialization
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]

# Redis with persistence
  redis:
    image: redis:alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data

# MinIO (S3-compatible)
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data

# Traefik reverse proxy
  traefik:
    image: traefik:v3.0
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

## CLI Commands

```bash
# Start services
docker compose up                    # Foreground
docker compose up -d                 # Detached
docker compose up --build            # Rebuild images
docker compose up -d --force-recreate # Recreate containers

# Stop services
docker compose down                  # Stop and remove
docker compose down -v               # Also remove volumes
docker compose down --rmi all        # Also remove images

# Service management
docker compose ps                    # List containers
docker compose logs                  # View logs
docker compose logs -f api           # Follow specific service
docker compose exec api sh           # Shell into container
docker compose run --rm api npm test # Run one-off command

# Build
docker compose build                 # Build all
docker compose build api             # Build specific

# Scale
docker compose up -d --scale api=3   # Scale service

# Configuration
docker compose config                # Validate and view
docker compose config --services     # List services

# Multiple files
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

## Project Patterns

### Development Environment
```
project/
├── compose.yaml           # Base configuration
├── compose.override.yaml  # Dev overrides (auto-loaded)
├── compose.prod.yaml      # Production overrides
├── .env                   # Environment variables
├── .env.example           # Template for .env
└── services/
    ├── api/
    │   └── Dockerfile
    └── web/
        └── Dockerfile
```

### Microservices
```yaml
services:
  gateway:
    image: kong:latest
    depends_on:
      - user-service
      - order-service
    networks:
      - public
      - internal

  user-service:
    build: ./services/user
    networks:
      - internal
    environment:
      DATABASE_URL: postgres://user-db:5432/users

  order-service:
    build: ./services/order
    networks:
      - internal

networks:
  public:
  internal:
    internal: true
```

## Best Practices

1. **Use Named Volumes**: For persistent data, prefer named volumes over bind mounts
2. **Health Checks**: Always define health checks for dependencies
3. **Environment Files**: Use `.env` files for configuration
4. **Override Files**: Use `compose.override.yaml` for development
5. **Resource Limits**: Set memory and CPU limits in production
6. **Networks**: Isolate services with custom networks
7. **Version Control**: Commit compose files, not `.env` with secrets

## Troubleshooting

### Container Won't Start
```bash
docker compose logs <service>        # Check logs
docker compose config                # Validate syntax
docker compose ps -a                 # Show stopped containers
```

### Network Issues
```bash
docker network ls                    # List networks
docker network inspect <network>     # Show connected containers
docker compose exec api ping db      # Test connectivity
```

### Volume Issues
```bash
docker volume ls                     # List volumes
docker volume inspect <volume>       # Show mount point
docker compose down -v               # Remove volumes
```

### Port Conflicts
```bash
lsof -i :3000                        # Find process using port
docker compose ps --format json | jq '.[] | .Publishers'
```

## Resources

- **Documentation**: https://docs.docker.com/compose/
- **Compose Spec**: https://compose-spec.io/
- **Reference**: https://docs.docker.com/compose/compose-file/
- **Best Practices**: https://docs.docker.com/develop/dev-best-practices/
