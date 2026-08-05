# API

Estado atual: API FastAPI versionada em `/api/v1`, compartilhada pelos
frontends web e mobile. Autenticação protege os dados próprios de banca,
apostas, favoritos e preferências. O roadmap mestre não prevê quebra de contrato:
jobs internos serão desacoplados mantendo as respostas públicas existentes.

Esta seção reunirá a documentação da API do UltraStats AI.

Documentos previstos:

- endpoints;
- autenticação;
- schemas;
- respostas;
- tratamento de erros;
- versionamento;
- exemplos de integração.
### `GET /api/v1/paper-trading`

Retorna o estado auditável da banca sintética, métricas consolidadas do último
ciclo de aprendizado e até 100 apostas fictícias recentes. Esse recurso não lê
nem modifica dados financeiros dos usuários.

Parâmetros opcionais: `status` (`pending`, `settled`, `won`, `lost`, `void` ou
`unsupported`), `limit` (máximo 1000) e `offset`. A resposta inclui contagens
da carteira ativa e do dia, identificação da partida e timestamps de
criação/liquidação. `counts.executed` e `counts.shadow` separam exposição de
observação; cada decisão informa `execution_mode` e `recommendation_tier`.
As métricas da carteira usam os nomes canônicos `paper_roi`,
`paper_brier_score`, `paper_drawdown` e `mean_clv`.
