# Recommendation accuracy v3

Esta evolução melhora a confiabilidade probabilística do UltraStats sem prometer
100% de acerto. Precisão, cobertura e retorno financeiro são métricas distintas.

## Controles implementados

1. Métricas segmentadas por competição, família, faixa de odd e antecedência.
2. Calibração monotônica por faixas com encolhimento beta-binomial.
3. Política seletiva com meta de acerto, cobertura observada e abstenção.
4. Intervalo de incerteza condicionado ao segmento para decisões conservadoras.
5. Modelos e calibradores específicos por competição e mercado.
6. Features de estádio, descanso, horário, calendário e importância da competição.
7. Indicadores explícitos de escalações, lesões e estatísticas de jogadores.
8. Regimes separados: antecipado, mesmo dia, pós-escalação e ao vivo.
9. Movimento de odds: abertura, atual, velocidade, casas e closing line.
10. Drift por segmento comparando Brier histórico e recente.
11. Walk-forward temporal com corte anterior à partida.
12. Ensemble dinâmico conforme cobertura do mercado e drift.
13. Amostra mínima antes de ativar uma política segmentada.
14. Brier, log loss, acerto, ROI flat-stake, ROI oficial, CLV e drawdown.
15. Fractional Kelly limitado por categoria de recomendação.

## Categorias

- `high_confidence`: limite seletivo atendido e segmento sem drift.
- `statistical_value`: expectativa conservadora positiva.
- `experimental`: projeção com exposição máxima reduzida e aviso claro.

Segmentos com menos de 30 resultados liquidados permanecem inativos. Odds ausentes
não são inventadas; nesses casos há projeção, mas não valor financeiro confirmado.
