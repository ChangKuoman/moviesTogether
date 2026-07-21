#!/usr/bin/env bash
# Sets up (or updates) the MoviesTogether backend on this VM. Safe to re-run - use it both for
# the first deploy and for every redeploy after a `git pull` (installs/updates deps, creates
# .env with fresh secrets only if one doesn't already exist, reinstalls the systemd service and
# Caddy config, then restarts everything).
#
# Usage: run from anywhere, as root, after the repo has been cloned to /opt/moviestogether:
#   cd /opt/moviestogether && sudo bash deploy/setup-backend.sh
#
# Optional: pass your Vercel origin to set CORS_ORIGINS correctly on first run:
#   sudo bash deploy/setup-backend.sh https://your-app.vercel.app

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_DIR/backend"
SERVICE_USER="moviestogether"
CORS_ORIGIN="${1:-http://localhost:5173}"

if [ "$EUID" -ne 0 ]; then
  echo "Run this with sudo: sudo bash deploy/setup-backend.sh" >&2
  exit 1
fi

if [ "$REPO_DIR" != "/opt/moviestogether" ]; then
  echo "Warning: expected the repo at /opt/moviestogether (per DEPLOY.md), found it at $REPO_DIR." >&2
  echo "The systemd unit template hardcodes /opt/moviestogether - edit deploy/moviestogether-backend.service if your path differs." >&2
fi

echo "==> Installing system packages (python3-venv, caddy) if missing"
apt-get update -qq
apt-get install -y -qq python3-venv caddy

echo "==> Ensuring service user '$SERVICE_USER' exists"
id -u "$SERVICE_USER" >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"

echo "==> Setting ownership of $REPO_DIR to $SERVICE_USER"
chown -R "$SERVICE_USER:$SERVICE_USER" "$REPO_DIR"

echo "==> Creating/updating the Python virtualenv"
sudo -u "$SERVICE_USER" python3 -m venv "$BACKEND_DIR/.venv"
sudo -u "$SERVICE_USER" "$BACKEND_DIR/.venv/bin/pip" install -q -r "$BACKEND_DIR/requirements.txt"

ENV_FILE="$BACKEND_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "==> No .env found - generating one with fresh secrets"
  JWT_SECRET="$(openssl rand -hex 32)"
  SITE_PASSPHRASE="$(openssl rand -hex 16)"
  cat > "$ENV_FILE" <<EOF
DATABASE_URL=sqlite:///./moviestogether.db
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
CORS_ORIGINS=$CORS_ORIGIN
TMDB_API_KEY=
SITE_PASSPHRASE=$SITE_PASSPHRASE
SITE_TOKEN_EXPIRE_MINUTES=43200
EOF
  chown "$SERVICE_USER:$SERVICE_USER" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  echo ""
  echo "    Generated SITE_PASSPHRASE: $SITE_PASSPHRASE"
  echo "    (this is what you and your friend type into the app - write it down)"
  echo ""
else
  echo "==> Found existing .env, leaving it untouched"
fi

echo "==> Installing systemd service"
cp "$REPO_DIR/deploy/moviestogether-backend.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable moviestogether-backend >/dev/null

echo "==> Installing Caddy config"
cp "$REPO_DIR/deploy/Caddyfile" /etc/caddy/Caddyfile
systemctl reload caddy 2>/dev/null || systemctl restart caddy

echo "==> Restarting backend"
systemctl restart moviestogether-backend
sleep 1
systemctl --no-pager status moviestogether-backend || true

echo ""
echo "==> Smoke test"
curl -sf http://127.0.0.1/api/health && echo " -> backend OK" || echo " -> backend NOT responding, check: journalctl -xeu moviestogether-backend"
