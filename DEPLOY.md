# Deploying MoviesTogether

Frontend on **Vercel** (free), backend + SQLite on your own **Google Compute Engine VM** (or any
Linux box — nothing here is GCE-specific except the firewall step). Vercel proxies `/api/*` to
your VM, so the browser only ever talks to your Vercel domain — no CORS to configure, and the VM
doesn't need a browser-trusted HTTPS certificate to get started.

Everything below is free (beyond the VM you already have). The one optional paid step (a domain
name, ~$10-15/year) is called out explicitly at the end and can be skipped entirely.

## 1. Rotate secrets

Never reuse the values from your local `backend/.env` in production. Generate fresh ones:

```bash
openssl rand -hex 32   # use the output as JWT_SECRET
openssl rand -hex 32   # use a *different* output as SITE_PASSPHRASE, or pick a memorable phrase
```

`SITE_PASSPHRASE` is the one you and your friend will actually type into the app, so a memorable
phrase (not necessarily random hex) is fine for that one specifically — just don't reuse a
password from anywhere else.

## 2. Set up the VM (backend)

SSH into your GCE VM, then:

```bash
sudo apt update && sudo apt install -y python3-venv git caddy

sudo useradd --system --create-home --home-dir /opt/moviestogether moviestogether
sudo -u moviestogether git clone <your-repo-url> /opt/moviestogether-src
sudo mkdir -p /opt/moviestogether/backend
sudo cp -r /opt/moviestogether-src/backend/* /opt/moviestogether/backend/
sudo chown -R moviestogether:moviestogether /opt/moviestogether

cd /opt/moviestogether/backend
sudo -u moviestogether python3 -m venv .venv
sudo -u moviestogether ./.venv/bin/pip install -r requirements.txt
```

Create `/opt/moviestogether/backend/.env` (as root or the `moviestogether` user) with the rotated
secrets from step 1:

```
DATABASE_URL=sqlite:///./moviestogether.db
JWT_SECRET=<paste from step 1>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
CORS_ORIGINS=https://your-vercel-app.vercel.app
TMDB_API_KEY=
SITE_PASSPHRASE=<paste from step 1>
SITE_TOKEN_EXPIRE_MINUTES=43200
```

(`CORS_ORIGINS` isn't security-critical here since the browser never calls this box directly — see
§4 — but set it to your real Vercel URL once you have it, for defense in depth.)

Install the systemd service (template at `deploy/moviestogether-backend.service` in this repo):

```bash
sudo cp deploy/moviestogether-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now moviestogether-backend
sudo systemctl status moviestogether-backend   # should show "active (running)"
```

Install Caddy's config (template at `deploy/Caddyfile`):

```bash
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

**Verify from the VM itself**, before opening any firewall:

```bash
curl http://127.0.0.1/api/health          # -> {"status":"ok"}
curl http://127.0.0.1/api/items           # -> 401 "Site access required" (correct - gate is working)
```

## 3. GCP firewall + static IP

In the GCP console (or `gcloud`):

- **Reserve a static external IP** for the VM (Compute Engine → IP addresses) so it doesn't change on reboot — Vercel's rewrite needs a stable target.
- **Firewall rules**: allow `tcp:80` from `0.0.0.0/0`. Restrict `tcp:22` (SSH) to your own current IP, not the whole internet. Do **not** add a rule for `8001` — it's bound to `127.0.0.1` only and reached exclusively through Caddy on the same box.

Verify from your own machine (not the VM):

```bash
curl http://<vm-static-ip>/api/health     # -> {"status":"ok"}
curl http://<vm-static-ip>:8001/api/health  # should time out / connection refused - not exposed
```

## 4. Deploy the frontend to Vercel

1. Push this repo to GitHub (if it isn't already).
2. In Vercel: **New Project** → import the repo → set **Root Directory** to `frontend`. Framework preset "Vite" should be auto-detected.
3. Edit `frontend/vercel.json` (already in the repo) and replace `YOUR_GCE_STATIC_IP` with your actual static IP from step 3, then commit/push:
   ```json
   { "rewrites": [{ "source": "/api/:path*", "destination": "http://<vm-static-ip>/api/:path*" }] }
   ```
4. In the Vercel project's **Environment Variables**, add:
   ```
   VITE_API_BASE_URL=/api
   ```
   (A relative path — because of the rewrite, the API is same-origin as far as the browser is concerned.)
5. Trigger a deploy (push to the connected branch, or click Deploy in the dashboard).

## 5. Verify end-to-end

- Visit your `*.vercel.app` URL. You should see **only the passphrase gate** — not the login form, not any app content.
- Enter the wrong passphrase a few times → eventually a "Too many attempts" message (rate limited).
- Enter the correct passphrase → the normal login/sign-up screen appears.
- Sign up your friend, log in, rate a few things, confirm Recommender/Movie Map/Analysis all work exactly like they did locally.

## 6. Ongoing maintenance (all free)

```bash
sudo apt install -y unattended-upgrades   # automatic OS security patches
sudo apt install -y fail2ban              # blocks repeated failed SSH attempts
```

**Backups** — a simple daily cron copying the SQLite file to a second directory on the same VM:

```bash
(crontab -l 2>/dev/null; echo "0 3 * * * cp /opt/moviestogether/backend/moviestogether.db /opt/moviestogether/backups/moviestogether-\$(date +%F).db") | crontab -
mkdir -p /opt/moviestogether/backups
```

(Off-VM backups via a GCS bucket are a fine upgrade later — costs a few cents/month for a file this
small — but aren't required.)

## Optional: a real domain (~$10-15/year, skip if you don't want to spend anything)

The plan above works fully without a domain. If you later want the Vercel→VM hop encrypted too
(defense in depth — that hop is never exposed to your friend's browser either way):

1. Buy a domain, point an `A` record at your VM's static IP.
2. Edit `deploy/Caddyfile` on the VM, swap to the commented-out domain block, `sudo systemctl reload caddy` — Caddy fetches a real Let's Encrypt certificate automatically.
3. Update `frontend/vercel.json`'s destination to `https://your-api-domain.com/api/:path*`, commit, redeploy.

Nothing else changes.
