import os


def normalizar_url_banco(url: str) -> str:
    """Indica o driver psycopg2 nas URLs de PostgreSQL sem driver.

    Serviços como Neon e Render entregam a URL como "postgresql://..." (ou
    "postgres://..."). Nesse formato, o SQLAlchemy 2.1 procura o driver psycopg
    (versão 3), mas o projeto instala o psycopg2.
    """
    for prefixo in ("postgresql://", "postgres://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg2://" + url[len(prefixo):]
    return url


class Settings:
    database_url: str = normalizar_url_banco(os.getenv(
        "DATABASE_URL",
        "sqlite:///./unb_core.db",
    ))
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        "dev-only-change-this-secret-key-32-bytes-minimum",
    )
    jwt_algorithm: str = "HS256"
    # Duração do login (minutos). Para apresentações, aumente com a variável de ambiente.
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


settings = Settings()
