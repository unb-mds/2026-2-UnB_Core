import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./unb_core.db",
    )
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        "dev-only-change-this-secret-key-32-bytes-minimum",
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
