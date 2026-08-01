#!/bin/bash
# =============================================================================
# PocketID Authentication Setup Helper
# =============================================================================
# This script helps generate secrets and validate PocketID configuration
# for the Aleyum Portal.
#
# Usage:
#   ./setup-auth.sh              # Generate secrets and show setup steps
#   ./setup-auth.sh --validate   # Validate current configuration
#   ./setup-auth.sh --test       # Test PocketID connectivity
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
POCKETID_ISSUER="${POCKETID_ISSUER:-https://auth.cianfhoghlaim.ie}"
PORTAL_URL="${AUTH_BASE_URL:-https://aleyum.cianfhoghlaim.ie}"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "========================================"
    echo "$1"
    echo "========================================"
    echo ""
}

# Generate random secret
generate_secret() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Validate PocketID connectivity
test_pocketid_connectivity() {
    print_header "Testing PocketID Connectivity"

    log_info "Checking PocketID at: $POCKETID_ISSUER"

    # Test basic connectivity
    if curl -s -f -o /dev/null -w "%{http_code}" "$POCKETID_ISSUER" | grep -q "200\|301\|302"; then
        log_success "PocketID is accessible"
    else
        log_error "Cannot reach PocketID at $POCKETID_ISSUER"
        return 1
    fi

    # Test OIDC discovery endpoint
    log_info "Testing OIDC discovery endpoint..."
    DISCOVERY_URL="${POCKETID_ISSUER}/.well-known/openid-configuration"

    if curl -s -f "$DISCOVERY_URL" > /dev/null 2>&1; then
        log_success "OIDC discovery endpoint is accessible"

        # Display endpoints
        log_info "Available endpoints:"
        curl -s "$DISCOVERY_URL" | jq -r '
            "  Authorization: " + .authorization_endpoint,
            "  Token: " + .token_endpoint,
            "  UserInfo: " + .userinfo_endpoint,
            "  JWKS: " + .jwks_uri
        ' 2>/dev/null || log_warning "Could not parse OIDC configuration"
    else
        log_warning "OIDC discovery endpoint not found (this might be okay if PocketID uses non-standard paths)"
    fi

    # Test health endpoint
    log_info "Testing health endpoint..."
    if curl -s -f "${POCKETID_ISSUER}/healthz" > /dev/null 2>&1; then
        log_success "PocketID health check passed"
    else
        log_warning "Health endpoint not available"
    fi

    return 0
}

