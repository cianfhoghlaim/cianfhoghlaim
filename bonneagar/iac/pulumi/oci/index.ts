import * as pulumi from "@pulumi/pulumi";
import * as oci from "@pulumi/oci";
import * as cloudflare from "@pulumi/cloudflare";

// This program provisions an ARM-based OCI instance (VM.Standard.A1.Flex) with 4 OCPUs and 24 GB RAM.
// Networking can be bootstrapped if a subnet OCID is not provided.
// Cloudflare DNS records are created to point the domain to the instance.

const cfg = new pulumi.Config();
const compartmentOcid = cfg.require("compartmentOcid");
const sshPublicKey = cfg.require("sshPublicKey");
const maybeSubnetOcid = cfg.get("subnetOcid");
const maybeAd = cfg.get("availabilityDomain");
const maybeImageOcid = cfg.get("imageOcid");
const allowedSshCidr = cfg.get("allowedSshCidr") ?? "0.0.0.0/0"; // For demo; restrict in production.

// Cloudflare configuration
const cloudflareConfig = new pulumi.Config("cloudflare");
const cloudflareDomain = cfg.get("cloudflareDomain") ?? "cianfhoghlaim.ie";
const cloudflareZoneId = cfg.get("cloudflareZoneId") ?? ""; // Set via config or env

// Get availability domain if not provided
const availabilityDomain = maybeAd
    ? pulumi.output(maybeAd)
    : oci.identity.getAvailabilityDomainsOutput({
          compartmentId: compartmentOcid,
      }).apply(ads => ads.availabilityDomains[0].name);

// Optional networking bootstrap if subnet OCID isn't provided.
let subnetId: pulumi.Output<string>;

if (!maybeSubnetOcid) {
    // Create VCN 10.0.0.0/16
    const vcn = new oci.core.Vcn("arm-free-vcn", {
        compartmentId: compartmentOcid,
        cidrBlock: "10.0.0.0/16",
        displayName: pulumi.interpolate`${pulumi.getProject()}-${pulumi.getStack()}-vcn`,
        dnsLabel: pulumi.getStack().replace(/[^a-z0-9]/g, "").slice(0, 15) || "stackvcn",
    });

    // Internet Gateway
    const igw = new oci.core.InternetGateway("arm-free-igw", {
        compartmentId: compartmentOcid,
        vcnId: vcn.id,
        displayName: pulumi.interpolate`${pulumi.getProject()}-${pulumi.getStack()}-igw`,
        enabled: true,
    });

    // Route Table with default route to IGW
    const routeTable = new oci.core.RouteTable("arm-free-rt", {
        compartmentId: compartmentOcid,
        vcnId: vcn.id,
        displayName: pulumi.interpolate`${pulumi.getProject()}-${pulumi.getStack()}-rt`,
        routeRules: [{
            networkEntityId: igw.id,
            destinationType: "CIDR_BLOCK",
            destination: "0.0.0.0/0",
        }],
    });

    // Security List - Pangolin required ports: 80, 443, 51820, 21820
    // See: https://docs.pangolin.net/self-host/quick-install
    const secList = new oci.core.SecurityList("arm-free-sl", {
        compartmentId: compartmentOcid,
        vcnId: vcn.id,
        displayName: pulumi.interpolate`${pulumi.getProject()}-${pulumi.getStack()}-sl`,
        egressSecurityRules: [{
            protocol: "all",
            destination: "0.0.0.0/0",
        }],
        ingressSecurityRules: [
            // SSH (for management)
            {
                protocol: "6", // TCP
                source: allowedSshCidr,
                tcpOptions: {
                    min: 22,
                    max: 22,
                },
            },
            // HTTP
            {
                protocol: "6",
                source: "0.0.0.0/0",
                tcpOptions: {
                    min: 80,
                    max: 80,
                },
            },
            // HTTPS
            {
                protocol: "6",
                source: "0.0.0.0/0",
                tcpOptions: {
                    min: 443,
                    max: 443,
                },
            },
            // WireGuard server (UDP)
            {
                protocol: "17", // UDP
                source: "0.0.0.0/0",
                udpOptions: {
                    min: 51820,
                    max: 51820,
                },
            },
            // WireGuard clients (UDP)
            {
                protocol: "17", // UDP
                source: "0.0.0.0/0",
                udpOptions: {
                    min: 21820,
                    max: 21820,
                },
            },
            // ICMP ping
            { protocol: "1", source: "0.0.0.0/0" },
        ],
    });

    // Public Subnet 10.0.1.0/24
    const subnet = new oci.core.Subnet("arm-free-subnet", {
        compartmentId: compartmentOcid,
        vcnId: vcn.id,
        cidrBlock: "10.0.1.0/24",
        displayName: pulumi.interpolate`${pulumi.getProject()}-${pulumi.getStack()}-subnet`,
        routeTableId: routeTable.id,
        securityListIds: [secList.id],
        prohibitPublicIpOnVnic: false,
        dnsLabel: "pubsubnet",
    });

    subnetId = subnet.id;
} else {
    subnetId = pulumi.output(maybeSubnetOcid);
}

