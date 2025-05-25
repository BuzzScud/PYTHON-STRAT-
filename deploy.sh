#!/bin/bash

# ICT Trading System Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

echo "=========================================="
echo "ICT Trading System Deployment Script"
echo "=========================================="

# Configuration
APP_NAME="ict-trading-system"
DOMAIN="${DOMAIN:-localhost}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_info "Prerequisites check passed!"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    mkdir -p data logs ssl
    chmod 755 data logs
}

# Generate SSL certificates (self-signed for development)
generate_ssl() {
    if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
        log_info "Generating SSL certificates..."
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}"
        chmod 600 ssl/key.pem ssl/cert.pem
    else
        log_info "SSL certificates already exist."
    fi
}

# Build and deploy
deploy() {
    log_info "Building and deploying application..."
    
    # Stop existing containers
    docker-compose down
    
    # Build new images
    docker-compose build --no-cache
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 30
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        log_info "Deployment successful!"
        log_info "Application is available at: https://${DOMAIN}"
    else
        log_error "Deployment failed. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check if the application responds
    if curl -f -k https://${DOMAIN}/health &> /dev/null; then
        log_info "Health check passed!"
    else
        log_warn "Health check failed. Application might still be starting up."
    fi
}

# Show status
show_status() {
    echo ""
    echo "=========================================="
    echo "Deployment Status"
    echo "=========================================="
    docker-compose ps
    echo ""
    echo "Application URL: https://${DOMAIN}"
    echo "Health Check: https://${DOMAIN}/health"
    echo ""
    echo "Useful commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop app:  docker-compose down"
    echo "  Restart:   docker-compose restart"
    echo "=========================================="
}

# Main deployment process
main() {
    log_info "Starting deployment for environment: ${ENVIRONMENT}"
    
    check_prerequisites
    create_directories
    generate_ssl
    deploy
    health_check
    show_status
    
    log_info "Deployment completed successfully!"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping application..."
        docker-compose down
        ;;
    "restart")
        log_info "Restarting application..."
        docker-compose restart
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        show_status
        ;;
    "clean")
        log_warn "This will remove all containers and volumes. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            docker-compose down -v
            docker system prune -f
            log_info "Cleanup completed."
        fi
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|clean}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy the application (default)"
        echo "  stop    - Stop the application"
        echo "  restart - Restart the application"
        echo "  logs    - View application logs"
        echo "  status  - Show deployment status"
        echo "  clean   - Remove all containers and volumes"
        exit 1
        ;;
esac
