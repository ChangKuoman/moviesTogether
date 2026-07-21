# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

MoviesTogether is a portfolio-style movie/TV recommender for a small group of friends. The point
of the project is to make classical recommendation-system internals visible and explorable
(matrix factorization implemented from scratch, latent factors, PCA projection, compatibility
scoring) rather than to compete with a real streaming service.

# Project Architecture

**Stack**: Vue 3 SPA (Vite, Pinia, Vue Router, ECharts) talking to a Python FastAPI backend
(SQLAlchemy + SQLite), deployed split across Vercel (frontend) and a single VM (backend), proxied
through a `vercel.json` rewrite so the browser only ever talks to one origin.

**Two independent auth layers, stacked**:
1. A **site-wide passphrase gate** (`app/main.py`'s `require_site_access` middleware) sits in
   front of every route, including `/docs`, login, and register. `POST /api/site-access` exchanges
   a shared passphrase for a site token (JWT with `"typ": "site"`), sent as `X-Site-Access` on every
   request. This exists so the app is invisible to anyone who doesn't already know the passphrase
   — not just "requires an account."
2. **Per-user auth** (JWT with `"typ": "user"`, `Authorization: Bearer`) sits on top of that, for
   knowing *which* person is rating/browsing.
   The two token types can never be confused for each other because of the differing `typ` claim.

**Data model**: `Item` is a shared, global catalog (movies and TV *seasons* — each season is its
own independently-rated row, never the whole show). `LibraryEntry` is a per-user join table
controlling which items show up in *your* Library — this lets ratings on the same item be compared
across users (for compatibility/collaborative filtering) while each person's Library view only
shows what they personally added. `Rating` is per-user-per-item. An `Item` is only ever hard-deleted
once no `LibraryEntry` or `Rating` references it anymore.

**ML core** (`app/services/mf_service.py`): matrix factorization implemented from scratch in NumPy
(no `surprise`/`implicit`) — `r̂ = μ + b_u + b_i + P_u·Q_i`, trained with plain SGD. Retrains
*synchronously* on every rating write (no task queue — see Design Decisions). Results persist as
`ModelRun`/`UserFactor`/`ItemFactor` snapshots, which `movie_map`, `recommendations`,
`compatibility`, and `analysis` (hybrid) all read from rather than retraining per request.

**Friendship gates cross-user features**: `Friendship` (pending/accepted/declined) must be
`accepted` before two users can see compatibility, watch-together picks, or each other's real name
on the Movie Map. This is enforced server-side in the relevant routers, not just hidden in the UI.

**Request path in production**: browser → Vercel (serves the static build, rewrites `/api/*`) →
Caddy on the VM (`:80`) → uvicorn (`127.0.0.1:8001`) → FastAPI middleware (CORS, then the site-access
gate) → router → service → SQLAlchemy → SQLite.

# Coding Conventions

- **Backend**: routers stay thin (auth/validation/wiring) and delegate real logic to
  `app/services/*`, one service per concern (`mf_service`, `pca_service`, `similarity_service`,
  `confidence_service`, `hybrid_service`, `friendship_service`, `library_service`, `rate_limit`,
  `tmdb_service`, etc.). Pydantic schemas (`app/schemas/`) are kept separate from SQLAlchemy models
  (`app/models/`) — never return an ORM instance directly from a route.
- **Frontend**: Vue 3 `<script setup>` everywhere, no TypeScript, no Composition API abstractions
  beyond what's needed. One Pinia store per domain (`auth`, `siteAccess`, `items`, `ratings`,
  `model`, `friends`), each following the same `{ state, error, loading }` + action shape. `api/*.js`
  files are thin axios wrappers only — no logic beyond the HTTP call.
- Shared reactive logic goes in `composables/` (e.g. `usePagination`, reused across
  Library/Recommender/Analysis) rather than being duplicated per view.
- Both token types (`token`, `siteToken`) persist to `localStorage` and drive a `window` custom
  event on 401 (`auth:unauthorized`, `site-access:required`) so any component can react without
  prop-drilling — see `api/client.js` and the listeners in `main.js`.
- Comments are rare and only explain non-obvious *why* (a deliberate deviation from a textbook ML
  default, a workaround for a specific framework quirk) — see the "Design Decisions" section below
  for the reasoning that's already inline in the code as comments.

# Useful Commands

**Backend** (`backend/`):
```bash
python -m venv .venv && .venv/Scripts/activate   # or source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                             # set SITE_PASSPHRASE, optionally TMDB_API_KEY
uvicorn app.main:app --reload --port 8000
pytest                                            # tests/test_mf_service.py is the one load-bearing
                                                   # test - verifies the from-scratch factorization
                                                   # actually converges and doesn't blow up numerically
```
No linter/formatter is configured for the backend (no ruff/black config present) — don't assume one.

**Frontend** (`frontend/`):
```bash
npm install
cp .env.example .env      # VITE_API_BASE_URL
npm run dev
npm run build              # production static build, consumed by Vercel
npm run preview
```
No lint/test script is defined in `package.json` — don't invent one when asked to "run the linter".

**Deploy** (VM side, from the repo root on the VM):
```bash
sudo bash deploy/setup-backend.sh https://your-vercel-app.vercel.app   # first deploy AND redeploys
```
This one script is idempotent: installs system deps, builds the venv, generates `backend/.env`
with fresh secrets only if one doesn't exist yet, (re)installs the systemd service + Caddy config,
and restarts everything. Re-run it after every `git pull` on the VM instead of doing any of that by hand.

# Design Decisions

- **Matrix factorization is hand-rolled, not from a library.** The entire premise of the project
  is making the "invisible numbers" visible — using `surprise`/`implicit` would hide exactly the
  thing the app exists to show.
