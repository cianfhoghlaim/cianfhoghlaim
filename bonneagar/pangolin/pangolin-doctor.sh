#!/usr/bin/env bash
# =============================================================================
# pangolin-doctor — assert the invariants that private resources depend on
# =============================================================================
# Every check here corresponds to a failure that actually happened in this
# deployment. They are cheap, read-only, and safe to run any time.
#
#   1  Resource bound to at least one ONLINE site
#   2  Destination reachable FROM NEWT (not from your shell)
#   3  Association cache populated for granted clients
#   4  Grants resolve to real users / clients
#   5  Blueprint file matches live state (drift)
#   6  Image tags pinned, not floating
#   7  Locket sidecars healthy and secrets volume populated
#
# USAGE
#   ./pangolin-doctor.sh                 # all checks
#   ./pangolin-doctor.sh 1 2 7           # selected checks
#
# ENVIRONMENT
#   PANGOLIN_SSH    ssh target for the control plane   (default oci.arm1)
#   PANGOLIN_DB     path to db.sqlite on that host
#   NEWT_CONTAINER  local newt container name          (default newt)
#   BLUEPRINT       blueprint file for the drift check
#
# EXIT: 0 all passed, 1 one or more FAILed. WARN does not fail the run.
# =============================================================================
set -uo pipefail

SSH_TARGET="${PANGOLIN_SSH:-oci.arm1}"
DB="${PANGOLIN_DB:-/opt/pangolin/config/db/db.sqlite}"
NEWT="${NEWT_CONTAINER:-newt}"
BLUEPRINT="${BLUEPRINT:-$(dirname "$0")/private-resources.blueprint.yaml}"

PASS=0; FAIL=0; WARN=0
ok()   { printf '  \033[32mPASS\033[0m  %s\n' "$1"; PASS=$((PASS+1)); }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; FAIL=$((FAIL+1)); }
warn() { printf '  \033[33mWARN\033[0m  %s\n' "$1"; WARN=$((WARN+1)); }
hdr()  { printf '\n\033[1m%s\033[0m\n' "$1"; }

# -n: never read stdin. Without it, ssh inside a while-read loop swallows the
# remaining rows and only the first record is ever processed.
q() { ssh -n -o BatchMode=yes "$SSH_TARGET" "sudo sqlite3 -noheader -separator '|' $DB \"$1\"" 2>/dev/null; }

