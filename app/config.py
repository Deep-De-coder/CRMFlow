from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    sf_username: str
    sf_password: str
    sf_security_token: str
    sf_domain: str = "login"
    app_env: str = "development"
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
