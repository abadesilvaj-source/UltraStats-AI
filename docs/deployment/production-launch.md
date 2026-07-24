# Produção e lançamento

Este pacote encerra o trabalho implementável das etapas G18–G22. A publicação
real permanece deliberadamente bloqueada até que exista um host, domínio e
aceite jurídico.

## Implantação

1. Copiar `.env.production.example` para `.env.production` no host.
2. Substituir todos os placeholders e proteger o arquivo fora do repositório.
3. Apontar o DNS de `APP_DOMAIN` para o host.
4. Executar `docker compose -f docker-compose.production.yml config`.
5. Fazer backup, executar migrations e subir os serviços.
6. Registrar evidência e executar `python -m scripts.launch_gate production evidence.json`.

O Caddy termina TLS automaticamente. PostgreSQL permanece em rede interna; o
dashboard é o único serviço exposto por proxy.

## Operação contínua

- sincronização a cada 30 minutos, com prioridade e fallback entre providers;
- health check do scheduler e dashboard;
- logs persistentes, alertas, backup/restore e rollback conforme o runbook;
- revisão semanal de qualidade, cobertura, conflitos e limites das APIs;
- nunca registrar tokens, payloads sensíveis ou dados pessoais em logs.

## Piloto

O piloto deve durar ao menos 7 dias, possuir 5 usuários ativos, 100 previsões,
disponibilidade de 99%, feedback médio de 3,5/5 e no máximo 2 incidentes.
Preencher a evidência e executar `python -m scripts.launch_gate pilot pilot.json`.
Resultados financeiros nunca substituem os critérios de confiabilidade.

## Lançamento público

O gate final exige produção e piloto aprovados, revisão jurídica, contato de
privacidade, consentimento versionado, confirmação de maioridade, jogo
responsável e autoexclusão. A revisão deve considerar os países de operação.

## Evolução pós-lançamento

Trabalhar em ciclos mensais: observar métricas, selecionar hipótese, executar
experimento controlado, revisar calibração/risco, publicar ou reverter e
registrar a decisão. Prioridades: qualidade de dados, calibração, confiabilidade,
retenção responsável e custo operacional.