- **Small-N-tuned hyperparameters, not textbook defaults** (`app/core/constants.py`): `k` scales
  down with how much data exists (`min(6, n_ratings // 3, n_items - 1)`, floor 2), regularization
  is higher than typical (`0.1` vs. the usual `0.02`), and there's no train/val split — holding out
  data is meaningless at N≈10-20 ratings, so training runs on everything with early stopping on a
  training-RMSE plateau instead.
- **Retraining is synchronous on every rating write**, not queued to a background worker. At this
  scale (a handful of users, k≤6) it's sub-100ms; a task queue would be premature complexity.
  Explicitly flagged in code as something to revisit only if the user base grows past dozens.
- **Confidence scores are a heuristic, not a statistical bootstrap** — a real bootstrap would
  itself be noisy at N≈10-20. The heuristic combines total-ratings-by-this-user with
  nearest-latent-neighbor evidence.
- **Compatibility % is cosine similarity of latent vectors, not raw rating agreement.** This is a
  known, intentional UX quirk: it can look inconsistent with the agreement/disagreement list shown
  right below it in the same response, because the two are computed completely differently. Not a bug.
- **Items are a shared global catalog; Library visibility is per-user.** Adding an item that's
  already in the catalog (e.g. a friend added it first) just creates a `LibraryEntry` — it never
  re-fetches TMDb or errors. Removing an item removes only *your* `LibraryEntry` + rating; the
  underlying `Item` row survives until literally nobody references it.
- **Recommender and Watch Together pull from your library, not the whole catalog.** Recommender =
  your library minus items you've rated. Watch Together = the *union* of both friends' libraries,
  minus only items **both** of you have rated (so "your friend already watched it" doesn't hide a
  pick from you — it just means you'd be catching up).
- **Friendship gates every cross-user feature server-side** (`friendship_service.are_friends`),
  not just in the UI — compatibility, watch-together, and the Movie Map's "friends" scope all check
  this in the router.
- **Movie Map has a privacy-aware "everyone" mode.** Besides the default "you + friends" (real
  names), there's an "everyone" scope showing every rated user's taste-point for context — but
  every point except your own is anonymized with a synthetic negative ID and the name `"Anonymous"`,
  so it can't be cross-referenced against any other endpoint.
- **Two JWT types with a `typ` claim, never confusable.** A site-access token can't be replayed as
  a per-user token or vice versa, even though both are signed with the same secret.
- **Middleware registration order matters and already bit us once**: Starlette's `add_middleware`
  *prepends* (last-registered = outermost/runs-first). The site-access gate middleware must be
  registered in `main.py` **before** `app.add_middleware(CORSMiddleware, ...)`, or CORS preflight
  `OPTIONS` requests get rejected by the gate before `CORSMiddleware` ever gets a chance to
  short-circuit them. If you ever reorder middleware in `main.py`, re-verify preflight still works.
- **The Vercel↔VM hop is deliberately plain HTTP, not HTTPS.** The browser never talks to the VM
  directly (Vercel's rewrite proxies it), so that hop isn't subject to browser cert-trust rules.
  This keeps the whole deployment free (no domain required). A real domain + Let's Encrypt is an
  explicit, optional, skippable upgrade path documented in `DEPLOY.md`, not a requirement.
- **`deploy/setup-backend.sh` is path-agnostic and idempotent by design.** It detects its own
  location rather than assuming `/opt/moviestogether`, and generates the systemd unit from
  `moviestogether-backend.service.template` (placeholder substitution) instead of a static file. It
  also auto-detects whether to run the service as a dedicated `moviestogether` system account or as
  the invoking `sudo` user — home directories are typically mode `750`/`700`, so a separate service
  account can never be `chown`'d into working order if the repo lives under someone's `~/`.
- **TMDb integration fails soft everywhere.** Every call in `tmdb_service.py` returns `None`/`[]`
  on failure or when no API key is configured; the frontend checks `GET /tmdb/status` to decide
  between live search and a manual-entry fallback form. No core flow (rating, recommending) ever
  hard-depends on TMDb being reachable.
- **Content-based scoring uses one-hot genre vectors, not embeddings.** `sentence-transformers` on
  item overviews was deliberately deferred (heavy model download, not worth it at this scale) — the
  extension point is called out in `content_service.py`.

# Purpose of Each Folder

- `backend/app/models/` — SQLAlchemy ORM models, one per table.
- `backend/app/schemas/` — Pydantic request/response models, intentionally decoupled from the ORM models.
- `backend/app/routers/` — FastAPI endpoints; thin, delegate to `services/`.
- `backend/app/services/` — business logic and the ML core. This is where almost all real logic lives.
- `backend/app/core/` — tuning constants (`constants.py`) and shared exception types.
- `backend/tests/` — pytest; `test_mf_service.py` is the one test that guards the core algorithmic
  guarantee (the from-scratch factorization converges and stays numerically bounded).
- `frontend/src/api/` — thin axios wrappers, one file per backend router group.
- `frontend/src/stores/` — Pinia stores, one per domain, sharing a consistent state/action shape.
- `frontend/src/views/` — one per nav tab/route (Library, Recommender, Latent Factors, Movie Map,
  Analysis, Friends) plus Login and the site-access gate.
- `frontend/src/components/` — grouped by feature area (`library/`, `recommender/`,
  `latent-factors/`, `movie-map/`, `compatibility/`, `common/`).
- `frontend/src/composables/` — shared reactive logic used across multiple views.
- `deploy/` — everything needed to stand up the backend on a VM: `Caddyfile` (reverse proxy config),
  `moviestogether-backend.service.template` (systemd unit, path/user substituted at install time),
  `setup-backend.sh` (the one script that does first-deploy and every redeploy).
- Root `README.md` — features and local setup. Root `DEPLOY.md` — production deployment walkthrough.
