from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_JWT_ALG: str = "HS256"
    APP_JWT_SECRET: str = "secret"
    APP_JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    APP_JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MONGO_DB_URL: str = "mongodb://localhost:27020"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
