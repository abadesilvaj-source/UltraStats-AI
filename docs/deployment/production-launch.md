# Produção

> PAUSADO — documento de referência. Nenhuma publicação deve ser executada sem
> nova autorização explícita e conclusão do G42.

## Implantação

1. Copiar `.env.production.example` para `.env.production`.
2. Substituir placeholders e proteger o arquivo fora do repositório.
3. Publicar imagens independentes de backend e frontend.
4. Apontar `APP_DOMAIN` para o host.
5. Validar `docker compose -f docker-compose.production.yml config`.
6. Fazer backup, aplicar migrations e iniciar os serviços.

O Caddy termina TLS. PostgreSQL e API permanecem na rede interna; somente o
frontend é exposto pelo proxy.

## Operação contínua

- monitorar scheduler, backend e frontend;
- revisar qualidade, cobertura, conflitos e cotas dos provedores;
- manter logs, backups testados e procedimento de rollback;
- nunca registrar tokens ou dados sensíveis em logs.
