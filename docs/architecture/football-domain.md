# UltraStats AI — Domínio Central de Futebol

## 1. Objetivo

Este documento define as entidades esportivas centrais do UltraStats AI.

Essas entidades representam fatos relacionados ao futebol.

Elas não devem armazenar:

- probabilidades;
- recomendações;
- stakes;
- valor esperado;
- perfil de risco;
- preferências do usuário;
- payloads específicos de provedores.

Essas informações pertencem a outros contextos do sistema.

---

## 2. Identificadores internos

Toda entidade canônica deverá possuir um identificador interno criado pelo
UltraStats AI.

Formato recomendado:

```text
UUID
```

Exemplo:

```text
team_id = 6d77b114-b8df-49f7-bce8-a390b9f1f135
```

Esse identificador:

- não depende de nenhum provedor;
- não muda quando o provedor é alterado;
- não deve ser reutilizado;
- identifica unicamente a entidade dentro do UltraStats AI.

---

## 3. Identificadores externos

Os identificadores recebidos de APIs externas não deverão ser utilizados como
chave principal das entidades canônicas.

Exemplo:

```text
Equipe canônica:
team_id = UUID interno

Mapeamentos externos:
football_data = 66
api_football = 33
sportmonks = 9
```

Os identificadores externos serão armazenados em estruturas específicas de
mapeamento.

---

## 4. Campos comuns

Sempre que aplicável, as entidades deverão possuir:

```text
id
created_at
updated_at
is_active
```

Entidades históricas também poderão possuir:

```text
valid_from
valid_until
```

---

## 5. Exclusão lógica

Entidades esportivas não deverão ser removidas fisicamente apenas porque
deixaram de aparecer em algum provedor.

Deverá ser utilizado:

```text
is_active = false
```

A exclusão física ficará restrita a registros claramente inválidos, duplicados
ou criados por erro operacional.

---

## 6. Country

Representa um país ou território relacionado ao futebol.

### Campos principais

```text
country_id
name
official_name
code_alpha_2
code_alpha_3
fifa_code
flag_url
is_active
created_at
updated_at
```

### Regras

- `name` é obrigatório.
- Os códigos devem ser armazenados em letras maiúsculas.
- Um país pode não possuir código FIFA.
- Um país pode possuir várias competições.
- Um país pode possuir várias equipes.
- Competições continentais podem possuir equipes de diferentes países.
- Uma competição internacional pode não estar vinculada a apenas um país.

---

## 7. Competition

Representa uma competição de futebol.

### Exemplos

```text
Campeonato Brasileiro Série A
Premier League
Copa do Brasil
UEFA Champions League
Copa Libertadores
FIFA World Cup
```

### Campos principais

```text
competition_id
name
short_name
official_name
competition_type
scope
gender
country_id
organizer
logo_url
founded_year
is_active
created_at
updated_at
```

### CompetitionType

```text
LEAGUE
CUP
SUPER_CUP
PLAYOFF
FRIENDLY
QUALIFICATION
TOURNAMENT
```

### CompetitionScope

```text
DOMESTIC
CONTINENTAL
INTERNATIONAL
REGIONAL
```

### Gender

```text
MALE
FEMALE
MIXED
UNSPECIFIED
```

### Regras

- Uma competição pode possuir várias temporadas.
- Mudanças de patrocinador não devem criar automaticamente uma nova competição.
- O nome comercial pode mudar sem alterar a identidade da competição.
- Competições eliminatórias e ligas utilizam a mesma entidade.
- O tipo da competição diferencia sua estrutura.
- Competições amistosas devem ser claramente classificadas.
- Competições encerradas devem permanecer registradas como inativas.

---

## 8. Season

Representa uma edição temporal de uma competição.

### Exemplos

```text
Brasileirão 2026
Premier League 2026/2027
Champions League 2026/2027
Copa do Mundo 2026
```

### Campos principais

```text
season_id
competition_id
name
start_date
end_date
season_year_start
season_year_end
status
current_stage_id
is_current
created_at
updated_at
```

### SeasonStatus

```text
SCHEDULED
ACTIVE
COMPLETED
SUSPENDED
CANCELLED
```

### Regras

