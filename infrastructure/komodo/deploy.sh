#!/bin/bash
# =============================================================================
# STORAGE STACK DEPLOYMENT SCRIPT
# =============================================================================
# Deploys the distributed storage stack across OCI, Hetzner, and MacBook.
#
# Prerequisites:
#   1. Pulumi CLI installed and configured
#   2. Hetzner API token in HCLOUD_TOKEN
#   3. Cloudflare API token in CLOUDFLARE_API_TOKEN
#   4. 1Password Connect running on OCI (132.145.27.89:8080)
#   5. SSH access to all servers
#
# Usage:
#   ./deploy.sh [phase]
#
# Phases:
#   hetzner   - Provision Hetzner CAX41 server only
#   sites     - Deploy Newt/Periphery on all sites
#   stacks    - Deploy storage stacks via Komodo
#   all       - Run all phases (default)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BONNEAGAR_DIR="$(dirname "$SCRIPT_DIR")"
PULUMI_DIR="$BONNEAGAR_DIR/pulumi"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

PHASE="${1:-all}"

# =============================================================================
# PHASE 1: Provision Hetzner CAX41
# =============================================================================
deploy_hetzner() {
    log_info "Phase 1: Provisioning Hetzner CAX41..."

    cd "$PULUMI_DIR/hetzner"

    # Install dependencies
    if [ ! -d "node_modules" ]; then
        log_info "Installing Pulumi dependencies..."
        npm install
    fi

    # Initialize stack if needed
    if ! pulumi stack ls 2>/dev/null | grep -q "prod"; then
        log_info "Creating Pulumi stack..."
        pulumi stack init prod
    fi

    pulumi stack select prod

    # Deploy
    log_info "Running pulumi up..."
    pulumi up --yes

    # Get outputs
    HETZNER_IP=$(pulumi stack output publicIp)
    log_success "Hetzner CAX41 provisioned at: $HETZNER_IP"

    # Wait for SSH
    log_info "Waiting for SSH to become available..."
    for i in {1..30}; do
        if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@"$HETZNER_IP" "echo ok" 2>/dev/null; then
            log_success "SSH is ready"
            break
        fi
        sleep 10
    done

    echo "$HETZNER_IP" > "$SCRIPT_DIR/.hetzner-ip"
}

# =============================================================================
# PHASE 2: Deploy Site Infrastructure (Newt + Periphery) via Ansible
# =============================================================================
deploy_sites() {
    log_info "Phase 2: Deploying site infrastructure via Ansible..."

    HETZNER_IP=$(cat "$SCRIPT_DIR/.hetzner-ip" 2>/dev/null || echo "")
    ANSIBLE_DIR="$BONNEAGAR_DIR/ansible"

    if [ -z "$HETZNER_IP" ]; then
        log_error "Hetzner IP not found. Run 'deploy.sh hetzner' first."
        exit 1
    fi

    # Export Hetzner IP for Ansible inventory
    export HETZNER_IP

    # Check for OP Connect token
    if [ ! -f "$HOME/.config/op/connect-token" ]; then
        log_warn "1Password Connect token not found at ~/.config/op/connect-token"
        log_warn "Ensure OP token is at /etc/connect/token on target hosts"
    fi

    # Deploy to Hetzner via Ansible
    log_info "Deploying site to Hetzner ($HETZNER_IP) via Ansible..."
    cd "$ANSIBLE_DIR"

    # First, copy OP token to Hetzner
    ssh root@"$HETZNER_IP" "mkdir -p /etc/connect"
    if [ -f "$HOME/.config/op/connect-token" ]; then
        scp "$HOME/.config/op/connect-token" root@"$HETZNER_IP":/etc/connect/token
    fi

    # Run Ansible playbook for Hetzner
    ansible-playbook -i inventory/komodo.yml playbooks/site.yml -l cax41-hetzner

    log_success "Hetzner site deployed"

    # Deploy to MacBook via Ansible
    log_info "Deploying site to MacBook (local) via Ansible..."

    # Ensure /etc/komodo exists (may need sudo)
    if [ ! -d "/etc/komodo" ]; then
        log_warn "Creating /etc/komodo (may require sudo)..."
        sudo mkdir -p /etc/komodo
        sudo chown -R "$(whoami)" /etc/komodo
    fi

    # Ensure /etc/connect exists
    if [ ! -d "/etc/connect" ]; then
        sudo mkdir -p /etc/connect
        sudo chown -R "$(whoami)" /etc/connect
    fi

    # Copy OP token locally if needed
    if [ -f "$HOME/.config/op/connect-token" ] && [ ! -f "/etc/connect/token" ]; then
        sudo cp "$HOME/.config/op/connect-token" /etc/connect/token
    fi

    ansible-playbook -i inventory/komodo.yml playbooks/site.yml -l bunchloch

    log_success "MacBook site deployed"
}

# =============================================================================
# PHASE 3: Deploy Storage Stacks via Komodo
# =============================================================================
deploy_stacks() {
    log_info "Phase 3: Deploying storage stacks via Komodo..."

    # This phase uses the Komodo CLI or API to deploy stacks
    # Requires km CLI to be installed and configured

    if ! command -v km &> /dev/null; then
        log_warn "Komodo CLI (km) not found. Using API instead..."

        # Alternative: Use curl to trigger procedure
        KOMODO_URL="https://komodo.cianfhoghlaim.ie"

        log_info "Triggering deploy-storage-stack procedure..."
        # This would need API key authentication
        # curl -X POST "$KOMODO_URL/api/execute/procedure/deploy-storage-stack"

        log_warn "Please run the deploy-storage-stack procedure from Komodo UI"
        log_info "URL: $KOMODO_URL"
    else
        log_info "Running deploy-storage-stack procedure..."
        km run procedure deploy-storage-stack --yes
    fi

    log_success "Storage stacks deployment initiated"
}

# =============================================================================
# MAIN
# =============================================================================
case "$PHASE" in
    hetzner)
        deploy_hetzner
        ;;
    sites)
        deploy_sites
        ;;
    stacks)
        deploy_stacks
        ;;
    all)
        deploy_hetzner
        deploy_sites
        deploy_stacks
        ;;
    *)
        echo "Usage: $0 [hetzner|sites|stacks|all]"
        exit 1
        ;;
esac

log_success "Deployment complete!"
echo ""
echo "Next steps:"
echo "  1. Fresh Pangolin deployment (if password forgotten):"
echo "     cd bonneagar/pangolin && docker compose down -v && docker compose up -d"
echo "  2. Create Newt sites in Pangolin UI: https://pangolin.cianfhoghlaim.ie"
echo "     - cax41-hetzner: Create site, save ID + Secret to 1Password"
echo "     - bunchloch: Create site, save ID + Secret to 1Password"
echo "  3. Add Newt credentials to 1Password (vault: dev-baile):"
echo "     - cax41-hetzner-newt: id, secret"
echo "     - bunchloch-newt: id, secret"
echo "  4. Verify servers appear in Komodo UI: https://komodo.cianfhoghlaim.ie"
echo "  5. Deploy stacks via Komodo procedures:"
echo "     - km run procedure deploy-hetzner"
echo "     - km run procedure deploy-macbook"
echo ""
