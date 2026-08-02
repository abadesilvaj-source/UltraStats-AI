# API

Estado atual: API FastAPI versionada em `/api/v1`, compartilhada pelos
frontends web e mobile. Autenticação protege os dados próprios de banca,
apostas, favoritos e preferências. O roadmap G27 não prevê quebra de contrato:
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
