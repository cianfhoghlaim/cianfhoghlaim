# =============================================================================
# ANSIBLE KOMODO EXECUTION ENVIRONMENT - Multi-Architecture Build
# =============================================================================
# Builds an ARM64 + AMD64 compatible Ansible execution environment for
# deploying Komodo Periphery, Locket, and infrastructure stacks.
#
# Build command:
#   docker buildx build --platform linux/amd64,linux/arm64 \
#     --tag git.cianfhoghlaim.ie/cliste/ansible-komodo-ee:latest \
#     --push .
#
# Based on: ghcr.io/bpbradley/ansible/komodo-ee (amd64 only)
# =============================================================================

# syntax=docker/dockerfile:1
FROM --platform=$TARGETPLATFORM quay.io/fedora/fedora:42

ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG ANSIBLE_CORE_VERSION=2.19.0
ARG ANSIBLE_RUNNER_VERSION=2.4.1

LABEL maintainer="cliste"
LABEL org.opencontainers.image.source="https://git.cianfhoghlaim.ie/cliste/cianfhoghlaim"
LABEL org.opencontainers.image.description="Multi-arch Ansible Execution Environment for Komodo"

# Install system packages
RUN dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    openssh-clients \
    sshpass \
    less \
    rsync \
    git \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# Install Ansible and dependencies
RUN pip3 install --no-cache-dir \
    ansible-core==${ANSIBLE_CORE_VERSION} \
    ansible-runner==${ANSIBLE_RUNNER_VERSION} \
    jmespath \
    netaddr

# Copy and install Ansible collections/roles
COPY requirements.yml /tmp/requirements.yml
RUN ansible-galaxy collection install -r /tmp/requirements.yml --force \
    && ansible-galaxy role install -r /tmp/requirements.yml --force \
    && rm /tmp/requirements.yml

# Copy entrypoint and vault password script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY vault_pass.sh /etc/ansible/vault_pass.sh
RUN chmod +x /usr/local/bin/entrypoint.sh /etc/ansible/vault_pass.sh

# Set up working directory
WORKDIR /ansible

# Entrypoint handles vault password setup
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]
