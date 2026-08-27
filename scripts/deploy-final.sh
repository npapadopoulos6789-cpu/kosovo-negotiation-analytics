#!/usr/bin/env bash
# deploy-final.sh -- switch the frontend/backend/Caddy config from the
# IP-based URL to the real HTTPS domain (fixes mixed-content block), add
# www subdomain support, restart containers, reload Caddy, verify with
# curl checks. Idempotent -- safe to re-run.
#
# Run as root, from the repo root (the directory containing
# docker-compose.yml), inside your VPS SSH session.

set -euo pipefail

# ---------- config -- edit here if the domain ever changes ----------
DOMAIN="kosovo-negotiations-analytics.online"
WWW_DOMAIN="www.kosovo-negotiations-analytics.online"
API_URL="https://${DOMAIN}"
ENV_FILE="backend/.env"
CADDYFILE="/etc/caddy/Caddyfile"
CADDY_TMP="/tmp/Caddyfile.new.$$"

step() { printf '\n==> %s\n' "$1"; }
ok()   { printf '    OK: %s\n' "$1"; }

# ---------- sanity checks ----------
step "Sanity checks"

if [ "$(id -u)" -ne 0 ]; then
  printf 'ERROR: run this as root (sudo) -- needs to write %s and reload systemd.\n' "$CADDYFILE"
  exit 1
fi

if [ ! -f docker-compose.yml ]; then
  printf 'ERROR: docker-compose.yml not found in %s -- run this from the repo root.\n' "$(pwd)"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  printf 'ERROR: %s not found.\n' "$ENV_FILE"
  exit 1
fi

if ! command -v caddy >/dev/null 2>&1; then
  printf 'ERROR: caddy binary not found on PATH.\n'
  exit 1
fi

ok "root, repo root, backend/.env, caddy binary all present"

# ---------- 1. rebuild frontend with the real HTTPS domain baked in ----------
step "1/6 -- rebuild frontend image (VITE_API_URL=${API_URL})"

docker compose build --build-arg VITE_API_URL="$API_URL" frontend
ok "frontend image rebuilt"

# ---------- 2. update FRONTEND_URL in backend/.env (line-safe, no full rewrite) ----------
step "2/6 -- update FRONTEND_URL in ${ENV_FILE}"

cp "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d%H%M%S)"
ok "backup taken before touching ${ENV_FILE}"

if grep -q '^FRONTEND_URL=' "$ENV_FILE"; then
  sed -i "s|^FRONTEND_URL=.*|FRONTEND_URL=${API_URL}|" "$ENV_FILE"
  ok "existing FRONTEND_URL line replaced"
else
  printf '%s\n' "FRONTEND_URL=${API_URL}" >> "$ENV_FILE"
  ok "FRONTEND_URL line was missing, appended"
fi

grep '^FRONTEND_URL=' "$ENV_FILE"

# ---------- 3. restart containers with the new image + new env ----------
step "3/6 -- restart containers (api picks up new FRONTEND_URL, frontend picks up new image)"

# NOT "up -d --build" on purpose -- that would re-trigger a frontend build
# through docker-compose.yml's own (arg-less) build config and silently
# overwrite the image built in step 1 with the localhost:8000 default.
# The image from step 1 is already correct; --force-recreate just makes
# both containers pick it up / re-read backend/.env, without rebuilding.
docker compose up -d --force-recreate api frontend
ok "api + frontend containers recreated"

# ---------- 4. rewrite /etc/caddy/Caddyfile (bare domain + www) ----------
step "4/6 -- write new Caddyfile (adds ${WWW_DOMAIN})"

printf '%s\n' \
  "${DOMAIN}, ${WWW_DOMAIN} {" \
  '    handle /docs* {' \
  '        reverse_proxy localhost:8000' \
  '    }' \
  '    handle /openapi.json {' \
  '        reverse_proxy localhost:8000' \
  '    }' \
  '    handle /countries* {' \
  '        reverse_proxy localhost:8000' \
  '    }' \
  '    handle /indicators* {' \
  '        reverse_proxy localhost:8000' \
  '    }' \
  '    handle /negotiation-events* {' \
  '        reverse_proxy localhost:8000' \
  '    }' \
  '    handle /negotiation-analyses* {' \
  '        reverse_proxy localhost:8000' \
  '    }' \
  '    handle /synthesis* {' \
  '        reverse_proxy localhost:8000' \
  '    }' \
  '    handle /compare* {' \
  '        reverse_proxy localhost:8000' \
  '    }' \
  '    handle /auth* {' \
  '        reverse_proxy localhost:8000' \
  '    }' \
  '    handle /analytics* {' \
  '        reverse_proxy localhost:8000' \
  '    }' \
  '    handle {' \
  '        reverse_proxy localhost:3000' \
  '    }' \
  '}' \
  > "$CADDY_TMP"

if ! caddy validate --config "$CADDY_TMP" --adapter caddyfile; then
  printf 'ERROR: new Caddyfile failed validation -- old %s left untouched.\n' "$CADDYFILE"
  rm -f "$CADDY_TMP"
  exit 1
fi
ok "new Caddyfile passed 'caddy validate'"

if [ -f "$CADDYFILE" ]; then
  cp "$CADDYFILE" "${CADDYFILE}.bak.$(date +%Y%m%d%H%M%S)"
  ok "backup taken of previous Caddyfile"
fi

mv "$CADDY_TMP" "$CADDYFILE"
ok "${CADDYFILE} written"

# ---------- 5. reload caddy ----------
step "5/6 -- reload caddy"

systemctl reload caddy
ok "caddy reloaded"

# ---------- 6. verify ----------
step "6/6 -- curl checks"

pass_count=0
fail_count=0

check_url() {
  local url="$1"
  local must_contain="${2:-}"
  local body status

  body="$(curl -sk -o - -w '\n%{http_code}' "$url" 2>/dev/null || true)"
  status="$(printf '%s' "$body" | tail -n1)"
  body="$(printf '%s' "$body" | sed '$d')"

  if [ "$status" != "200" ]; then
    printf '[FAIL] %s -> HTTP %s (expected 200)\n' "$url" "$status"
    fail_count=$((fail_count + 1))
    return
  fi

  if [ -n "$must_contain" ] && ! printf '%s' "$body" | grep -q "$must_contain"; then
    printf '[FAIL] %s -> HTTP 200 but body did not contain "%s"\n' "$url" "$must_contain"
    fail_count=$((fail_count + 1))
    return
  fi

  printf '[PASS] %s -> HTTP 200%s\n' "$url" "$([ -n "$must_contain" ] && printf ' (found "%s")' "$must_contain")"
  pass_count=$((pass_count + 1))
}

check_url "https://${DOMAIN}/docs"
check_url "https://${WWW_DOMAIN}"
check_url "https://${DOMAIN}/countries" "Serbia"

printf '\n%d passed, %d failed.\n' "$pass_count" "$fail_count"

if [ "$fail_count" -gt 0 ]; then
  exit 1
fi

printf '\nAll checks passed.\n'