- Toda temporada pertence a uma competição.
- Uma competição pode possuir várias temporadas.
- Temporadas canceladas não devem ser excluídas.
- A nomenclatura oficial deve ser preservada.
- Competições realizadas em um único ano podem possuir o mesmo valor em
  `season_year_start` e `season_year_end`.
- Apenas uma temporada deve ser considerada atual para a mesma competição em
  um determinado período.

---

## 9. Stage

Representa uma fase de uma temporada.

### Exemplos

```text
Temporada regular
Fase de grupos
Oitavas de final
Quartas de final
Semifinal
Final
Playoffs
```

### Campos principais

```text
stage_id
season_id
name
stage_type
order_index
start_date
end_date
is_current
created_at
updated_at
```

### StageType

```text
REGULAR_SEASON
GROUP_STAGE
KNOCKOUT
ROUND_OF_32
ROUND_OF_16
QUARTER_FINAL
SEMI_FINAL
FINAL
PLAYOFF
QUALIFICATION
OTHER
```

### Regras

- Uma temporada pode possuir uma ou várias fases.
- Fases devem possuir uma ordem lógica.
- Nem toda competição utiliza fases explicitamente.
- Quando não existir uma fase explícita, poderá ser utilizada:

```text
REGULAR_SEASON
```

---

## 10. Round

Representa uma rodada ou agrupamento de partidas.

### Exemplos

```text
Rodada 1
Rodada 38
Oitavas de final
Jogo de ida
Jogo de volta
```

### Campos principais

```text
round_id
stage_id
name
number
round_type
start_date
end_date
created_at
updated_at
```

### RoundType

```text
REGULAR
KNOCKOUT
FIRST_LEG
SECOND_LEG
REPLAY
PLAYOFF
OTHER
```

### Regras

- Uma rodada pertence a uma fase.
- O campo `number` pode ser nulo.
- Rodadas eliminatórias podem utilizar nomes em vez de números.
- Rodadas com o mesmo significado não devem ser duplicadas dentro da mesma
  fase.

---

## 11. Team

Representa uma equipe de futebol.

### Exemplos

```text
Palmeiras
Manchester United
Brazil
Real Madrid Castilla
Barcelona Women
```

### Campos principais

```text
team_id
name
official_name
short_name
code
team_type
gender
country_id
city
founded_year
logo_url
primary_color
secondary_color
is_active
created_at
updated_at
```

### TeamType

```text
CLUB
NATIONAL_TEAM
YOUTH
RESERVE
WOMEN
AMATEUR
OTHER
```

### Regras

- Uma equipe deve possuir nome.
- Nome abreviado e código não são obrigatórios.
- Uma seleção nacional não precisa possuir cidade.
- Uma equipe pode participar de várias competições.
- Mudanças de nome não devem criar automaticamente uma nova equipe.
- Mudanças de escudo e cores devem preservar o histórico quando necessário.
- Equipes principal, reserva e de base devem ser entidades diferentes.
- Fusões, dissoluções e recriações de clubes devem ser analisadas
  individualmente.

---

## 12. TeamAlias

Representa nomes alternativos utilizados para identificar uma equipe.

### Campos principais

```text
team_alias_id
team_id
alias
normalized_alias
language
valid_from
valid_until
created_at
```

### Exemplo

```text
Manchester United
Manchester United FC
Man United
Manchester Utd
```

### Regras

- Uma equipe pode possuir vários aliases.
- Aliases auxiliam o processo de resolução de entidades.
- Um alias não deve ser considerado único sem contexto.
- País, competição e período podem ser utilizados para desambiguação.
- Aliases vazios não devem ser permitidos.

---

## 13. Player

Representa um jogador de futebol.

### Campos principais

```text
player_id
full_name
display_name
first_name
last_name
common_name
date_of_birth
gender
country_id
secondary_country_id
preferred_foot
primary_position
height_cm
weight_kg
photo_url
is_active
created_at
updated_at
```

### PreferredFoot

```text
RIGHT
LEFT
BOTH
UNKNOWN
```

### PlayerPosition

```text
GOALKEEPER
CENTRE_BACK
LEFT_BACK
RIGHT_BACK
DEFENSIVE_MIDFIELDER
CENTRAL_MIDFIELDER
ATTACKING_MIDFIELDER
LEFT_WINGER
RIGHT_WINGER
CENTRE_FORWARD
SECOND_STRIKER
UNKNOWN
```

### Regras

