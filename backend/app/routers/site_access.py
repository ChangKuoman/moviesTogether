import secrets

from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.schemas.site_access import SiteAccessRequest, SiteAccessResponse
from app.security import create_site_token
from app.services.rate_limit import is_rate_limited, record_attempt

router = APIRouter(prefix="/api/site-access", tags=["site-access"])


@router.post("", response_model=SiteAccessResponse)
def verify_site_access(payload: SiteAccessRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if is_rate_limited(f"site-access:{client_ip}"):
        raise HTTPException(status_code=429, detail="Too many attempts, try again later")

    if not secrets.compare_digest(payload.passphrase, settings.site_passphrase):
        record_attempt(f"site-access:{client_ip}")
        raise HTTPException(status_code=401, detail="Incorrect passphrase")

    return SiteAccessResponse(site_token=create_site_token())