# Validate environment configuration
validate_config() {
    print_header "Validating Configuration"

    local errors=0

    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_error ".env file not found"
        log_info "Create it from .env.example: cp .env.example .env"
        ((errors++))
    else
        log_success ".env file exists"

        # Source the .env file
        set -a
        source .env
        set +a

        # Check required variables
        log_info "Checking required environment variables..."

        check_var "POCKETID_CLIENT_ID" "$POCKETID_CLIENT_ID" || ((errors++))
        check_var "POCKETID_CLIENT_SECRET" "$POCKETID_CLIENT_SECRET" || ((errors++))
        check_var "POCKETID_ISSUER" "$POCKETID_ISSUER" || ((errors++))
        check_var "BETTER_AUTH_SECRET" "$BETTER_AUTH_SECRET" || ((errors++))
        check_var "AUTH_BASE_URL" "$AUTH_BASE_URL" || ((errors++))
        check_var "DATABASE_URL" "$DATABASE_URL" || ((errors++))

        # Validate URLs
        log_info "Validating URL formats..."
        if [[ "$POCKETID_ISSUER" =~ ^https?:// ]]; then
            log_success "POCKETID_ISSUER format is valid"
        else
            log_error "POCKETID_ISSUER must start with http:// or https://"
            ((errors++))
        fi

        if [[ "$AUTH_BASE_URL" =~ ^https?:// ]]; then
            log_success "AUTH_BASE_URL format is valid"
        else
            log_error "AUTH_BASE_URL must start with http:// or https://"
            ((errors++))
        fi
    fi

    # Check lib directory
    if [ -d "lib" ]; then
        log_success "lib directory exists"

        # Check auth files
        local auth_files=("lib/auth.ts" "lib/auth-client.ts" "lib/middleware.ts" "lib/utils.ts")
        for file in "${auth_files[@]}"; do
            if [ -f "$file" ]; then
                log_success "Found: $file"
            else
                log_error "Missing: $file"
                ((errors++))
            fi
        done
    else
        log_error "lib directory not found"
        ((errors++))
    fi

    echo ""
    if [ $errors -eq 0 ]; then
        log_success "Configuration validation passed!"
        return 0
    else
        log_error "Found $errors error(s)"
        return 1
    fi
}

check_var() {
    local var_name="$1"
    local var_value="$2"

    if [ -z "$var_value" ] || [ "$var_value" = "your-client-id" ] || [ "$var_value" = "your-client-secret" ] || [ "$var_value" = "your-better-auth-secret-min-32-chars" ]; then
        log_error "$var_name is not set or still has placeholder value"
        return 1
    else
        log_success "$var_name is set"
        return 0
    fi
}

# Generate secrets file
generate_secrets() {
    print_header "Generating Secrets"

    local BETTER_AUTH_SECRET=$(generate_secret)
    local POSTGRES_PASSWORD=$(generate_secret)

    log_info "Generated secrets:"
    echo ""
    echo "BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET"
    echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
    echo ""

    log_info "Add these to your .env file:"
    echo ""
    cat << EOF
# =============================================================================
# Generated Secrets
# =============================================================================
BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET
POSTGRES_PASSWORD=$POSTGRES_PASSWORD

# Database URL
DATABASE_URL=postgresql://postgres:$POSTGRES_PASSWORD@postgres:5432/aleyum_portal
EOF
    echo ""
}

# Show setup instructions
show_instructions() {
    print_header "PocketID Setup Instructions"

    cat << 'EOF'
Follow these steps to set up PocketID authentication:

1. REGISTER OIDC APPLICATION
   - Go to: https://auth.cianfhoghlaim.ie/admin
   - Navigate to: Settings > OIDC Applications > Create Application
   - Configure:
     * Application Name: Aleyum Portal
     * Redirect URI: https://aleyum.cianfhoghlaim.ie/api/auth/callback/oidc
     * Scopes: openid email profile groups

2. COPY CREDENTIALS
   - After creating, copy the Client ID and Client Secret
   - Add them to your .env file:
     POCKETID_CLIENT_ID=<your-client-id>
     POCKETID_CLIENT_SECRET=<your-client-secret>

3. GENERATE SECRETS
   - Run: ./setup-auth.sh
   - Copy the generated BETTER_AUTH_SECRET to your .env file

4. UPDATE ENVIRONMENT
   - Ensure all required variables are set in .env
   - Run: ./setup-auth.sh --validate

5. START SERVICES
   - Start PostgreSQL: docker compose up -d aleyum-db
   - Start portal: docker compose up -d aleyum-portal

6. TEST AUTHENTICATION
   - Go to: https://aleyum.cianfhoghlaim.ie/login
   - Click "Sign in with PocketID"
   - Complete passkey authentication

See POCKETID_SETUP.md for detailed documentation and troubleshooting.
EOF
}

# Main script
main() {
    print_header "PocketID Authentication Setup Helper"

    case "${1:-}" in
        --validate)
            validate_config
            ;;
        --test)
            test_pocketid_connectivity
            ;;
        --secrets)
            generate_secrets
            ;;
        --help)
            echo "Usage: $0 [OPTION]"
            echo ""
            echo "Options:"
            echo "  (no args)    Show setup instructions"
            echo "  --validate   Validate current configuration"
            echo "  --test       Test PocketID connectivity"
            echo "  --secrets    Generate secrets for .env file"
            echo "  --help       Show this help message"
            ;;
        *)
            show_instructions
            echo ""
            log_info "Quick commands:"
            echo "  $0 --secrets  # Generate secrets"
            echo "  $0 --validate # Validate configuration"
            echo "  $0 --test     # Test PocketID connectivity"
            ;;
    esac
}

main "$@"