- O nome completo ou nome de exibição deve existir.
- Dois jogadores podem possuir o mesmo nome.
- Jogadores não devem ser identificados apenas pelo nome.
- Data de nascimento, equipe, posição e nacionalidade ajudam na identificação.
- A posição principal não deve ser considerada permanentemente imutável.
- Um jogador pode atuar em várias posições.
- Nacionalidade civil e nacionalidade esportiva podem ser diferentes.
- Jogadores aposentados devem permanecer cadastrados como inativos.

---

## 14. PlayerTeamMembership

Representa o vínculo de um jogador com uma equipe.

### Campos principais

```text
membership_id
player_id
team_id
shirt_number
start_date
end_date
membership_type
is_active
created_at
updated_at
```

### MembershipType

```text
PERMANENT
LOAN
YOUTH
TRIAL
UNKNOWN
```

### Regras

- O histórico de equipes não deve ser sobrescrito.
- Empréstimos devem ser registrados explicitamente.
- O número da camisa pertence ao vínculo entre jogador e equipe.
- Um jogador pode possuir múltiplos vínculos em situações específicas.
- Datas de início e término devem ser preservadas.
- Transferências não devem apagar os vínculos anteriores.

---

## 15. Coach

Representa um treinador ou integrante principal da comissão técnica.

### Campos principais

```text
coach_id
full_name
display_name
date_of_birth
country_id
photo_url
is_active
created_at
updated_at
```

### Regras

- Treinadores devem possuir histórico de vínculos.
- Mudanças de treinador podem afetar modelos estatísticos.
- Treinadores inativos devem permanecer no histórico.
- O mesmo treinador pode comandar equipes diferentes durante a mesma
  temporada.

---

## 16. CoachTeamMembership

Representa o vínculo de um treinador com uma equipe.

### Campos principais

```text
coach_membership_id
coach_id
team_id
role
start_date
end_date
is_interim
created_at
updated_at
```

### CoachRole

```text
HEAD_COACH
ASSISTANT_COACH
INTERIM_COACH
GOALKEEPER_COACH
FITNESS_COACH
OTHER
```

### Regras

- O treinador principal deve ser identificado.
- Treinadores interinos devem ser marcados.
- O histórico do comando técnico não deve ser apagado.
- Estatísticas por treinador utilizarão esse histórico.
- Mudanças de função devem preservar os vínculos anteriores.

---

## 17. Referee

Representa um árbitro.

### Campos principais

```text
referee_id
full_name
display_name
date_of_birth
country_id
photo_url
is_active
created_at
updated_at
```

### Regras

- Árbitros não devem ser identificados apenas pelo nome.
- Estatísticas disciplinares utilizarão o árbitro canônico.
- O histórico de partidas arbitradas deve ser preservado.
- Árbitros inativos não devem ser removidos do histórico.

---

## 18. Stadium

Representa um estádio.

### Campos principais

```text
stadium_id
name
official_name
city
country_id
capacity
latitude
longitude
surface_type
timezone
photo_url
is_active
created_at
updated_at
```

### SurfaceType

```text
NATURAL_GRASS
ARTIFICIAL_GRASS
HYBRID
OTHER
UNKNOWN
```

### Regras

- Um estádio pode ser utilizado por várias equipes.
- Uma equipe pode utilizar vários estádios.
- A capacidade pode variar ao longo do tempo.
- O fuso horário será importante para as partidas.
- Coordenadas geográficas são opcionais.
- Partidas realizadas em campo neutro devem ser identificadas.
- A capacidade não pode ser negativa.

---

## 19. TeamStadiumMembership

Representa o vínculo entre uma equipe e um estádio.

### Campos principais

```text
team_stadium_id
team_id
stadium_id
relationship_type
start_date
end_date
is_primary
created_at
updated_at
```

### RelationshipType

```text
HOME
TEMPORARY_HOME
TRAINING
SHARED
OTHER
```

### Regras

- Uma equipe pode possuir mais de um vínculo com estádios.
- O estádio principal deve ser identificado quando aplicável.
- Mudanças de estádio devem preservar o histórico.
- Estádios temporários não devem substituir silenciosamente o estádio
  principal.

---

## 20. Match

Representa uma partida de futebol.

### Campos principais

