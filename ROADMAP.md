# Roadmap UltraStats AI

O roadmap detalhado e oficial está em
[`docs/development/roadmap.md`](docs/development/roadmap.md).

## Estado consolidado

- [x] G1–G5 — Fundação e Domínio Canônico
- [x] G6 — Providers
- [x] G7 — Identidade e Data Fusion
- [x] G8 — Motor Estatístico
- [x] G9 — Modelos Preditivos
- [x] G10 — Motor de Recomendações
- [x] G11 — Gestão de Risco e Portfólio
- [x] G12 — Experiência do Usuário
- [x] G13 — Motor ao Vivo
- [x] G14 — Produção, Segurança e Escalabilidade
- [x] G15 — Release Candidate e Validação Integrada

- [x] G15.1 — Motor Multi-Provider Real
- [x] G15.2 — Dataset, Backtesting e Calibração

Versão estável atual: `v0.1.0`.

## G16 — Homologação em staging

- [x] ambiente isolado, migrations, scheduler, API e frontend;
- [x] carga, backup/restore, rollback e controles de segurança;
- [x] coleta real de OpenLigaDB, Football-Data.co.uk e StatsBomb Open Data;
- [x] API-Football homologada com fixtures, odds e estatísticas reais;
- [x] Football-Data.org autenticada e homologada com token real;
- [x] aceite operacional registrado;
- [x] promoção para `v0.1.0`.

Status: G16 concluída integralmente.

## G17–G22 — Operação e lançamento

- [x] consolidação integral no `main`;
- [x] pacote de produção com Docker Compose e HTTPS;
- [x] operação contínua e gates auditáveis;
- [x] preparação de piloto e conformidade;
- [x] fundação de evolução pós-lançamento.

Para o uso pessoal atualmente definido, piloto comercial e aprovação jurídica
ficam fora do escopo. Próximo passo: implantação privada em nuvem.

## G23 — Maturidade operacional e preditiva

- [x] cobertura e qualidade multi-provider mensuráveis;
- [x] escalações, confirmação e continuidade no modelo;
- [x] validação temporal, métricas por mercado e drift;
- [x] catálogo champion/challenger;
- [x] recomendações por EV conservador e atualidade de odds;
- [x] análise de risco e correlação de múltiplas;
- [x] continuidade e deduplicação do motor ao vivo;
- [x] observabilidade no backend e frontend.

Status: G23 implementada. A qualidade das recomendações continuará crescendo
com o backfill automático e com a ampliação da amostra auditada.
## G24 — Neutralidade total de provedores e SLA 90%–100% ✅

- [x] Remover pesos e prioridades globais por provedor.
- [x] Aplicar consenso por campo com desempate por recência.
- [x] Tornar identidade, fixtures, odds, escalações e live multiprovedor.
- [x] Preservar estatísticas complementares não nulas entre fontes.
- [x] Separar SLA operacional de cobertura bruta.
- [x] Expor capacidades, elegibilidade, atualidade e neutralidade no painel.
- [x] Documentar a arquitetura e os critérios auditáveis.
## G26 — Motor estatístico e recomendador avançados ✅

- [x] Elo contextual com recência, adversário, mando e descanso.
- [x] Modelos especializados para 1X2, gols, escanteios e cartões.
- [x] Ensemble de Poisson, ratings, escalações e consenso de mercado.
- [x] Calibração segmentada por competição e mercado.
- [x] Política explícita de “Sem aposta”.
- [x] Controle de mercados correlacionados.
- [x] Integração ao walk-forward, drift e champion/challenger existentes.
- [x] Documentação e testes de regressão.
