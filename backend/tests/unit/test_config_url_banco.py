import pytest
from sqlalchemy.engine import make_url

from backend.app.settings.config import normalizar_url_banco


NEON = "postgresql://usuario:senha@ep-exemplo.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"


@pytest.mark.parametrize(
    "url",
    [NEON, NEON.replace("postgresql://", "postgres://", 1)],
)
def test_url_copiada_do_neon_usa_o_psycopg2_instalado(url: str) -> None:
    normalizada = normalizar_url_banco(url)

    assert normalizada.startswith("postgresql+psycopg2://")
    # O resto da URL, com usuário, host e opções de SSL, não muda.
    assert normalizada.endswith("@ep-exemplo.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
    assert make_url(normalizada).get_dialect().driver == "psycopg2"


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg2://postgres:postgres@db:5432/unb_core",
        "sqlite:///./unb_core.db",
        "sqlite://",
    ],
)
def test_urls_com_driver_ou_sqlite_ficam_iguais(url: str) -> None:
    assert normalizar_url_banco(url) == url
