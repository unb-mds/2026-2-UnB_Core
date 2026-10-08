import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:change-me@localhost:5214/postgres",
    )


settings = Settings()