# Quick start — Mylar3 + qBittorrent (local)

## TL;DR
```bash
cd /Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar/stacks/mylar3
./start.sh                # both stacks in dev mode
```

For **production** (Locket + Infisical):
```bash
PRODUCTION=1 ./start.sh
```

## Prerequisites
- Docker running
- `compose.yaml` + `sidecar.yaml` present (already in this directory)
- `.env.local` (auto-copied from `.env.example` on first run; edit as needed)

## What the script does
1. Creates `.env.local` from `.env.example` if missing
2. Brings up `mylar3` (port 8090 → 127.0.0.1)
3. Brings up `qbittorrent-gluetun` (port 8080 → 127.0.0.1, requires VPN creds)

## Connecting the two
After both stacks are up, in the Mylar3 WebUI:
1. Settings → Download Clients → Add → qBittorrent
2. Host: `qbittorrent-gluetun` (Docker DNS)
3. Port: `8080`
4. Username: `admin`
5. Password: from Infisical `dev-baile/qbittorrent-gluetun/webui_password`

## Pangolin private resources
After both stacks are running, apply the blueprints to Pangolin Core:
```bash
export PANGOLIN_API_KEY='<apiKeyId>.<apiKeySecret>'
/Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar/pangolin/apply-blueprint.sh \
  /Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar/stacks/mylar3/blueprint.yaml
/Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar/pangolin/apply-blueprint.sh \
  /Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar/stacks/qbittorrent-gluetun/blueprint.yaml
```

Then `https://mylar3.cianfhoghlaim.ie` and `https://qbittorrent.cianfhoghlaim.ie`
become reachable from any device on the Pangolin mesh (Pocket ID SSO required).

## Health
```bash
docker ps --filter name=mylar3 --filter name=qbittorrent --filter name=gluetun
curl -fsS http://localhost:8090    # mylar3
curl -fsS http://localhost:8080    # qBittorrent
```
