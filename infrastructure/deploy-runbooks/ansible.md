# Runbook: ansible

> Written for a future AI agent. Every snippet is shell-
> pasteable. **Do not auto-execute** — the agent must paste
> each snippet deliberately.

Ansible is the **provisioning automation** for the
infrastructure layer — it provisions new hosts (bare-metal
or cloud VPS) so the per-stack Docker Compose can take over
after the host is up. Ansible is not a runtime service.

## Pre-flight

```bash
# 0.1 — Verify the Ansible EE builder
command -v ansible-builder 2>/dev/null \
  || pip3 install ansible-builder ansible-core ansible-runner

# 0.2 — Verify the inventory
ls infrastructure/ansible/inventory/
# Expect: hosts (or a similar filename). If empty, populate it
# with the new arm1-oci host entry (see Step 1.1).

# 0.3 — Verify SSH key access
[ -f ~/.ssh/ansible_arm1_oci ] || {
  echo "ERROR: SSH key ~/.ssh/ansible_arm1_oci missing; generate with: ssh-keygen -t ed25519 -f ~/.ssh/ansible_arm1_oci"
  exit 1
}
ssh -i ~/.ssh/ansible_arm1_oci -o ConnectTimeout=5 arm1-oci 'true' \
  || { echo "ERROR: SSH key not installed on arm1-oci"; exit 2; }
```

## First-time deploy (provision a new arm1-oci from scratch)

```bash
# 1.1 — Populate the inventory
cat > infrastructure/ansible/inventory/hosts.yml <<'ANSIBLE_EOF'
all:
  vars:
    ansible_user: ubuntu
    ansible_ssh_private_key_file: ~/.ssh/ansible_arm1_oci
    ansible_python_interpreter: /usr/bin/python3.12
  children:
    control_plane:
      hosts:
        arm1-oci:
          ansible_host: <OCI-INSTANCE-IP>
          region: uk-london-1
          spec: 4_ocpu_24gb_arm
    workload:
      hosts:
        bunchloch:
          ansible_host: 127.0.0.1
          ansible_connection: local
ANSIBLE_EOF

# 1.2 — Build the Ansible execution environment
cd infrastructure/ansible
ansible-builder build --tag cianfhoghlaim-ee:latest --context . --file execution-environment.yml
cd -

# 1.3 — Run the site playbook (provisions the OCI host)
cd infrastructure/ansible
docker run --rm -it \
  -v "$PWD:/work" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  cianfhoghlaim-ee:latest \
  ansible-playbook -i inventory/hosts.yml playbooks/site.yml --diff
cd -

# 1.4 — Run the deploy-infrastructure playbook (installs docker,
#       komodo, pangolin, infisical — the 4 control-plane stacks)
cd infrastructure/ansible
docker run --rm -it \
  -v "$PWD:/work" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  cianfhoghlaim-ee:latest \
  ansible-playbook -i inventory/hosts.yml playbooks/deploy-infrastructure.yml --diff
cd -
```

## Verify

```bash
# 2.1 — The new arm1-oci is reachable + has docker
ssh arm1-oci 'docker info | head -5'
# Expected: Server Version: ...

# 2.2 — The 4 control-plane stacks are running
ssh arm1-oci 'docker ps --format "{{.Names}}" | sort'
# Expected: includes pangolin, gerbil, traefik, pocket-id, tinyauth,
#           middleware-manager, crowdsec, komodo-periphery, infisical

# 2.3 — The Komodo Periphery has connected to the Core on bunchloch
docker logs komodo-periphery 2>&1 | tail -20
# Expected: "Connected to Komodo Core", "Reachable at https://komodo.cianfhoghlaim.ie"

# 2.4 — The Pangolin UI is reachable at the public hostname
curl -I https://pangolin.cianfhoghlaim.ie/
# Expected: HTTP 200 (or 302 → Pocket ID SSO)
```

## Rollback

```bash
# 3.1 — Tear down the new arm1-oci (drains the host)
cd infrastructure/ansible
docker run --rm -it \
  -v "$PWD:/work" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  cianfhoghlaim-ee:latest \
  ansible-playbook -i inventory/hosts.yml playbooks/site.yml --tags drain --diff
cd -

# 3.2 — Optionally: destroy the OCI instance
# (Not part of Ansible; do this via the OCI console or the
#  OCI CLI: `oci compute instance terminate --instance-id <ocid>`)

# 3.3 — Remove the inventory entry
sed -i '/arm1-oci/,/^        bunchloch/d' infrastructure/ansible/inventory/hosts.yml
# Or use the OCI-specific group:
sed -i '/^    control_plane:/,/^    workload:/d' infrastructure/ansible/inventory/hosts.yml
```

## Last verified

- 2026-06-15: runbook drafted, no end-to-end provision
  executed. See `openspec/changes/audit-infrastructure-2026-06-15/proposal.md`
  for why deploy is deferred.
- The 4 known blockers from `infrastructure/stacks/HEALTH_REPORT.md`
  Session 3 (newt/pangolin version, 3 manual private resources,
  expired `PANGOLIN_API_KEY`, `komodo-locket` production
  credentials) all need fixing before the deploy succeeds.
