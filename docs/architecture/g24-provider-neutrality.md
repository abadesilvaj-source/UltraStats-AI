# G24 — Neutralidade total de provedores

## Regra de decisão

Nenhum provedor possui prioridade global. Toda observação capaz de fornecer um
campo entra com peso-base `1.0`. A decisão é feita campo a campo:

1. consenso entre valores normalizados;
2. em empate, vence a observação mais recente;
3. valores ausentes nunca apagam valores válidos;
4. a procedência e os conflitos permanecem registrados.

Essa regra vale para partidas, placares, estatísticas, odds, escalações e estado
ao vivo. A entidade canônica é resolvida pela camada de identidade; nenhum
identificador de um provedor é tratado como identificador universal.

## Complementaridade

Cada fonte participa somente das capacidades que oferece. API-Football e
Sportmonks podem complementar estatísticas, escalações e eventos ao vivo;
The Odds API, Football-Data.co.uk e API-Football complementam odds; os demais
provedores contribuem com calendário, identidade, placares ou histórico.

## Índice de qualidade

O painel separa duas medidas:

- **SLA operacional**: cobertura das partidas elegíveis, atualidade dos feeds,
  disponibilidade, previsões e identidade multiprovedor;
- **cobertura bruta**: proporção sobre todos os jogos armazenados, inclusive os
  que nenhum plano contratado permite enriquecer.

O alvo de 90%–100% se aplica ao SLA operacional. A cobertura bruta continua
visível e não é artificialmente inflada. Uma partida só entra no denominador
elegível de uma capacidade quando existe identidade em um provedor que declara
essa capacidade. Escalações são medidas na janela operacional próxima ao jogo,
e ausência de snapshots ao vivo só é falha quando há jogo em andamento.

## Garantias implementadas

- peso-base igual para todas as fontes;
- fusão por campo, consenso e recência;
- promoção canônica de todas as fontes via identidade;
- odds resolvidas pelo par `provedor:id`;
- escalações e eventos ao vivo multiprovedor;
- estatísticas parciais complementares e não destrutivas;
- painel com matriz de capacidades, cobertura elegível e cobertura bruta;
- nome canônico `football_data` usado na saúde do provedor.
