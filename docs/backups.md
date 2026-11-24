# Backups e restauração do banco de dados

Os comandos desta página devem ser executados no PowerShell, na raiz do
repositório, com o Docker Desktop em execução.

## Como os backups funcionam

O serviço `db-backup` cria um backup completo do PostgreSQL ao iniciar e,
depois, a cada 24 horas. Os arquivos ficam na pasta `backups/` da raiz do
projeto, com nomes no formato `unb_core-AAAAMMDD-HHMMSS.dump`. Arquivos com
mais de 7 dias são removidos automaticamente.

Para iniciar a aplicação e o serviço de backup:

```powershell
docker compose up --build -d
```

## Verificar os backups

Confira os logs do serviço. Uma execução bem-sucedida deve exibir
`Backup completed`:

```powershell
docker compose logs db-backup
```

Para listar os arquivos disponíveis, do mais recente ao mais antigo:

```powershell
Get-ChildItem .\backups\*.dump | Sort-Object LastWriteTime -Descending |
  Format-Table Name, Length, LastWriteTime
```

Para executar um backup imediatamente, recrie o serviço `db-backup`:

```powershell
docker compose up -d --force-recreate db-backup
```

Confira os logs novamente para confirmar que a execução terminou com
`Backup completed`.

Para verificar se um arquivo pode ser lido e listar sua estrutura, substitua
`NOME_DO_ARQUIVO.dump` por um arquivo existente na pasta `backups/`:

```powershell
docker compose exec db-backup pg_restore --list /backups/NOME_DO_ARQUIVO.dump
```

Essa verificação não altera o banco. Se os logs indicarem `Backup failed`,
nenhum arquivo novo será mantido. Como os arquivos antigos continuam sujeitos
à retenção de 7 dias, copie periodicamente `backups/` para um local seguro,
como um HD externo ou armazenamento em nuvem. A pasta é ignorada pelo Git e
não deve ser enviada ao repositório.

## Restaurar um backup

> **Atenção:** a restauração substitui o conteúdo atual do banco `unb_core`
> pelos dados do arquivo escolhido. Antes de restaurar, confirme o nome do
> arquivo e, se necessário, faça uma cópia externa do backup.

Pare o backend, informe o nome do arquivo e execute o serviço de restauração:

```powershell
docker compose stop backend
$env:RESTORE_FILE = "NOME_DO_ARQUIVO.dump"
docker compose run --rm db-restore
```

Substitua `NOME_DO_ARQUIVO.dump` por um arquivo existente em `backups/`.
Antes de substituir o banco, o serviço cria um backup de segurança do estado
atual, com o nome `unb_core-before-restore-*.dump`.

Só inicie o backend novamente se a restauração terminar com `Restore completed`
e sem erros anteriores:

```powershell
Remove-Item Env:RESTORE_FILE
docker compose start backend
```

Se o arquivo não existir ou `RESTORE_FILE` não estiver definido, a restauração
é cancelada. Para instruções de inicialização dos serviços, consulte
[Como rodar o projeto](como-rodar.md).
