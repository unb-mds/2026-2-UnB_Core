import os

from sqlmodel import Session

from backend.app.db import create_db_and_tables, engine
from backend.app.domain import PerfilUsuario
from backend.app.services.usuario_service import criar_usuario_admin


def main() -> None:
    nome = os.environ.get("ADMIN_NAME")
    email = os.environ.get("ADMIN_EMAIL")
    senha = os.environ.get("ADMIN_PASSWORD")
    if not all((nome, email, senha)):
        raise SystemExit(
            "Defina ADMIN_NAME, ADMIN_EMAIL e ADMIN_PASSWORD para executar o seed."
        )

    create_db_and_tables()
    with Session(engine) as session:
        criar_usuario_admin(
            session,
            nome=nome,
            email=email,
            senha=senha,
            perfil=PerfilUsuario.ADMINISTRADOR,
        )


if __name__ == "__main__":
    main()
