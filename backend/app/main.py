from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import models  # noqa: F401 - ensures all models are registered before create_all
from app.config import settings
from app.database import Base, engine
from app.routers import (
    analysis,
    auth,
    compatibility,
    factorization,
    friends,
    items,
    movie_map,
    ratings,
    recommendations,
    site_access,
    tmdb,
)
from app.security import verify_site_token

app = FastAPI(title="MoviesTogether API")

SITE_ACCESS_EXEMPT_PATHS = {"/api/health", "/api/site-access"}


# NOTE: Starlette's add_middleware() PREPENDS to the middleware stack (each call moves to the
# outermost position), so whichever middleware is registered LAST here ends up running FIRST on
# every request. CORSMiddleware must be registered after (and therefore run before/outside) this
# gate middleware, or CORS preflight OPTIONS requests never reach CORSMiddleware's own
# short-circuit handling and fail with a 401 from the gate instead of proper CORS headers.
@app.middleware("http")
async def require_site_access(request: Request, call_next):
    """Blocks every route (including docs, login, and register) until the shared site
    passphrase has been exchanged for a site token via POST /api/site-access - this is a
    separate, coarser gate than per-user auth, meant to keep the app invisible to anyone who
    doesn't already know the passphrase, not just unauthenticated."""
    if request.url.path in SITE_ACCESS_EXEMPT_PATHS:
        return await call_next(request)

    token = request.headers.get("x-site-access")
    if not token or not verify_site_token(token):
        return JSONResponse(status_code=401, content={"detail": "Site access required"})

    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(items.router)
app.include_router(ratings.router)
app.include_router(tmdb.router)
app.include_router(factorization.router)
app.include_router(recommendations.router)
app.include_router(movie_map.router)
app.include_router(compatibility.router)
app.include_router(analysis.router)
app.include_router(friends.router)
app.include_router(site_access.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