```text
match_id
competition_id
season_id
stage_id
round_id
home_team_id
away_team_id
stadium_id
referee_id
scheduled_at
started_at
ended_at
timezone
status
home_score
away_score
home_score_halftime
away_score_halftime
home_score_extra_time
away_score_extra_time
home_score_penalties
away_score_penalties
attendance
is_neutral_venue
has_extra_time
has_penalty_shootout
created_at
updated_at
```

### MatchStatus

```text
SCHEDULED
TIME_TO_BE_DEFINED
POSTPONED
CANCELLED
DELAYED
WARMUP
FIRST_HALF
HALFTIME
SECOND_HALF
EXTRA_TIME
PENALTY_SHOOTOUT
SUSPENDED
ABANDONED
FINISHED
AWARDED
```

### Regras

- Mandante e visitante devem ser equipes diferentes.
- A partida deve pertencer a uma competição e a uma temporada.
- `scheduled_at` deve ser armazenado em UTC.
- O fuso horário original deve ser preservado.
- Partidas adiadas não devem ser excluídas.
- Partidas remarcadas devem preservar o histórico de horários.
- O placar de pênaltis não deve ser somado ao placar normal.
- O placar da prorrogação deve ser registrado separadamente.
- Uma partida pode existir sem estádio ou árbitro inicialmente definidos.
- Eventos e placar devem ser validados entre si.
- O placar oficial não deve ser inferido apenas pelos eventos.
- Partidas suspensas e abandonadas devem ser diferenciadas.
- Resultados administrativos devem utilizar o estado `AWARDED`.
- Placares negativos não devem ser permitidos.

---

## 21. MatchScheduleHistory

Representa alterações no agendamento de uma partida.

### Campos principais

```text
schedule_history_id
match_id
previous_scheduled_at
new_scheduled_at
change_reason
source
changed_at
```

### Regras

- Alterações de horário devem preservar o valor anterior.
- Adiamentos e remarcações devem ser auditáveis.
- O horário atual permanece armazenado em `Match`.
- O histórico completo permanece em `MatchScheduleHistory`.
- Uma mudança de horário não deve criar automaticamente uma nova partida.

---

## 22. Formation

Representa uma formação tática.

### Campos principais

```text
formation_id
code
description
player_count
created_at
updated_at
```

### Exemplos

```text
4-3-3
4-2-3-1
3-5-2
4-4-2
```

### Regras

- A formação pode representar o início ou outro momento da partida.
- Mudanças táticas podem gerar snapshots.
- A formação não deve ser repetida como texto livre em vários registros.
- O código da formação deve possuir uma representação padronizada.
- O número de jogadores deve ser coerente com a formação.

---

## 23. Lineup

Representa a escalação de uma equipe em uma partida.

### Campos principais

```text
lineup_id
match_id
team_id
formation_id
coach_id
lineup_type
confirmed_at
source_confidence
created_at
updated_at
```

### LineupType

```text
PREDICTED
PROVISIONAL
CONFIRMED
UPDATED
```

### Regras

- Uma equipe pode possuir escalação provável e confirmada.
- A escalação confirmada não deve apagar a escalação provável.
- Alterações relevantes devem preservar o histórico.
- Uma escalação pertence a uma equipe dentro de uma partida.
- A equipe da escalação deve participar da partida.
- `source_confidence` representa a confiança no dado recebido.
- Previsões devem identificar qual versão da escalação foi utilizada.

---

## 24. LineupPlayer

Representa um jogador dentro de uma escalação.

### Campos principais

```text
lineup_player_id
lineup_id
player_id
position
shirt_number
role
field_position_x
field_position_y
is_captain
created_at
updated_at
```

### LineupPlayerRole

```text
STARTER
SUBSTITUTE
RESERVE
UNAVAILABLE
UNKNOWN
```

### Regras

- Um jogador não deve aparecer duas vezes na mesma escalação.
- Titulares devem possuir posição quando disponível.
- O capitão deve ser identificado quando possível.
- Coordenadas de campo são opcionais.
- O número da camisa pertence à participação do jogador naquela escalação.
- Jogadores indisponíveis não devem ser tratados como titulares confirmados.

---

## 25. MatchEvent

Representa um evento ocorrido durante uma partida.

### Campos principais

```text
match_event_id
match_id
team_id
player_id
secondary_player_id
event_type
period
minute
added_time
sequence_number
description
score_home_after_event
score_away_after_event
is_cancelled
is_var_reviewed
occurred_at
created_at
updated_at
```

