from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./moviestogether.db"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080
    cors_origins: str = "http://localhost:5173"
    tmdb_api_key: str = ""
    site_passphrase: str = "dev-passphrase-change-me"
    site_token_expire_minutes: int = 43200  # 30 days

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def tmdb_configured(self) -> bool:
        return bool(self.tmdb_api_key)


settings = Settings()
