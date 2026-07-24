# Gestão de Risco e Portfólio

## Objetivo

A G11 converte recomendações seguras em planos financeiros controlados. O
contexto preserva a decisão do usuário: ele calcula stake, exposição e
desempenho, mas não executa apostas.

## Fluxo de decisão

```text
recomendações seguras + banca + perfil + exposição atual
                              |
                              v
                 Kelly integral e fracionado
                              |
                              v
        limites por aposta, dia, competição e mercado
                              |
                              v
             limite de posições correlacionadas
                              |
                              v
        portfólio ordenado pelo Opportunity Score
                              |
                              v
       snapshot + ROI + yield + drawdown + auditoria
```

## Perfis

O motor oferece três presets:

| Perfil | Kelly | Máx. por aposta | Máx. diário | Correlação |
| --- | ---: | ---: | ---: | ---: |
| Conservador | 25% | 1% | 5% | 1 |
| Moderado | 50% | 2% | 10% | 1 |
| Agressivo | 75% | 3% | 15% | 2 |

Cada perfil também possui limites próprios por competição e mercado. Os
valores são configurações explícitas e podem ser substituídos por um perfil
válido personalizado.

## Sizing e otimização

O Kelly integral é calculado por:

```text
Kelly = (probabilidade × odd - 1) / (odd - 1)
```

Valores negativos são convertidos em zero. A stake proposta aplica a fração de
Kelly do perfil e é então limitada, simultaneamente, pelo saldo, máximo por
aposta, exposição diária restante, exposição por competição e exposição por
mercado. Candidatos são processados por Opportunity Score decrescente.

O motor bloqueia candidatos sem Kelly positivo, sem capacidade de exposição ou
que ultrapassem o limite de posições com a mesma chave de correlação. Os
motivos permanecem no snapshot.

## Simulação e desempenho

O simulador reaplica a estratégia sobre uma sequência determinística de
resultados e compõe a banca após cada aposta. A curva resultante produz:

- lucro líquido;
- ROI sobre a banca inicial;
- yield sobre o volume apostado;
- drawdown máximo relativo ao pico anterior.

## Persistência

`risk_profiles` mantém um perfil vigente por usuário.
`portfolio_snapshots` preserva banca, exposição, posições, bloqueios e métricas
de cada cálculo. A migration reversível `d4bf1261d117` cria as duas tabelas e o
índice de histórico.

O painel `15_Risco_e_Portfolio.py` apresenta o snapshot mais recente, suas
posições, bloqueios e métricas de desempenho.

## Garantias

A G11 foi concluída com 2.506 testes e 100% de cobertura de linhas e branches.
Os cenários cobrem perfis, validações, Kelly, todos os limites de exposição,
correlação, ordenação, composição, ROI, yield, drawdown, persistência, upsert,
histórico e reversão da migration.
