# Reconstrução full-stack do UltraStats AI

## Objetivo

Separar definitivamente apresentação, aplicação, domínio, persistência e
processamento assíncrono. O frontend não acessa o banco nem importa serviços
Python; toda comunicação ocorre pela API versionada.

## Arquitetura

```text
React/Vite (porta 8516)
        |
        | HTTP JSON /api/v1
        v
FastAPI (porta 8000)
        |
        +-- consultas e comandos
        +-- validação de bilhetes e risco
        |
        v
PostgreSQL
        ^
        |
Scheduler -> coleta multi-provider -> normalização -> estatísticas
          -> ratings/features -> previsões/calibração -> recomendações
          -> liquidação simples/múltipla -> auditoria
```

O dashboard Streamlit permanece temporariamente na porta 8517 como console
administrativo legado. Ele não é mais a interface principal.

## Decisões

1. `src/ultrastats_ai` permanece como domínio canônico.
2. `app` orquestra persistência, coletores e casos de uso operacionais.
3. `backend` publica os casos de uso por FastAPI.
4. `frontend` contém a aplicação React derivada do protótipo fornecido.
5. Datas são armazenadas em UTC e serializadas no timezone solicitado; o
   padrão é `America/Sao_Paulo`.
6. Recomendações nunca são rótulos de treinamento. Resultados oficiais
   alimentam auditoria, ratings e calibração.
7. Um mercado só é operacional quando possui coleta de odd, previsão e regra
   de liquidação.

## Fluxo de dados

Cada sincronização:

1. verifica a saúde das fontes;
2. coleta partidas e odds;
3. preserva payload bruto e proveniência;
4. promove dados API-Football para o modelo operacional;
5. registra snapshots de partidas ao vivo;
6. coleta incrementalmente estatísticas de partidas encerradas;
7. liquida apostas e pernas de múltiplas;
8. audita todas as previsões da partida;
9. atualiza ratings de ataque, defesa, gols, cartões e escanteios;
10. utiliza os ratings atualizados nas previsões seguintes.

## Calibração

A calibração é automática após amostra mínima de 20 previsões auditadas na
mesma faixa de probabilidade e versão de modelo. O cálculo usa suavização
bayesiana para evitar mudanças abruptas com amostras pequenas. A probabilidade
original é sempre preservada para auditoria.

## Multi-provider

As fontes são coletadas pelo `MultiSourceEngine`. Payload bruto, saúde e
proveniência são preservados. API-Football continua como fonte operacional de
estatísticas e odds enquanto as demais fontes servem para cobertura,
confirmação e histórico. A evolução seguinte da fusão deve promover cada campo
canônico por uma matriz de autoridade, sem alterar os contratos da API.

## Limites do plano gratuito

`AUTO_STATS_MAX_PER_SYNC=1` limita consultas detalhadas por ciclo e prioriza
partidas com apostas pendentes. Aumentar esse valor exige conferir a cota do
plano. O feed ao vivo utiliza o lote de partidas já coletado; sua atualização
fica limitada ao intervalo do scheduler enquanto não houver uma cota dedicada.

## Segurança e integridade financeira

- odds são relidas do banco no momento do registro;
- partidas encerradas são bloqueadas;
- saldo é validado e debitado atomicamente;
- cada transação possui saldo anterior e posterior;
- seleções da mesma partida são bloqueadas em múltiplas até existir um modelo
  de correlação;
- uma perna anulada assume odd efetiva 1;
- qualquer perna perdida encerra a múltipla como perdida;
- liquidação é idempotente.
