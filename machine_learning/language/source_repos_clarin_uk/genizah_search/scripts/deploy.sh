#!/bin/bash

# Deployment script for MacBook Pro
# This script handles container updates and deployment

set -e

# Configuration
PROJECT_DIR="/Users/isaac/Documents/GitHub/genizah_search"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_FILE="$PROJECT_DIR/deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    log "Docker is running"
}

# Function to backup current data
backup_data() {
    log "Creating backup of current data..."
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Backup Elasticsearch data
    if [ -d "$PROJECT_DIR/backups/elasticsearch" ]; then
        cp -r "$PROJECT_DIR/backups/elasticsearch" "$BACKUP_DIR/elasticsearch-$(date +%Y%m%d-%H%M%S)"
        log "Elasticsearch data backed up"
    fi
    
    # Backup logs
    if [ -d "$PROJECT_DIR/logs" ]; then
        cp -r "$PROJECT_DIR/logs" "$BACKUP_DIR/logs-$(date +%Y%m%d-%H%M%S)"
        log "Logs backed up"
    fi
}

# Function to pull and deploy new images
deploy_images() {
    local backend_image="$1"
    local frontend_image="$2"
    
    log "Pulling new images..."
    
    # Pull backend image
    if ! docker pull "$backend_image"; then
        error "Failed to pull backend image: $backend_image"
        exit 1
    fi
    
    # Pull frontend image
    if ! docker pull "$frontend_image"; then
        error "Failed to pull frontend image: $frontend_image"
        exit 1
    fi
    
    log "Images pulled successfully"
    
    # Tag images for docker-compose
    docker tag "$backend_image" genizah_search-backend:latest
    docker tag "$frontend_image" genizah_search-frontend:latest
    
    log "Images tagged for docker-compose"
}

# Function to stop and start services
restart_services() {
    log "Stopping existing services..."
    cd "$PROJECT_DIR"
    
    # Stop services gracefully
    docker-compose down --timeout 30
    
    log "Starting new services..."
    
    # Start services
    if ! docker-compose up -d; then
        error "Failed to start services"
        exit 1
    fi
    
    log "Services started successfully"
}

# Function to check service health
check_health() {
    log "Checking service health..."
    
    # Wait for services to be ready
    sleep 10
    
    # Check backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "Backend is healthy"
    else
        warning "Backend health check failed"
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log "Frontend is healthy"
    else
        warning "Frontend health check failed"
    fi
    
    # Check Elasticsearch
    if curl -f http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        log "Elasticsearch is healthy"
    else
        warning "Elasticsearch health check failed"
    fi
}

# Function to clean up old images
cleanup() {
    log "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove unused images (keep last 3 versions)
    docker images --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | \
    grep -E "(genizah_search|ghcr.io)" | \
    tail -n +4 | \
    awk '{print $1}' | \
    xargs -r docker rmi || true
    
    log "Cleanup completed"
}

# Function to show deployment status
show_status() {
    log "Deployment Status:"
    echo "=================="
    docker-compose ps
    echo ""
    echo "Recent deployments:"
    tail -5 "$LOG_FILE" 2>/dev/null || echo "No deployment log found"
}

# Main deployment function
deploy() {
    local backend_image="$1"
    local frontend_image="$2"
    
    if [ -z "$backend_image" ] || [ -z "$frontend_image" ]; then
        error "Usage: $0 <backend_image> <frontend_image>"
        exit 1
    fi
    
    log "Starting deployment..."
    log "Backend image: $backend_image"
    log "Frontend image: $frontend_image"
    
    check_docker
    backup_data
    deploy_images "$backend_image" "$frontend_image"
    restart_services
    check_health
    cleanup
    
    log "Deployment completed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    "deploy")
        deploy "$2" "$3"
        ;;
    "status")
        show_status
        ;;
    "backup")
        backup_data
        ;;
    "cleanup")
        cleanup
        ;;
    "health")
        check_health
        ;;
    *)
        echo "Usage: $0 {deploy|status|backup|cleanup|health}"
        echo ""
        echo "Commands:"
        echo "  deploy <backend_image> <frontend_image>  - Deploy new images"
        echo "  status                                   - Show deployment status"
        echo "  backup                                   - Create backup of current data"
        echo "  cleanup                                  - Clean up old Docker images"
        echo "  health                                   - Check service health"
        exit 1
        ;;
esac