### MatchEventType

```text
KICK_OFF
GOAL
OWN_GOAL
PENALTY_GOAL
MISSED_PENALTY
YELLOW_CARD
SECOND_YELLOW_CARD
RED_CARD
SUBSTITUTION
VAR_REVIEW
GOAL_CANCELLED
PENALTY_AWARDED
PENALTY_CANCELLED
INJURY
OFFSIDE
CORNER
FOUL
SHOT
SHOT_ON_TARGET
SAVE
HALFTIME
SECOND_HALF_START
EXTRA_TIME_START
PENALTY_SHOOTOUT_START
MATCH_END
OTHER
```

### MatchPeriod

```text
PRE_MATCH
FIRST_HALF
HALFTIME
SECOND_HALF
EXTRA_TIME_FIRST_HALF
EXTRA_TIME_HALFTIME
EXTRA_TIME_SECOND_HALF
PENALTY_SHOOTOUT
POST_MATCH
UNKNOWN
```

### Regras

- Eventos devem possuir uma ordem consistente.
- O campo `minute` pode ser nulo quando o provedor não informar.
- Acréscimos devem ser armazenados em `added_time`.
- Um gol anulado permanece registrado com `is_cancelled = true`.
- Eventos revisados pelo VAR devem ser identificados.
- Em substituições:
  - `player_id` representa o jogador que saiu;
  - `secondary_player_id` representa o jogador que entrou.
- Em gols, `secondary_player_id` pode representar o jogador que deu a
  assistência.
- Eventos não devem ser a única fonte do placar oficial.
- Eventos duplicados devem ser detectados pelo motor de fusão.
- A equipe associada ao evento deve participar da partida.
- O jogador associado deve possuir relação coerente com a equipe.

---

## 26. Injury

Representa uma lesão ou condição física relevante.

### Campos principais

```text
injury_id
player_id
team_id
injury_type
body_part
status
started_at
expected_return_at
actual_return_at
description
severity
created_at
updated_at
```

### InjuryStatus

```text
REPORTED
CONFIRMED
RECOVERING
DOUBTFUL
AVAILABLE
RETURNED
UNKNOWN
```

### InjurySeverity

```text
MINOR
MODERATE
SEVERE
UNKNOWN
```

### Regras

- Uma lesão não significa automaticamente indisponibilidade.
- O status e a previsão de retorno podem mudar.
- A mesma lesão não deve ser duplicada por vários provedores.
- Informações incertas devem ser claramente classificadas.
- O retorno real deve ser separado da previsão de retorno.
- Alterações relevantes devem preservar o histórico.

---

## 27. Suspension

Representa uma suspensão disciplinar ou administrativa.

### Campos principais

```text
suspension_id
player_id
team_id
competition_id
reason
status
start_date
end_date
matches_remaining
created_at
updated_at
```

### SuspensionStatus

```text
PENDING
ACTIVE
SERVED
CANCELLED
APPEALED
UNKNOWN
```

### Regras

- Suspensões podem valer apenas para determinada competição.
- Uma suspensão não deve tornar o jogador indisponível em todas as competições
  automaticamente.
- O número de partidas restantes pode mudar.
- Recursos e cancelamentos devem ser registrados.
- O número de partidas restantes não pode ser negativo.
- Suspensões cumpridas devem permanecer no histórico.

---

## 28. MatchAvailability

Representa a disponibilidade de um jogador para uma partida específica.

### Campos principais

```text
availability_id
match_id
player_id
team_id
availability_status
reason_type
injury_id
suspension_id
confidence
source
created_at
updated_at
```

### AvailabilityStatus

```text
AVAILABLE
EXPECTED_STARTER
EXPECTED_SUBSTITUTE
DOUBTFUL
UNAVAILABLE
SUSPENDED
INJURED
NOT_CALLED
UNKNOWN
```

### Regras

- A disponibilidade é específica de uma partida.
- Uma lesão não significa automaticamente indisponibilidade.
- Uma suspensão pode ser específica de determinada competição.
- A confiança da informação deve ser registrada.
- Previsões devem saber se utilizaram escalação provável ou confirmada.
- Um registro pode referenciar uma lesão ou suspensão relacionada.
- A equipe informada deve participar da partida.

