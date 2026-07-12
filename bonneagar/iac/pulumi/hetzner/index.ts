import * as pulumi from "@pulumi/pulumi";
import * as hcloud from "@pulumi/hcloud";
import * as cloudflare from "@pulumi/cloudflare";

// =============================================================================
// HETZNER CAX41 - ARM Workload Server
// =============================================================================
// Provisions a Hetzner CAX41 ARM server for storage stack workloads.
// 16 ARM vCPU, 32 GB RAM, 320 GB NVMe, 20 TB traffic
//
// USAGE:
//   pulumi up --stack prod
// =============================================================================

const cfg = new pulumi.Config();
const serverName = cfg.get("serverName") ?? "cax41-workloads";
const location = cfg.get("location") ?? "fsn1"; // Falkenstein, Germany
const serverType = cfg.get("serverType") ?? "cax41";

// SSH key configuration
const sshPublicKey = cfg.require("sshPublicKey");
const sshKeyName = cfg.get("sshKeyName") ?? `${serverName}-ssh-key`;

// Cloudflare configuration (optional - for DNS records)
const cloudflareZoneId = cfg.get("cloudflareZoneId") ?? "";
const cloudflareDomain = cfg.get("cloudflareDomain") ?? "cianfhoghlaim.ie";

// =============================================================================
// SSH KEY
// =============================================================================
const sshKey = new hcloud.SshKey("ssh-key", {
    name: sshKeyName,
    publicKey: sshPublicKey,
});

// =============================================================================
// FIREWALL
// =============================================================================
const firewall = new hcloud.Firewall("firewall", {
    name: `${serverName}-fw`,
    rules: [
        // SSH
        {
            direction: "in",
            protocol: "tcp",
            port: "22",
            sourceIps: ["0.0.0.0/0", "::/0"],
            description: "SSH access",
        },
        // HTTP
        {
            direction: "in",
            protocol: "tcp",
            port: "80",
            sourceIps: ["0.0.0.0/0", "::/0"],
            description: "HTTP traffic",
        },
        // HTTPS
        {
            direction: "in",
            protocol: "tcp",
            port: "443",
            sourceIps: ["0.0.0.0/0", "::/0"],
            description: "HTTPS traffic",
        },
        // WireGuard (for Pangolin Newt)
        {
            direction: "in",
            protocol: "udp",
            port: "51820",
            sourceIps: ["0.0.0.0/0", "::/0"],
            description: "WireGuard VPN",
        },
        // Komodo Periphery (optional direct access)
        {
            direction: "in",
            protocol: "tcp",
            port: "8120",
            sourceIps: ["0.0.0.0/0", "::/0"],
            description: "Komodo Periphery",
        },
        // ICMP
        {
            direction: "in",
            protocol: "icmp",
            sourceIps: ["0.0.0.0/0", "::/0"],
            description: "ICMP ping",
        },
    ],
});

// =============================================================================
// SERVER
// =============================================================================
const userData = `#!/bin/bash
set -e

# Configure system for databases
echo 'vm.max_map_count=262144' >> /etc/sysctl.conf
echo 'vm.swappiness=1' >> /etc/sysctl.conf
echo 'net.core.somaxconn=65535' >> /etc/sysctl.conf
sysctl -p

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose plugin
apt-get update
apt-get install -y docker-compose-plugin

# Create directories for Komodo/Newt
mkdir -p /etc/komodo
mkdir -p /opt/newt
mkdir -p /etc/connect

# Add default user to docker group
usermod -aG docker root

echo "Hetzner CAX41 provisioning complete"
`;

const server = new hcloud.Server("server", {
    name: serverName,
    serverType: serverType,
    image: "ubuntu-24.04",
    location: location,
    sshKeys: [sshKey.id],
    userData: userData,
    firewallIds: [firewall.id.apply(id => parseInt(id))],
    publicNets: [{
        ipv4Enabled: true,
        ipv6Enabled: true,
    }],
    labels: {
        environment: "production",
        role: "workloads",
        managed_by: "pulumi",
    },
});

// =============================================================================
// CLOUDFLARE DNS (Optional)
// =============================================================================
// Create DNS records if Cloudflare zone is configured
const dnsRecords = cloudflareZoneId ? (() => {
    // Hetzner-specific subdomain
    const hetznerRecord = new cloudflare.Record("hetzner-dns", {
        zoneId: cloudflareZoneId,
        name: "hetzner",
        content: server.ipv4Address,
        type: "A",
        ttl: 300,
        proxied: false,
    });

    return { hetznerRecord };
})() : null;

// =============================================================================
// OUTPUTS
// =============================================================================
export const serverId = server.id;
export const serverName_out = server.name;
export const publicIp = server.ipv4Address;
export const publicIpv6 = server.ipv6Address;
export const location_out = server.location;
export const serverType_out = server.serverType;
export const sshHint = pulumi.interpolate`ssh root@${server.ipv4Address}`;
export const domain = cloudflareDomain;
export const dnsConfigured = !!dnsRecords;

// Status information
export const status = server.status;
export const datacenter = server.datacenter;
