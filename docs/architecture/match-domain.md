# Match Domain

## 1. Estado da implementação

O Match Context está em desenvolvimento incremental na G5.8. As fatias G5.8.A
e G5.8.B implementam a fundação do agregado, seu ciclo de vida e o histórico
auditável de alterações da agenda.

## 2. Agregado

`Match` é a raiz do agregado e atualmente controla:

- identidade canônica da partida;
- competição e temporada;
- fase e rodada opcionais;
- natureza e estado atual;
- data esportiva e horário UTC;
- transições válidas do ciclo de vida;
- histórico imutável de reagendamentos;
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

Reagendamentos preservam o `MatchId` e acrescentam um
`MatchScheduleChange` imutável. Cada registro contém identidade própria,
instante e motivo da alteração, além dos valores anterior e posterior da data
e do horário. O agregado rejeita mudanças sem nova agenda, sem motivo, sem
diferença efetiva, pertencentes a outra partida ou com identidade duplicada.

## 5. Ciclo de vida

`Match.change_status` aplica uma matriz explícita de transições. Ela cobre a
preparação da agenda, os estados pré-jogo, o andamento regulamentar e
adicional, interrupções e suspensões, além dos resultados terminais. Estados
terminais não aceitam novas transições.

O método `reschedule` é a operação controlada para alterar a agenda: registra o
histórico e devolve a partida no estado `SCHEDULED`.

## 6. Limites da fatia

Permanecem para as próximas fatias:

- `MatchVenue`;
- `MatchOfficial`;
- `MatchPeriod`;
- `MatchSquad`;
- `Lineup` e `LineupEntry`;
- `MatchEvent`;
- `MatchStatistic`;
- interrupções, decisões e revisões.

## 7. Dependências

O contexto depende apenas de tipos canônicos compartilhados e identificadores
dos contextos Competition e Team. Não depende de ORM, banco de dados ou
providers concretos.

## 8. Validação

Os testes estão em `tests/unit/domain/match`. O comando padrão do projeto cobre
100% das linhas e branches do domínio canônico. A validação da G5.8.B concluiu
2.296 testes.
