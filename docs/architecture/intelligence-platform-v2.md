# Plataforma de inteligência v2

> Atualização de 2 de agosto de 2026: “modelo registrado” não é sinônimo de
> ensemble executável. Somente `results` e `goals` possuem hoje combinação real
> de probabilidades champion/challenger. As demais famílias usam seus baselines.

Resultados combinam Poisson, Elo e ML temporal; gols e BTTS combinam Poisson e
ML. Champion e challenger produzem forecasts persistidos. Treino e inferência
ainda podem ocorrer dentro de um ciclo amplo; a G27 irá separá-los em jobs
menores, mantendo o último champion sempre disponível.

Esta evolução transforma os motores estatístico e de recomendações em um
ciclo científico observável. Nenhuma promoção utiliza partidas posteriores ao
corte do treinamento e nenhum desafiante assume produção sem validação.

## Componentes

1. **Modelos especializados:** resultados, gols, escanteios, cartões,
   jogadores e mercados auxiliares. Gols usam Poisson; cartões e escanteios
   usam binomial negativa para representar superdispersão.
2. **Ensemble contextual:** pesos por família e peso variável do consenso de
   mercado conforme o número de casas presentes.
3. **Amostras contextuais:** força, ataque, defesa, descanso, mando,
   escalações, ausências, forma e competição.
4. **Validação temporal:** expanding-window walk-forward ordenado pelo
   instante da auditoria.
5. **Gates por mercado:** amostra, Brier, calibração e estabilidade separados.
6. **Champion–challenger:** campeão e desafiante em `shadow` por família.
7. **Feature store temporal:** valores, origem e `as_of`, sempre anteriores ao
   início da partida.
8. **Qualidade:** incidentes idempotentes para estatísticas, odds e status.
9. **Explicabilidade:** versão, corte, variáveis, fatores e decisão.
10. **Avaliação financeira:** ROI, yield, acerto, drawdown e CLV somente para
    apostas oficiais liquidadas.
11. **Backtester:** folds temporais reproduzem treino e validação subsequente.
12. **Diversidade:** correlação fica visível e limita somente a prioridade de
    exposição.
13. **Idempotência:** fingerprints impedem duplicação de artefatos.
14. **Contratos:** `frontend/src/api-contract.ts` é verificado no build.
15. **Fila persistente:** prioridade, tentativas, backoff, falha e conclusão.

## Persistência

- `feature_snapshots`
- `data_quality_incidents`
- `model_deployments`
- `temporal_backtests`
- `processing_tasks`
- `prediction_explanations`

## Regras de segurança científica

- Nunca usar informação posterior ao início da partida.
- Nunca fabricar ROI ou CLV sem apostas oficiais.
- Nunca promover challenger sem melhora fora da amostra.
- Não esconder previsões correlacionadas; sinalizar o risco.
- Não interpretar cobertura operacional como taxa de acerto.

O pipeline materializa previsões e recomendações e depois atualiza essa
plataforma. A tela **Modelos e aprendizado** apresenta feature store, famílias,
shadow models, backtests, explicações, incidentes e fila.
