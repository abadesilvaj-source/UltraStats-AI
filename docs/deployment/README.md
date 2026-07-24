# Implantação

Esta seção reúne documentos relacionados à execução e implantação do UltraStats AI.

Documentos previstos:

- execução com Docker;
- configuração de ambiente;
- inicialização no Windows;
- scheduler;
- persistência de dados;
- logs e monitoramento.

## Staging da release candidate

- configuração: `../../docker-compose.staging.yml`;
- ambiente de referência: `../../.env.staging.example`;
- smoke test: `python -m scripts.release_smoke`;
- release notes: [`v0.1.0-rc.1`](../releases/v0.1.0-rc.1.md);
- runbook: [`Runbook de Produção`](../operations/production-runbook.md).
