# Match Domain

## 1. Estado da implementação

O Match Context está em desenvolvimento incremental na G5.8. A primeira fatia,
G5.8.A, implementa a fundação necessária para as demais entidades subordinadas
do agregado.

## 2. Agregado

`Match` é a raiz do agregado e atualmente controla:

- identidade canônica da partida;
- competição e temporada;
- fase e rodada opcionais;
- natureza e estado atual;
- data esportiva e horário UTC;
- exatamente dois `MatchParticipant`;
- ownership e substituição imutável dos participantes.

## 3. Participantes

`MatchParticipant` representa um lado contextual da partida. A entidade
referencia `Team` apenas por `TeamId` e não controla o ciclo de vida da equipe.

Invariantes implementadas:

- o participante pertence a exatamente um `Match`;
- cada partida possui os papéis únicos `HOME` e `AWAY`;
- identidades, equipes, papéis e ordens não se repetem;
- placares não podem ser negativos;
- participantes definidos exigem `TeamId`;
- participantes ainda indefinidos usam placeholder e não criam equipes
  artificiais;
- a resolução de um placeholder preserva a identidade do participante.

## 4. Programação

Uma partida em estado `SCHEDULED` exige ao menos:

- `DomainDate`, quando apenas a data esportiva é conhecida; ou
- `UtcTimestamp`, quando o horário programado está disponível.

Reagendamentos preservam o `MatchId`. O histórico detalhado de alterações será
implementado na G5.8.B.

## 5. Limites da fatia

A fundação ainda não implementa a política completa de transições de estado.
Também permanecem para as próximas fatias:

- `MatchScheduleChange`;
- `MatchVenue`;
- `MatchOfficial`;
- `MatchPeriod`;
- `MatchSquad`;
- `Lineup` e `LineupEntry`;
- `MatchEvent`;
- `MatchStatistic`;
- interrupções, decisões e revisões.

## 6. Dependências

O contexto depende apenas de tipos canônicos compartilhados e identificadores
dos contextos Competition e Team. Não depende de ORM, banco de dados ou
providers concretos.

## 7. Validação

Os testes estão em `tests/unit/domain/match`. O comando padrão do projeto cobre
100% das linhas e branches do domínio canônico.
