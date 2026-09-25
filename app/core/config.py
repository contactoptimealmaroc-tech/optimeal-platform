from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str
    database_url: str = "sqlite:///./optimeal.db"
    session_cookie: str = "optimeal_session"
    session_max_age: int = 28800
    public_base_url: str = "http://127.0.0.1:8000"
    app_base_url: str = "http://127.0.0.1:8000"
    api_base_url: str = "http://127.0.0.1:8000"
    carte_base_url: str = "https://carte.optimeal.ma"
    allowed_origins: str = "http://127.0.0.1:8000"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [x.strip() for x in self.allowed_origins.split(",") if x.strip()]

settings = Settings()
