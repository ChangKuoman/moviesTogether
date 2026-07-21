# Deploying MoviesTogether

Assumes this repo is already pushed to GitHub — both the VM and Vercel deploy straight from it.

Frontend on **Vercel** (free), backend + SQLite on your own **Google Compute Engine VM** (or any
Linux box — nothing here is GCE-specific except the firewall step). Vercel proxies `/api/*` to
your VM, so the browser only ever talks to your Vercel domain — no CORS to configure, and the VM
doesn't need a browser-trusted HTTPS certificate to get started.

Everything below is free (beyond the VM you already have). The one optional paid step (a domain
name, ~$10-15/year) is called out explicitly at the end and can be skipped entirely.

## 1. Secrets

Never reuse the values from your local `backend/.env` in production. You don't need to generate
anything by hand — the setup script in §2 creates fresh, random secrets automatically the first
time it runs. If you'd rather pick your own (e.g. a memorable `SITE_PASSPHRASE` instead of random
hex), create `backend/.env` yourself before running the script; it leaves an existing file alone.

## 2. Set up the VM (backend)

SSH into your GCE VM and clone your GitHub repo — any path is fine, the setup script in the next
step detects its own location and adapts (`/opt/moviestogether` below is just a suggestion):

```bash
sudo apt update && sudo apt install -y git
sudo git clone https://github.com/ChangKuoman/moviesTogether.git /opt/moviestogether
```

If the repo is **private**, plain `https://` cloning will prompt for credentials that don't work
well non-interactively — use a fine-grained GitHub Personal Access Token (read-only, scoped to
just this repo) in the URL instead:
`https://<token>@github.com/ChangKuoman/moviesTogether.git`, or set up a read-only SSH deploy
key if you prefer.

Then run the setup script (`deploy/setup-backend.sh`, already in the repo) — it installs
`python3-venv`/Caddy if missing, creates the dedicated `moviestogether` service user, builds the
venv, generates a systemd unit for wherever you cloned it, installs the Caddy config, and starts
everything:

```bash
cd /opt/moviestogether   # or wherever you cloned it
sudo bash deploy/setup-backend.sh https://your-vercel-app.vercel.app
```

(The URL argument is optional — it just pre-fills `CORS_ORIGINS`; you can edit `backend/.env`
later if you don't have your Vercel URL yet.)

**The first time you run it**, since no `backend/.env` exists yet, the script generates one with a
fresh `JWT_SECRET` and `SITE_PASSPHRASE` automatically (no need to do the `openssl rand` step from
§1 by hand) and **prints the generated passphrase at the end — write it down**, you and your friend
need it to get past the gate. Re-running the script later (e.g. after `git pull` for an update)
leaves an existing `.env` untouched and just reinstalls/restarts everything else.

The script ends with a smoke test. You should see:

```
{"status":"ok"} -> backend OK
```

If instead you get "backend NOT responding," it prints the exact `journalctl` command to run for
details.

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

1. In Vercel: **New Project** → **Import Git Repository** → pick your GitHub repo → set **Root Directory** to `frontend`. Framework preset "Vite" should be auto-detected. (First time connecting Vercel to this repo, it'll ask to install the Vercel GitHub App — scope that to just this repo.)
2. Edit `frontend/vercel.json` (already in the repo) and replace `YOUR_GCE_STATIC_IP` with your actual static IP from step 3, then commit/push:
   ```json
   { "rewrites": [{ "source": "/api/:path*", "destination": "http://<vm-static-ip>/api/:path*" }] }
   ```
3. In the Vercel project's **Environment Variables**, add:
   ```
   VITE_API_BASE_URL=/api
   ```
   (A relative path — because of the rewrite, the API is same-origin as far as the browser is concerned.)
4. Push to the connected branch → Vercel builds and deploys automatically; every future push redeploys too.

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

**Backups** — a simple daily cron copying the SQLite file to a second directory on the same VM
(adjust `/opt/moviestogether` below if you cloned to a different path):

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
