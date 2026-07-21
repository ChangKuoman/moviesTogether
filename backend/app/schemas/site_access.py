from pydantic import BaseModel


class SiteAccessRequest(BaseModel):
    passphrase: str


class SiteAccessResponse(BaseModel):
    site_token: str
