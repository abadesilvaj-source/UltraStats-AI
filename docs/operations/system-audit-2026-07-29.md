# Auditoria operacional — 29/07/2026

## Escopo

Auditoria ponta a ponta da coleta multiprovedor, API, frontend, gestão de banca,
apostas, liquidação, motor estatístico, previsões, recomendações, aprendizado,
risco, maturidade e scheduler.

## Resultado validado

- PostgreSQL, migrations, scheduler, API e frontend operacionais em Docker.
- 10 provedores monitorados e disponíveis no último ciclo.
- última sincronização completa concluída com sucesso;
- 2.346 partidas, 54.766 previsões e 125 mercados persistidos;
- 26 partidas com ficha estatística detalhada;
- 13.344 previsões auditadas;
- último dataset de validação com 2.623 amostras e gate aprovado;
- 100% das partidas elegíveis nas competições modeladas com previsões;
- 685 snapshots ao vivo persistidos;
- todas as rotas funcionais renderizadas sem erro de console;
- 2.698 testes automatizados aprovados e build de produção aprovado.

## Correções aplicadas

1. A cobertura preditiva passou a usar somente competições efetivamente
   modeladas como denominador.
2. O SLA do feed ao vivo passou a respeitar a cadência configurada, eliminando
   alertas falsos entre sincronizações.
3. Alertas operacionais resolvidos deixam de permanecer abertos.
4. A Zafronix deixou de anunciar estatísticas, eventos e escalações que não
   possuem contrato gratuito homologado.
5. A validação por competição/mercado passou a usar fallback hierárquico:
   amostra local pequena gera aviso e usa o mercado global validado; amostra
   local suficiente e ruim continua bloqueando a recomendação.
6. Falhas parciais de provedores passam a persistir a sincronização como
   `degraded`, com os motivos, em vez de parecer sucesso integral.
7. Reiniciar o scheduler não dispara nova coleta completa antes do intervalo,
   preservando a franquia das APIs.
8. O frontend passou a carregar previsões, inteligência e recomendações apenas
   nas rotas que consomem esses dados.

## Limitações reais

O índice operacional permanece abaixo do ideal principalmente por cobertura
externa, não por indisponibilidade do software:

- estatísticas detalhadas: 26 partidas;
- odds elegíveis: aproximadamente 10,5%;
- escalações na janela operacional: sem cobertura atual;
- nenhuma recomendação recente possui odd simultaneamente presente, atual,
  validada e com valor conservador positivo.

O limite `AUTO_STATS_MAX_PER_SYNC=2` é deliberado para não consumir a franquia
gratuita da API-Football. A aplicação continua aprendendo com placares finais
mesmo quando cartões, escanteios e demais estatísticas não estão disponíveis.

## Prioridades recomendadas

1. Ampliar primeiro a cobertura de estatísticas e odds; é o maior limitador de
   qualidade atual.
2. Adotar paginação e agregações SQL para reduzir a latência da consulta de
   recomendações conforme o histórico crescer.
3. Implementar promoção automática champion/challenger com shadow scoring.
4. Adicionar métricas temporais e alertas externos para latência, quota,
   cobertura e drift.
5. Manter backtests separados por competição e mercado quando cada grupo
   atingir amostra suficiente.
6. Se houver uso fora da máquina pessoal, adicionar autenticação, isolamento
   por usuário, backup automatizado e gestão externa de segredos.
