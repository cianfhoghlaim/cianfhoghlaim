# Bonneagar Ansible Playbooks

These playbooks orchestrate the core foundations of the cluster, deploying Pangolin Core, Komodo Core, and configuring remote site nodes with Newt & Periphery.

## Refactored Architecture (Komodo 2.x + Infisical)

We use **Ansible** to bootstrap the essential services needed for Komodo to take over the rest of the application deployment lifecycle.

*   **Secrets:** All roles natively utilize Infisical as the secrets backend. `ghcr.io/bpbradley/locket:infisical` operates as a Docker sidecar that seamlessly parses `secrets.env.j2` templates replacing `{{ infisical:///<SECRET_NAME> }}` variables into ephemeral tmpfs directories at runtime.
*   **Networking:** Periphery relies on the **Noise XX Protocol** and **Onboarding Keys**. Periphery dynamically phones home to the Komodo Core WSS interface over a Pangolin tunnel, completely removing the necessity for inbound firewall rules or overlay networking.

## Available Playbooks

### `deploy-infrastructure.yml`
Provisions the **Control Plane** (e.g., MacBook / Central Server).
```bash
ansible-playbook -i inventory/inventory.yml playbooks/deploy-infrastructure.yml
```
It deploys:
1.  **Pangolin Core**: Central reverse proxy and tunnel manager.
2.  **Komodo Core**: The orchestration control plane.

### `site.yml`
Provisions **Workload Nodes** (e.g., Oracle Cloud Free Tier).
```bash
ansible-playbook -i inventory/inventory.yml playbooks/site.yml
```
It deploys:
1.  **Newt**: The Pangolin client to establish secure connectivity back to Pangolin Core.
2.  **Komodo Periphery**: The execution agent for Komodo 2.x, using an outbound WSS connection back to Komodo Core.
3.  **Locket**: The Infisical sidecar syncing environment secrets locally.