SELECTED=("$@")
# No arguments = run everything; otherwise run only the numbered checks given.
run_check() {
  local id="$1"; shift
  if [[ ${#SELECTED[@]} -eq 0 ]] || [[ " ${SELECTED[*]} " == *" $id "* ]]; then
    "$@"
  fi
}

# -----------------------------------------------------------------------------
check_sites_online() {
  hdr "1. Resources bound to an online site"
  local rows
  rows="$(q "select sr.niceId, coalesce(group_concat(s.name),''), coalesce(sum(s.online),0) from siteResources sr left join siteNetworks sn on sn.networkId = sr.networkId left join sites s on s.siteId = sn.siteId where sr.enabled = 1 group by sr.siteResourceId")"
  [[ -z "$rows" ]] && { warn "no enabled site resources found"; return; }
  while IFS='|' read -r nice sites online; do
    [[ -z "$nice" ]] && continue
    if [[ "${online:-0}" -ge 1 ]]; then
      ok "$nice → ${sites:-?} (online)"
    else
      bad "$nice → ${sites:-<no site>} is OFFLINE; resource is unreachable"
    fi
  done <<< "$rows"
}

# -----------------------------------------------------------------------------
check_newt_reachability() {
  hdr "2. Destinations reachable from newt"
  if ! docker ps --format '{{.Names}}' | grep -qx "$NEWT"; then
    warn "container '$NEWT' not running locally; skipping (run on the workload host)"
    return
  fi
  local rows; rows="$(q "select niceId, destination, destinationPort from siteResources where enabled=1 and mode='http'")"
  [[ -z "$rows" ]] && { warn "no http resources to test"; return; }
  while IFS='|' read -r nice dest port; do
    [[ -z "$nice" ]] && continue
    local code
    code="$(docker exec "$NEWT" sh -c \
      "wget -q -O /dev/null -T 6 -S http://$dest:$port/ 2>&1 | grep -m1 'HTTP/' | awk '{print \$2}'" 2>/dev/null)"
    if [[ -n "$code" ]]; then
      ok "$nice → $dest:$port (HTTP $code)"
    else
      # A resource on a remote site is expected to be unreachable from THIS newt.
      warn "$nice → $dest:$port unreachable from this newt (expected if it is served by another site)"
    fi
  done <<< "$rows"
}

# -----------------------------------------------------------------------------
check_assoc_cache() {
  hdr "3. Association cache populated"
  local rows; rows="$(q "select sr.niceId, (select count(*) from clientSiteResourcesAssociationsCache c where c.siteResourceId = sr.siteResourceId), (select count(*) from userSiteResources u where u.siteResourceId = sr.siteResourceId), (select count(*) from roleSiteResources r where r.siteResourceId = sr.siteResourceId) from siteResources sr where sr.enabled = 1")"
  while IFS='|' read -r nice cached users roles; do
    [[ -z "$nice" ]] && continue
    if [[ "${cached:-0}" -gt 0 ]]; then
      ok "$nice — $cached client association(s)"
    elif [[ "${users:-0}" -eq 0 && "${roles:-0}" -eq 0 ]]; then
      warn "$nice — no grants at all (admin-only access)"
    else
      bad "$nice — has grants but EMPTY association cache (stale: re-apply the blueprint, do not hand-edit the DB)"
    fi
  done <<< "$rows"
}

# -----------------------------------------------------------------------------
check_grants_resolve() {
  hdr "4. Grants resolve to real users and clients"
  local orphan_u orphan_c
  orphan_u="$(q 'select count(*) from userSiteResources us left join user u on u.id = us.userId where u.id is null')"
  orphan_c="$(q 'select count(*) from clientSiteResources cs left join clients c on c.clientId = cs.clientId where c.clientId is null')"
  [[ "${orphan_u:-0}" -eq 0 ]] && ok "no user grants pointing at missing accounts" \
                               || bad "$orphan_u user grant(s) reference a non-existent account"
  [[ "${orphan_c:-0}" -eq 0 ]] && ok "no client grants pointing at missing clients" \
                               || bad "$orphan_c client grant(s) reference a non-existent client"

  local admin_rows
  admin_rows="$(q 'select count(*) from roleSiteResources rsr join roles r on r.roleId = rsr.roleId where r.isAdmin = 1')"
  [[ "${admin_rows:-0}" -eq 0 ]] && ok "no inert Admin role grants" \
                                 || warn "$admin_rows Admin role grant(s) present — inert; admin access is implicit"
}

# -----------------------------------------------------------------------------
check_blueprint_drift() {
  hdr "5. Blueprint matches live state"
  [[ -f "$BLUEPRINT" ]] || { warn "blueprint not found: $BLUEPRINT"; return; }
  command -v python3 >/dev/null || { warn "python3 not available; skipping"; return; }

  local declared; declared="$(python3 -c '
import sys, yaml
d = yaml.safe_load(open(sys.argv[1])) or {}
sec = d.get("private-resources") or d.get("client-resources") or {}
for k, v in sec.items():
    print("%s|%s|%s" % (k, v.get("destination",""), v.get("destination-port","")))
' "$BLUEPRINT" 2>/dev/null)"
  [[ -z "$declared" ]] && { warn "no private-resources declared in blueprint"; return; }

  while IFS='|' read -r nice dest port; do
    [[ -z "$nice" ]] && continue
    local live; live="$(q "select destination||'|'||destinationPort from siteResources where niceId='$nice'")"
    if [[ -z "$live" ]]; then
      bad "$nice declared in blueprint but ABSENT live (never applied?)"
    elif [[ "$live" == "$dest|$port" ]]; then
      ok "$nice matches live ($dest:$port)"
    else
      bad "$nice DRIFT — blueprint says $dest:$port, live is $live"
    fi
  done <<< "$declared"

  # live resources with no blueprint entry = unmanaged
  local live_all; live_all="$(q 'select niceId from siteResources where enabled=1')"
  while read -r ln; do
    [[ -z "$ln" ]] && continue
    grep -q "^$ln|" <<< "$declared" || warn "$ln exists live but is NOT in the blueprint (unmanaged)"
  done <<< "$live_all"
}

# -----------------------------------------------------------------------------
check_pinned_images() {
  hdr "6. Image tags pinned"
  local imgs; imgs="$(ssh -o BatchMode=yes "$SSH_TARGET" \
    'sudo docker inspect pangolin gerbil traefik --format "{{.Name}} {{.Config.Image}}" 2>/dev/null' 2>/dev/null)"
  if [[ -n "$imgs" ]]; then
    while read -r name image; do
      [[ -z "$image" ]] && continue
      if [[ "$image" == *:latest || "$image" == *:ee-latest || "$image" != *:* ]]; then
        bad "${name#/} uses floating tag '$image' — pin it"
      else
        ok "${name#/} pinned: $image"
      fi
    done <<< "$imgs"
  else
    warn "could not inspect control-plane images"
  fi

  if docker ps --format '{{.Names}}' | grep -qx "$NEWT"; then
    local ni; ni="$(docker inspect "$NEWT" --format '{{.Config.Image}}')"
    [[ "$ni" == *:latest || "$ni" != *:* ]] && bad "newt uses floating tag '$ni'" || ok "newt pinned: $ni"
  fi
}

# -----------------------------------------------------------------------------
check_locket_health() {
  hdr "7. Locket sidecars healthy and secrets populated"
  local found=0
  while read -r name; do
    [[ -z "$name" ]] && continue
    found=1
    local status; status="$(docker inspect "$name" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' 2>/dev/null)"
    local app="${name%-locket}"; app="${app##*_}"
    if [[ "$status" == "healthy" ]]; then
      ok "$name healthy"
    else
      bad "$name is '$status' — dependent stack will start without secrets"
    fi
    if docker ps --format '{{.Names}}' | grep -qx "$app"; then
      if docker exec "$app" sh -c 'ls /run/secrets/locket/ >/dev/null 2>&1' 2>/dev/null; then
        ok "$app has /run/secrets/locket populated"
      else
        bad "$app is MISSING /run/secrets/locket — secrets never injected"
      fi
    fi
  done <<< "$(docker ps --format '{{.Names}}' 2>/dev/null | grep -i locket || true)"
  [[ $found -eq 0 ]] && warn "no locket sidecars running locally"
}

# -----------------------------------------------------------------------------
echo "pangolin-doctor — control plane: $SSH_TARGET"
if ! q 'select 1' >/dev/null 2>&1; then
  echo "  FAIL  cannot read $DB on $SSH_TARGET" >&2; exit 1
fi

run_check 1 check_sites_online
run_check 2 check_newt_reachability
run_check 3 check_assoc_cache
run_check 4 check_grants_resolve
run_check 5 check_blueprint_drift
run_check 6 check_pinned_images
run_check 7 check_locket_health

printf '\n\033[1mSummary:\033[0m %d passed, %d failed, %d warnings\n' "$PASS" "$FAIL" "$WARN"
[[ $FAIL -eq 0 ]] || exit 1