// Lookup Ubuntu 22.04 aarch64 image if not provided
const imageId = maybeImageOcid
    ? pulumi.output(maybeImageOcid)
    : oci.core.getImagesOutput({
          compartmentId: compartmentOcid,
          shape: "VM.Standard.A1.Flex",
          operatingSystem: "Canonical Ubuntu",
      }).apply(images => {
          // Filter for Ubuntu 22.04 ARM images
          const ubuntuImage = images.images.find(
              img => /Ubuntu.*22\.04|Jammy/i.test(img.displayName) && /aarch64|ARM/i.test(img.displayName)
          );
          if (ubuntuImage) return ubuntuImage.id;

          // Fallback to any ARM Ubuntu image
          const anyUbuntu = images.images.find(
              img => /aarch64|ARM/i.test(img.displayName)
          );
          if (anyUbuntu) return anyUbuntu.id;

          throw new Error("No compatible ARM Ubuntu image found for VM.Standard.A1.Flex. Provide imageOcid.");
      });

// Create the instance
const instance = new oci.core.Instance("arm-free-instance", {
    compartmentId: compartmentOcid,
    availabilityDomain: availabilityDomain,
    displayName: pulumi.interpolate`${pulumi.getProject()}-${pulumi.getStack()}-arm-a1`,
    shape: "VM.Standard.A1.Flex",
    shapeConfig: {
        ocpus: 4,
        memoryInGbs: 24,
    },
    // Assign public IP in the selected subnet
    createVnicDetails: {
        subnetId: subnetId,
        assignPublicIp: "true",
        hostnameLabel: pulumi.getStack().replace(/[^a-z0-9]/g, "").slice(0, 63) || "armhost",
    },
    metadata: {
        ssh_authorized_keys: sshPublicKey,
    },
    sourceDetails: {
        sourceType: "image",
        sourceId: imageId,
        bootVolumeSizeInGbs: "200", // 200GB for infrastructure stack
    },
});

// =============================================================================
// CLOUDFLARE DNS RECORDS
// =============================================================================
// Create DNS records pointing the domain to the instance public IP.
// Requires CLOUDFLARE_API_TOKEN environment variable.

// Only create DNS records if zone ID is provided
const dnsRecords = cloudflareZoneId ? (() => {
    // Wildcard A record for *.cianfhoghlaim.ie
    const wildcardRecord = new cloudflare.Record("wildcard-dns", {
        zoneId: cloudflareZoneId,
        name: "*",
        content: instance.publicIp,
        type: "A",
        ttl: 300,
        proxied: false, // Direct connection needed for WireGuard/SSH
    });

    // Root domain A record
    const rootRecord = new cloudflare.Record("root-dns", {
        zoneId: cloudflareZoneId,
        name: "@",
        content: instance.publicIp,
        type: "A",
        ttl: 300,
        proxied: false,
    });

    return { wildcardRecord, rootRecord };
})() : null;

// Outputs
export const instanceOcid = instance.id;
export const publicIp = instance.publicIp;
export const privateIp = instance.privateIp;
export const availabilityDomainOut = instance.availabilityDomain;
export const sshHint = pulumi.interpolate`ssh ubuntu@${publicIp}`;
export const subnetIdOut = subnetId;
export const domain = cloudflareDomain;
export const dnsConfigured = !!dnsRecords;
