# Match Domain

## 1. Estado da implementação

O Match Context foi concluído na G5.8. O agregado cobre sua fundação, ciclo de
vida, agenda, local, oficiais, períodos, convocação, escalação, eventos,
estatísticas, interrupções, decisões e revisões.

## 2. Agregado

`Match` é a raiz do agregado e atualmente controla:

- identidade canônica da partida;
- competição e temporada;
- fase e rodada opcionais;
- natureza e estado atual;
- data esportiva e horário UTC;
- transições válidas do ciclo de vida;
- histórico imutável de reagendamentos;
- local principal atual e histórico de locais anteriores;
- oficiais e períodos esportivos;
- convocados, escalações e entradas;
- eventos cronológicos e placar resumido;
- estatísticas, interrupções, decisões e revisões;
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

## 6. Local da partida

`MatchVenue` representa o uso contextual de um estádio ou cidade por uma
partida. Ele referencia `Stadium` por `VenueId` e `City` por `CityId`, sem
controlar o ciclo de vida dessas entidades geográficas.

O contexto preserva:

- papel e estado do local;
- estádio e cidade conhecidos;
- superfície e sua condição;
- clima, temperatura, umidade, vento e altitude;
- capacidade estrutural, operacional, limite e público;
- campo neutro, ambiente coberto, teto e portões fechados;
- uso temporário ou alternativo;
- confirmação e intervalo de validade.

O agregado aceita no máximo um `MatchVenue` principal vigente. A operação
`assign_venue` encerra o principal anterior, mantém esse registro no histórico,
adiciona o novo local confirmado e sincroniza `Match.stadium_id`. Identidades
duplicadas, ownership incorreto e divergências com o atalho atual são
rejeitados.

As capacidades obedecem à hierarquia estrutural, operacional, limite e público.
Portões fechados não aceitam público, teto fechado exige ambiente coberto e a
confirmação deve ser coerente com o estado do local.

## 7. Operação esportiva

As entidades operacionais são subordinadas ao `Match` e não possuem ciclo de
vida independente:

- `MatchOfficial` registra a função exercida por pessoa, árbitro ou placeholder;
- `MatchPeriod` preserva ordem, duração, acréscimos, timestamps e placar;
- `MatchSquad` representa a lista de convocados de cada participante;
- `Lineup` preserva versões da escalação;
- `LineupEntry` relaciona pessoas e jogadores à escalação contextual;
- `MatchEvent` registra acontecimentos em ordem cronológica;
- `MatchStatistic` armazena métricas por escopo e unidade;
- `MatchInterruption` registra paralisação e retomada;
- `MatchDecision` preserva decisões esportivas e administrativas;
- `MatchRevision` audita correções e alterações de versão.

Todas as coleções são tuplas imutáveis. O agregado rejeita tipos incorretos,
ownership divergente e identidades duplicadas. `record_event` acrescenta o
evento e, quando houver placar posterior completo, sincroniza os placares e o
vencedor resumido dos participantes.

## 8. Integração com Tie

`Tie` permanece no Competition Context e referencia partidas por
`TieMatchReference`. A integração utiliza somente `MatchId`, preservando as
fronteiras dos agregados e impedindo que o confronto controle o ciclo de vida
da partida.

## 9. Limites do contexto

Persistência, serviços de aplicação, ingestão de providers e projeções
analíticas pertencem às etapas posteriores. A G5.8 entrega o modelo canônico de
domínio, sem ORM ou dependência de infraestrutura.

## 10. Dependências

O contexto depende apenas de tipos canônicos compartilhados e identificadores
dos contextos Competition e Team. Não depende de ORM, banco de dados ou
providers concretos.

## 11. Validação

Os testes estão em `tests/unit/domain/match`. O comando padrão do projeto cobre
100% das linhas e branches do domínio canônico. A validação final da G5.8
concluiu 2.388 testes, 4.494 statements e 1.372 branches.
