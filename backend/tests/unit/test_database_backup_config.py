from pathlib import Path


PROJETO_RAIZ = Path(__file__).resolve().parents[3]
COMPOSE = (PROJETO_RAIZ / "docker-compose.yml").read_text(
    encoding="utf-8"
)


def test_compose_define_servico_automatico_de_backup():
    assert "db-backup:" in COMPOSE
    assert "pg_dump" in COMPOSE
    assert "sleep 86400" in COMPOSE
    assert "- ./backups:/backups" in COMPOSE
    assert "unb_core-${" in COMPOSE or "unb_core-$" in COMPOSE


def test_backup_mantem_somente_arquivos_dos_ultimos_sete_dias():
    assert "find /backups -type f -mtime +7 -delete" in COMPOSE


def test_compose_define_restauracao_manual_separada():
    assert "db-restore:" in COMPOSE
    assert "profiles:" in COMPOSE
    assert "- manual" in COMPOSE
    assert "RESTORE_FILE: ${RESTORE_FILE:-}" in COMPOSE
    assert "pg_restore" in COMPOSE


def test_restauracao_valida_arquivo_e_exibe_informacoes():
    assert 'restore_file=$(basename "$RESTORE_FILE")' in COMPOSE or (
        'restore_file=$$(basename "$$RESTORE_FILE")' in COMPOSE
    )
    assert "Backup being used:" in COMPOSE
    assert "Current database being replaced:" in COMPOSE
    assert "Safety backup:" in COMPOSE
    assert "unb_core-before-restore-" in COMPOSE


def test_credenciais_sao_recebidas_por_variaveis():
    assert "POSTGRES_USER: ${POSTGRES_USER:-postgres}" in COMPOSE
    assert "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}" in COMPOSE
    assert "POSTGRES_DB: ${POSTGRES_DB:-unb_core}" in COMPOSE
