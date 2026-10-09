import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:password@localhost:5214/postgres",
    )
    jwt_secret_key: str = os.environ["JWT_SECRET_KEY"]
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
