# Catálogo canônico de métricas

Atualizado em: 2 de agosto de 2026.

Este catálogo elimina nomes ambíguos e define uma única origem para cada
métrica decisória. Telas podem reapresentar valores, mas não recalculá-los.

| Nome canônico | Definição | Fonte oficial | Não confundir com |
|---|---|---|---|
| `raw_statistics_coverage` | encerradas com estatística / todas encerradas na janela | `MaturityService` | cobertura elegível |
| `eligible_statistics_coverage` | elegíveis com estatística / elegíveis | `MaturityService` | acurácia |
| `fresh_odds_coverage` | elegíveis com odd dentro do SLA / elegíveis cobertas | `MaturityService` | existência histórica de odd |
| `selective_coverage` | previsões acima do gate / previsões auditadas | política de decisão | cobertura de dados |
| `brier_score` | média de `(p-y)²` em coorte temporal | validação operacional | ROI |
| `calibration_error` | erro absoluto ponderado por faixa | validação operacional | acurácia simples |
| `paper_hit_rate` | ganhas / liquidadas suportadas | `PaperTradingService` | taxa prevista |
| `paper_roi` | lucro / stake das executadas liquidadas | `PaperTradingService` | shadow ou aposta real |
| `paper_drawdown` | queda percentual do pico da carteira | `PaperTradingService` | perda nominal |
| `mean_clv` | média de `odd_execução/odd_fechamento - 1` | `PaperTradingService` | ROI realizado |
| `official_roi` | lucro / stake de bilhetes reais liquidados | performance de banca | paper ROI |

## Regras

- denominador, janela, timezone e filtros acompanham toda métrica;
- `null` significa ausência de evidência; não é convertido em zero ou 100%;
- paper, shadow, backtest e apostas registradas nunca são agregados juntos;
- valores globais sempre oferecem recorte por mercado/competição quando houver
  amostra suficiente;
- frontend formata, mas não recalcula métricas;
- novos nomes exigem atualização deste catálogo e teste de contrato.

## Duplicações descontinuadas

- “cobertura” sem qualificador;
- “taxa de acerto” misturando previsão e aposta;
- ROI calculado com pendentes ou shadow stake zero;
- maturidade geral usada como substituta de qualidade preditiva;
- estatísticas globais usadas para promover segmento local.
