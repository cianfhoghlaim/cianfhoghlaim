import os
import json
from pathlib import Path
import subprocess

def get_docker_compose_info(repo_path):
    # just find the compose file
    compose_path = repo_path / "docker-compose.yml"
    if not compose_path.exists():
        compose_path = repo_path / "docker-compose.yaml"
    if not compose_path.exists():
        compose_path = repo_path / "compose.yaml"
    if not compose_path.exists():
        return None
    with open(compose_path, 'r') as f:
        return f.read()

def convert_repo(category, repo_name, source_path, target_base):
    print(f"Processing {category}/{repo_name}...")
    compose_content = get_docker_compose_info(source_path)
    if not compose_content:
        print(f"  No compose file found for {repo_name}, skipping.")
        return

    target_dir = target_base / category / repo_name
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # We will write a basic compose.yaml that mirrors the original but stripped of secrets logic,
    # a sidecar.yaml, secrets.env, pangolin.yaml, blueprint.yaml
    # Since we can't reliably hit an LLM in this simple script without an API key setup, 
    # we will generate boilerplate that the user/subagents can refine.
    
    with open(target_dir / "compose.yaml", "w") as f:
        f.write(compose_content)
        
    sidecar_template = f"""services:
  locket:
    image: ghcr.io/bpbradley/locket:connect
    container_name: {repo_name}-locket
    restart: unless-stopped
    user: "65532:65532"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    environment:
      OP_CONNECT_HOST: ${{OP_CONNECT_HOST:-http://132.145.27.89:8080}}
    command:
      - "--connect-host=${{OP_CONNECT_HOST:-http://132.145.27.89:8080}}"
      - "--connect-token=file:/run/secrets/op_token"
      - "--map=/templates:/run/secrets/locket"
      - "--mode=${{LOCKET_MODE:-watch}}"
    secrets:
      - op_token
    volumes:
      - ./secrets.env:/templates/secrets.env:ro
      - stack-secrets:/run/secrets/locket
    healthcheck:
      test: ["CMD", "/locket", "healthcheck"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s
    networks:
      - stack

  # Replace 'main-service' with the actual name of the primary app container
  main-service:
    depends_on:
      locket:
        condition: service_healthy
    volumes:
      - stack-secrets:/run/secrets/locket:ro
    env_file:
      - /run/secrets/locket/secrets.env

secrets:
  op_token:
    file: ${{OP_CONNECT_TOKEN_FILE:-../../op_token}}

volumes:
  stack-secrets:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: uid=65532,gid=65532,mode=700
"""
    with open(target_dir / "sidecar.yaml", "w") as f:
        f.write(sidecar_template)

    secrets_template = f"""# {repo_name} secrets
# Replace with actual secret references
SERVICE_API_KEY={{{{ op://dev-baile/{repo_name}/api_key }}}}
"""
    with open(target_dir / "secrets.env", "w") as f:
        f.write(secrets_template)
        
    pangolin_template = f"""services:
  main-service:
    labels:
      - "pangolin.public-resources.{repo_name}.name={repo_name.capitalize()}"
      - "pangolin.public-resources.{repo_name}.full-domain={repo_name}.cianfhoghlaim.ie"
      - "pangolin.public-resources.{repo_name}.protocol=http"
      - "pangolin.public-resources.{repo_name}.targets[0].method=http"
      - "pangolin.public-resources.{repo_name}.targets[0].port=8080"
"""
    with open(target_dir / "pangolin.yaml", "w") as f:
        f.write(pangolin_template)

    blueprint_template = f"""public-resources:
  {repo_name}:
    name: "{repo_name.capitalize()}"
    full-domain: "{repo_name}.cianfhoghlaim.ie"
    protocol: "http"
    targets:
      - site: "arm1-oci"
        hostname: "{repo_name}-main"
        method: "http"
        port: 8080
"""
    with open(target_dir / "blueprint.yaml", "w") as f:
        f.write(blueprint_template)


def main():
    base_dir = Path("/Users/cliste/dev/cianfhoghlaim/stacks")
    target_base = Path("/Users/cliste/dev/cianfhoghlaim/sruth/bonneagar/stacks")
    
    for category_path in base_dir.iterdir():
        if not category_path.is_dir() or category_path.name.startswith('.'):
            continue
        category = category_path.name
        for repo_path in category_path.iterdir():
            if not repo_path.is_dir() or repo_path.name.startswith('.'):
                continue
            repo_name = repo_path.name
            convert_repo(category, repo_name, repo_path, target_base)

if __name__ == "__main__":
    main()
