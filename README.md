# MoviesTogether

A movie & TV recommendation app built to learn how recommendation systems actually work, not to
compete with Netflix. Matrix factorization is implemented **from scratch in NumPy** (no `surprise`
or `implicit`), so the "invisible numbers" behind every recommendation are visible and explorable.

Movies and TV seasons can both be rated — each season of a show is tracked as its own item, since
taste can vary wildly season to season.

## Features

- **Library** — add movies/seasons (manually, or via TMDb search if you set an API key) and rate them 1-5
- **Recommender** — top unseen-item predictions per user, each with a plain-language explanation and a confidence score
- **Latent Factors** — inspect the raw factor vectors the model learned, and see which items load highest/lowest on each dimension
- **Movie Map** — a 2D PCA projection of every item's latent vector, click a point to see its nearest neighbors
- **Analysis** — pairwise compatibility between any two users, plus a live slider blending collaborative and content-based (genre) scoring

Works for any number of users, not just two — new people can sign up from the login screen at any time.

## Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, NumPy (matrix factorization), scikit-learn (PCA)
- **Frontend**: Vue 3, Vite, Pinia, Vue Router, ECharts (movie map)
- **Auth**: JWT, bcrypt-hashed passwords, self-serve sign-up

## Setup

### Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env            # optionally set TMDB_API_KEY here; set SITE_PASSPHRASE to whatever you want locally
uvicorn app.main:app --reload --port 8000
```

The API is served at `http://127.0.0.1:8000/api`, with interactive docs at `/docs`.

The whole API — including `/docs` — is gated behind a shared site passphrase (`SITE_PASSPHRASE` in
`.env`), separate from per-user login. The frontend will prompt for it before showing the login
screen; see [DEPLOY.md](DEPLOY.md) for why and how this is used in production.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # point VITE_API_BASE_URL at your backend
npm run dev
```

Open the printed local URL, sign up (there are no seeded accounts — the first users are created
through the login screen's "Sign up" link), and start rating.

### Running tests

```bash
cd backend
pytest
```

`tests/test_mf_service.py` verifies the from-scratch matrix factorization converges on synthetic
data and doesn't blow up numerically — the core algorithmic guarantee the rest of the app depends on.

## Deployment

See [DEPLOY.md](DEPLOY.md) for putting this on the internet for you and a friend: frontend on
Vercel, backend on your own VM, with a site-wide passphrase gate so nobody else can reach it — at
no cost beyond a server you already have.

## Notes on the ML approach

- **No TMDb key required.** The Library falls back to manual entry for title/type/year when no key
  is configured; TMDb search/autofill kicks in automatically once `TMDB_API_KEY` is set.
- **Tuned for small data.** With only a handful of users and ratings, the model deliberately
  deviates from textbook defaults: the number of latent factors scales down with how much data
  exists, regularization is higher than usual, and there's no train/val split (not enough ratings
  to hold any out) — early stopping on training-RMSE plateau substitutes instead. See
  `backend/app/services/mf_service.py` and `backend/app/core/constants.py` for the specifics.
- **Content scoring is intentionally simple.** The content-based half of the hybrid score uses
  one-hot genre vectors, not text embeddings — good enough to demonstrate the hybrid blend without
  a heavy model download. Swapping in `sentence-transformers` embeddings of each item's overview is
  a natural next step (see `backend/app/services/content_service.py`).