---

## 29. TeamSeasonParticipation

Representa a participação de uma equipe em uma temporada.

### Campos principais

```text
participation_id
team_id
season_id
group_name
entry_status
final_position
points_deduction
created_at
updated_at
```

### EntryStatus

```text
CONFIRMED
QUALIFIED
INVITED
WITHDRAWN
DISQUALIFIED
UNKNOWN
```

### Regras

- Uma equipe pode participar de várias competições.
- Grupos devem ser registrados quando existirem.
- Punições de pontos devem ser representadas.
- Desclassificações não devem apagar o histórico.
- A posição final pode permanecer vazia enquanto a competição estiver ativa.
- Uma equipe não deve possuir participações duplicadas na mesma temporada e no
  mesmo contexto competitivo.

---

## 30. Relacionamentos principais

### Competition e Season

```text
Competition 1 ─── N Season
```

### Season, Stage e Round

```text
Season 1 ─── N Stage
Stage 1 ─── N Round
```

### Season e Team

```text
Season N ─── N Team
```

A relação entre temporada e equipe utiliza:

```text
TeamSeasonParticipation
```

### Match e Team

```text
Match N ─── 1 Home Team
Match N ─── 1 Away Team
```

### Team e Player

```text
Team N ─── N Player
```

A relação entre equipe e jogador utiliza:

```text
PlayerTeamMembership
```

### Team e Coach

```text
Team N ─── N Coach
```

A relação entre equipe e treinador utiliza:

```text
CoachTeamMembership
```

### Match e Lineup

```text
Match 1 ─── N Lineup
Lineup 1 ─── N LineupPlayer
```

### Match e Event

```text
Match 1 ─── N MatchEvent
```

### Player e Injury

```text
Player 1 ─── N Injury
```

### Player e Suspension

```text
Player 1 ─── N Suspension
```

---

## 31. Regras de integridade

O domínio deverá impedir ou sinalizar:

- partida com a mesma equipe como mandante e visitante;
- jogador duplicado na mesma escalação;
- temporada sem competição;
- fase sem temporada;
- rodada sem fase;
- partida sem temporada;
- escalação vinculada a equipe que não participa da partida;
- evento associado a equipe que não participa da partida;
- evento associado a jogador incompatível com a equipe;
- placar negativo;
- data final anterior à data inicial;
- suspensão com número negativo de partidas;
- capacidade negativa de estádio;
- jogador com altura ou peso fisicamente impossíveis;
- partidas duplicadas;
- vínculos temporais contraditórios;
- aliases vazios;
- identificadores externos sem provedor.

Algumas inconsistências poderão ser bloqueadas imediatamente.

Outras poderão ser encaminhadas para revisão ou quarentena.

---

## 32. Dados observados e derivados

### Dados observados

Exemplos:

```text
placar
eventos
escalação
cartões
substituições
estádio
árbitro
lesões informadas
suspensões
horário da partida
```

### Dados derivados

Exemplos:

```text
forma recente
força ofensiva
força defensiva
impacto de ausência
força do calendário
médias ponderadas
tendências
índice disciplinar
desempenho por treinador
```

Dados derivados pertencem ao contexto `Statistics`, e não ao contexto
`Football`.

O contexto `Football` deve armazenar fatos esportivos observados ou
consolidados.

---

## 33. Histórico

As seguintes informações devem preservar histórico:

- nomes de equipes;
- escudos;
- vínculos de jogadores;
- vínculos de treinadores;
- estádios utilizados;
- horários de partidas;
- escalações previstas;
- escalações confirmadas;
- lesões;
- suspensões;
- estados de partidas;
- mudanças de competição;
- mudanças de fase e rodada.

Informações históricas importantes não devem ser sobrescritas silenciosamente.

Quando aplicável, devem ser utilizados:

```text
valid_from
valid_until
created_at
updated_at
```

Também poderão ser utilizadas tabelas específicas de histórico.

---

## 34. Fora do escopo deste documento

Este documento não define:

- estatísticas derivadas detalhadas;
- mercados de apostas;
- odds;
- probabilidades;
- recomendações;
- níveis de risco;
- gestão de banca;
- notificações;
- usuários;
- modelos preditivos;
- backtesting;
- simulações de estratégias.

Esses conceitos serão definidos em documentos específicos das próximas etapas.