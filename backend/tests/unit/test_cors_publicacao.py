from fastapi.testclient import TestClient

from backend.app.main import criar_aplicacao


def preflight(client: TestClient, origem: str):
    # Pergunta que o navegador faz antes de chamar a API de outro domínio.
    return client.options(
        "/api/v1/cursos",
        headers={"Origin": origem, "Access-Control-Request-Method": "GET"},
    )


def test_sem_variavel_libera_so_o_front_local(monkeypatch) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    client = TestClient(criar_aplicacao())

    local = preflight(client, "http://localhost:5173")
    externo = preflight(client, "https://unb-core.vercel.app")

    assert local.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-origin" not in externo.headers


def test_cors_origins_libera_os_enderecos_da_publicacao(monkeypatch) -> None:
    # Espaços e a barra final, comuns ao copiar o endereço do painel, são ignorados.
    monkeypatch.setenv("CORS_ORIGINS", " https://unb-core.vercel.app/ , https://unb-core-git-main.vercel.app")
    client = TestClient(criar_aplicacao())

    publicado = preflight(client, "https://unb-core.vercel.app")
    outro = preflight(client, "https://unb-core-git-main.vercel.app")
    local = preflight(client, "http://localhost:5173")

    assert publicado.headers.get("access-control-allow-origin") == "https://unb-core.vercel.app"
    assert outro.headers.get("access-control-allow-origin") == "https://unb-core-git-main.vercel.app"
    assert "access-control-allow-origin" not in local.headers
