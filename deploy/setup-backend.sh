#!/usr/bin/env bash
# Sets up (or updates) the MoviesTogether backend on this VM. Safe to re-run - use it both for
# the first deploy and for every redeploy after a `git pull` (installs/updates deps, creates
# .env with fresh secrets only if one doesn't already exist, reinstalls the systemd service and
# Caddy config, then restarts everything).
#
# Works no matter where you cloned the repo - it detects its own location and generates the
# systemd unit from a template rather than assuming a fixed path.
#
# Usage: run from anywhere, as root, after cloning the repo:
#   cd /path/to/moviestogether && sudo bash deploy/setup-backend.sh
#
# Optional: pass your Vercel origin to set CORS_ORIGINS correctly on first run:
#   sudo bash deploy/setup-backend.sh https://your-app.vercel.app

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_DIR/backend"
CORS_ORIGIN="${1:-http://localhost:5173}"

if [ "$EUID" -ne 0 ]; then
  echo "Run this with sudo: sudo bash deploy/setup-backend.sh" >&2
  exit 1
fi

# If the repo lives under a real login user's home directory (the common case - you cloned it
# into your own account), run the service as that same user instead of a separate system
# account. A dedicated 'moviestogether' account can't be chown'd into working order there: home
# directories are typically mode 750/700, so no amount of chown-ing the repo itself lets a
# DIFFERENT account even traverse into ~/, regardless of the repo's own ownership. Only fall back
# to a dedicated system account when the repo is somewhere shared (e.g. /opt), where that
# isolation is actually meaningful.
if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ] && [[ "$REPO_DIR" == "/home/$SUDO_USER"* ]]; then
  SERVICE_USER="$SUDO_USER"
  echo "==> Repo is under $SUDO_USER's home directory - running the service as $SUDO_USER"
else
  SERVICE_USER="moviestogether"
  echo "==> Ensuring dedicated service user '$SERVICE_USER' exists"
  id -u "$SERVICE_USER" >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"
fi

# Always (re-)apply ownership, even in the home-directory case - a previous run of an older
# version of this script may have already chown'd everything to a stale/different user.
echo "==> Ensuring $REPO_DIR is owned by $SERVICE_USER"
chown -R "$SERVICE_USER:$SERVICE_USER" "$REPO_DIR"

echo "==> Using repo at $REPO_DIR"

echo "==> Installing system packages (python3-venv, caddy) if missing"
apt-get update -qq
apt-get install -y -qq python3-venv caddy

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

echo "==> Generating and installing systemd service for this path"
sed \
  -e "s|__BACKEND_DIR__|$BACKEND_DIR|g" \
  -e "s|__SERVICE_USER__|$SERVICE_USER|g" \
  "$REPO_DIR/deploy/moviestogether-backend.service.template" > /etc/systemd/system/moviestogether-backend.service
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
