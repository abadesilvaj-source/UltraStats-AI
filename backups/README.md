# Backup portátil do UltraStats AI

Este diretório acompanha o estado persistente usado na migração para outro computador.

Conteúdo:

- `ultrastats_full.dump.part*`: dump lógico completo do PostgreSQL, dividido para respeitar o limite de arquivo do GitHub.
- `staging_logs.tar.gz`: volume de logs do ambiente G16.
- `staging_exports.tar.gz`: volume de exportações do ambiente G16.
- `legacy_postgres_volume.tar.gz`: cópia do volume PostgreSQL legado ainda presente no Docker.
- `SHA256SUMS.txt`: checksums de todos os pacotes.
- `restore-postgres.ps1`: recompõe e restaura o banco no container G16.

## Restauração no novo computador

1. Instale Git, Docker Desktop e habilite Docker Compose.
2. Clone o repositório incluindo todos os arquivos.
3. Abra PowerShell na raiz do projeto.
4. Inicie somente o PostgreSQL:

   ```powershell
   docker compose --env-file .env.staging.g16.local -f docker-compose.staging.yml -p ultrastats-g16 up -d postgres
   ```

5. Restaure o banco:

   ```powershell
   .\backups\restore-postgres.ps1
   ```

6. Inicie os demais serviços:

   ```powershell
   docker compose --env-file .env.staging.g16.local -f docker-compose.staging.yml -p ultrastats-g16 up -d --build
   ```

O restaurador valida todos os checksums antes de alterar o banco. A restauração usa `--clean --if-exists`, portanto deve ser executada no banco novo destinado à migração.

