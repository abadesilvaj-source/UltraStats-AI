# Experiência do Usuário

## Objetivo

A G12 organiza os recursos analíticos do UltraStats AI em uma experiência
única, acessível e personalizável. O Experience Context mantém preferências e
interações do usuário separado dos motores estatístico, preditivo, de
recomendação e de risco.

## Navegação

O hub `16_Experiencia.py` reúne:

- home;
- partidas;
- mercados;
- análises;
- sugestões;
- equipes;
- competições;
- favoritos;
- alertas;
- perfil;
- comparação de cenários;
- linha do tempo;
- busca em linguagem natural;
- relatórios;
- notificações.

O modo simples reduz detalhes técnicos. O modo avançado expõe métricas e
proveniência. Preferências de redução de movimento e alto contraste fazem parte
do perfil persistente.

## Descoberta e decisão

A busca normaliza caixa e acentos, considera títulos e palavras-chave e devolve
resultados por relevância determinística. A comparação de cenários apresenta
lucro esperado a partir de probabilidade, odd e stake. A linha do tempo combina
eventos por instante e identidade estável.

O indicador discreto de atualização classifica os dados como `fresh`, `stale`
ou `clock_skew`, sem interromper a navegação.

## Interações persistentes

As tabelas da G12 são:

- `user_experience_profiles`;
- `user_favorites`;
- `user_alerts`;
- `user_notifications`;
- `push_subscriptions`;
- `automatic_reports`.

Favoritos são idempotentes por usuário e entidade. Alertas aceitam operadores
comparativos explícitos. Notificações possuem feed e estado de leitura.
Assinaturas push exigem endpoint HTTPS e chave pública. Relatórios automáticos
são ordenados e reproduzíveis.

A migration reversível `e5c01372e228` cria todas as estruturas e índices.

## Canais

Os únicos canais suportados são:

- dentro da aplicação;
- push.

Email, Telegram, Discord e WhatsApp não fazem parte do contrato. O envio
externo de push usa as assinaturas persistidas e poderá receber um adapter de
infraestrutura específico no ambiente de produção.

## Garantias

A G12 foi concluída com 2.527 testes e 100% de cobertura de linhas e branches.
Os testes cobrem validações, modos, acessibilidade, alertas, busca, cenários,
timeline, atualização, relatórios, CRUD persistente, assinaturas push,
notificações e reversão da migration.
