# UltraStats AI — Modelo Canônico do Domínio

## 1. Objetivo

Este documento define o modelo canônico do UltraStats AI.

O modelo canônico representa as entidades internas e oficiais utilizadas pelo
sistema, independentemente do formato ou dos identificadores fornecidos por APIs
externas.

Os dados recebidos de providers deverão passar pelas etapas de:

```text
coleta
    ↓
armazenamento do payload bruto
    ↓
validação
    ↓
normalização
    ↓
resolução de identidade
    ↓
fusão de dados
    ↓
persistência no modelo canônico
```

Nenhum payload externo deverá ser persistido diretamente nas entidades
canônicas sem passar por esse processo.

---

## 2. Princípios do modelo canônico

O modelo canônico deverá seguir estes princípios:

- independência de providers;
- identidade interna estável;
- uso de UUID;
- preservação de histórico;
- rastreabilidade da origem dos dados;
- auditoria de alterações;
- integridade referencial;
- suporte a múltiplos providers;
- suporte a dados incompletos;
- suporte a conflitos entre fontes;
- separação entre fatos observados e previsões;
- separação entre dados pré-jogo e dados ao vivo;
- inativação lógica quando aplicável;
- datas e horários armazenados em UTC.

---

## 3. Identificadores internos

Todas as entidades canônicas deverão utilizar identificadores internos.

Exemplo:

```text
team_id = UUID
player_id = UUID
match_id = UUID
competition_id = UUID
```

Identificadores recebidos de APIs externas não deverão ser utilizados como
chaves primárias do domínio.

Os identificadores externos serão relacionados às entidades canônicas por meio
de estruturas específicas de mapeamento.

Documento relacionado:

- [`provider-identity-mappings.md`](provider-identity-mappings.md)

---

## 4. Organização do domínio

O modelo será dividido nos seguintes grupos:

```text
Identidade e localização
Competições e temporadas
Participantes do futebol
Partidas
Escalações e formações
Eventos e estatísticas
Disponibilidade de jogadores
Apostas e odds
Predições e recomendações
Auditoria e rastreabilidade
```
---

## 5. Identidade e localização

As entidades deste grupo representam a base geográfica do domínio.

Elas deverão ser independentes dos identificadores fornecidos por providers e
permitirão relacionamentos consistentes entre competições, equipes, estádios e
partidas.

As entidades previstas são:

```text
Country
City
Stadium
```

Responsabilidades gerais:

- representar países;
- representar cidades;
- representar estádios;
- armazenar localização geográfica;
- permitir vínculos entre entidades;
- preservar consistência dos dados;
- servir como referência para todo o restante do domínio.

---

### 5.1 Country

A entidade `Country` representa um país dentro do modelo canônico.

Ela será utilizada como referência para competições, equipes, jogadores,
treinadores, árbitros, cidades e estádios.

#### Campos principais

```text
id
name
official_name
common_name
iso_alpha_2
iso_alpha_3
fifa_code
continent
flag_url
is_active
created_at
updated_at
```

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|--------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno da entidade. |
| `name` | string | Sim | Nome principal utilizado pelo sistema. |
| `official_name` | string | Não | Nome oficial completo do país. |
| `common_name` | string | Não | Nome popular ou abreviado. |
| `iso_alpha_2` | string | Não | Código ISO Alpha-2. |
| `iso_alpha_3` | string | Não | Código ISO Alpha-3. |
| `fifa_code` | string | Não | Código utilizado pela FIFA. |
| `continent` | enum | Não | Continente ao qual pertence. |
| `flag_url` | string | Não | URL opcional da bandeira. |
| `is_active` | boolean | Sim | Indica se o registro está ativo. |
| `created_at` | datetime UTC | Sim | Data de criação. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |


#### Continentes previstos

```text
AFRICA
ASIA
EUROPE
NORTH_AMERICA
SOUTH_AMERICA
OCEANIA
ANTARCTICA
UNKNOWN
```

O valor `UNKNOWN` deverá ser utilizado somente quando o continente ainda não
puder ser determinado com segurança.

#### Regras de integridade

- `name` não poderá ser vazio;
- `iso_alpha_2`, quando informado, deverá possuir dois caracteres;
- `iso_alpha_3`, quando informado, deverá possuir três caracteres;
- `fifa_code`, quando informado, deverá possuir três caracteres;
- os códigos deverão ser armazenados em letras maiúsculas;
- `iso_alpha_2` deverá ser único quando informado;
- `iso_alpha_3` deverá ser único quando informado;
- `fifa_code` deverá ser único quando informado;
- países históricos ou extintos poderão permanecer inativos;
- um país não deverá ser removido fisicamente enquanto possuir vínculos.

---

### 5.2 City

A entidade `City` representa uma cidade dentro do modelo canônico.

Cada cidade deverá estar vinculada a um país e poderá ser utilizada por equipes
e estádios.

#### Campos principais

```text
id
country_id
name
official_name
state_region
latitude
longitude
timezone
is_active
created_at
updated_at
```

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|--------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno da entidade. |
| `country_id` | UUID | Sim | País ao qual a cidade pertence. |
| `name` | string | Sim | Nome principal da cidade. |
| `official_name` | string | Não | Nome oficial ou completo. |
| `state_region` | string | Não | Estado, província ou região administrativa. |
| `latitude` | decimal | Não | Latitude geográfica da cidade. |
| `longitude` | decimal | Não | Longitude geográfica da cidade. |
| `timezone` | string | Não | Fuso horário no padrão IANA. |
| `is_active` | boolean | Sim | Indica se o registro está ativo. |
| `created_at` | datetime UTC | Sim | Data de criação. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Relacionamentos

```text
Country 1 ─── N City
City    1 ─── N Stadium
City    1 ─── N Team
```

#### Regras de integridade

- `country_id` deverá referenciar um país existente;
- `name` não poderá ser vazio;
- `latitude`, quando informada, deverá estar entre `-90` e `90`;
- `longitude`, quando informada, deverá estar entre `-180` e `180`;
- `timezone`, quando informado, deverá utilizar preferencialmente o padrão IANA;
- cidades com nomes iguais poderão existir em países diferentes;
- cidades com nomes iguais poderão existir no mesmo país quando estiverem em
  regiões administrativas diferentes;
- uma cidade não deverá ser removida fisicamente enquanto possuir vínculos.

#### Regra inicial de unicidade

A unicidade de uma cidade não deverá depender apenas de seu nome.

Uma combinação candidata para identificação é:

```text
country_id
normalized_name
normalized_state_region
```

O comportamento definitivo será definido durante a implementação do modelo
persistente.

---

### 5.3 Stadium

A entidade `Stadium` representa um estádio ou local esportivo dentro do modelo
canônico.

Um estádio poderá estar vinculado a uma cidade e a um país.

O vínculo direto com o país será útil quando a cidade ainda não estiver
disponível ou quando o provider fornecer apenas a informação do país.

#### Campos principais

```text
id
country_id
city_id
name
official_name
short_name
address
latitude
longitude
capacity
surface_type
opened_year
timezone
is_active
created_at
updated_at
```

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|--------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno da entidade. |
| `country_id` | UUID | Não | País onde o estádio está localizado. |
| `city_id` | UUID | Não | Cidade onde o estádio está localizado. |
| `name` | string | Sim | Nome principal do estádio. |
| `official_name` | string | Não | Nome oficial completo. |
| `short_name` | string | Não | Nome abreviado ou popular. |
| `address` | string | Não | Endereço textual do estádio. |
| `latitude` | decimal | Não | Latitude geográfica do estádio. |
| `longitude` | decimal | Não | Longitude geográfica do estádio. |
| `capacity` | integer | Não | Capacidade máxima de público. |
| `surface_type` | enum | Não | Tipo de superfície do campo. |
| `opened_year` | integer | Não | Ano de inauguração. |
| `timezone` | string | Não | Fuso horário no padrão IANA. |
| `is_active` | boolean | Sim | Indica se o estádio está ativo. |
| `created_at` | datetime UTC | Sim | Data de criação. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |


#### Tipos de superfície previstos

```text
NATURAL_GRASS
ARTIFICIAL_GRASS
HYBRID_GRASS
DIRT
INDOOR
UNKNOWN
```

O valor `UNKNOWN` deverá ser utilizado somente quando o tipo de superfície ainda
não puder ser identificado com segurança.

#### Relacionamentos

```text
Country 1 ─── N Stadium
City    1 ─── N Stadium
Stadium 1 ─── N Match
Stadium 1 ─── N TeamStadiumAssignment
```

#### Regras de integridade

- `name` não poderá ser vazio;
- `capacity`, quando informada, deverá ser maior que zero;
- `latitude`, quando informada, deverá estar entre `-90` e `90`;
- `longitude`, quando informada, deverá estar entre `-180` e `180`;
- `opened_year`, quando informado, deverá ser coerente;
- `city_id`, quando informado, deverá referenciar uma cidade existente;
- `country_id`, quando informado, deverá referenciar um país existente;
- quando `city_id` e `country_id` forem informados, o país do estádio deverá
  corresponder ao país da cidade;
- o estádio não deverá ser identificado apenas pelo nome;
- estádios com nomes semelhantes deverão considerar cidade, país e coordenadas;
- um estádio não deverá ser removido fisicamente enquanto possuir partidas ou
  vínculos históricos.
  
---

### 5.4 Histórico de nomes e propriedades

Nomes de países, cidades e estádios podem mudar ao longo do tempo.

Na primeira versão do modelo, os dados atuais poderão permanecer diretamente nas
entidades principais.

Caso seja necessário preservar alterações históricas, poderão ser introduzidas
entidades específicas, como:

```text
CountryNameHistory
CityNameHistory
StadiumNameHistory
StadiumCapacityHistory
```

Essas entidades permitirão registrar alterações sem sobrescrever informações
anteriores.

Mudanças relevantes deverão ser preservadas sempre que impactarem análises
históricas, auditorias ou rastreabilidade.

A implementação dessas entidades será definida durante a modelagem persistente,
quando houver requisitos concretos para seu uso.

---

### 5.5 Resolução de identidade geográfica

A resolução de identidade tem como objetivo garantir que países, cidades e
estádios provenientes de diferentes providers sejam associados à mesma entidade
canônica sempre que representarem o mesmo objeto do mundo real.

A criação de novas entidades deverá ocorrer somente quando houver evidências de
que realmente se trata de um novo registro.

#### Critérios para Country

A identificação poderá considerar:

```text
ISO Alpha-2
ISO Alpha-3
Código FIFA
Nome normalizado
Aliases conhecidos
```

#### Critérios para City

A identificação poderá considerar:

```text
País
Nome normalizado
Estado ou região
Coordenadas geográficas
Aliases conhecidos
```

#### Critérios para Stadium

A identificação poderá considerar:

```text
Nome normalizado
Cidade
País
Endereço
Coordenadas
Capacidade aproximada
Equipe mandante
Aliases conhecidos
```

#### Exemplos

Os registros abaixo poderão representar o mesmo estádio:

```text
Estádio do Morumbi
Morumbi
Morumbi Stadium
Estádio Cícero Pompeu de Toledo
```

Da mesma forma, pequenas diferenças de escrita em nomes de cidades ou países não
deverão resultar automaticamente na criação de novos registros.

#### Diretrizes

- a comparação não deverá depender apenas do nome textual;
- diferentes providers poderão utilizar nomes distintos para a mesma entidade;
- aliases deverão ser preservados sempre que possível;
- conflitos deverão ser registrados para análise;
- decisões automáticas deverão ser rastreáveis;
- quando necessário, a associação poderá ser revisada manualmente.

---

### 5.6 Dependências futuras

As entidades deste grupo servirão de base para diversas entidades do domínio,
incluindo:

```text
Competition
Team
Player
Coach
Referee
Match
TeamStadiumAssignment
```

Essas dependências deverão utilizar sempre os identificadores internos do modelo
canônico, nunca os identificadores fornecidos por providers externos.

---

### 5.7 Índices recomendados

Durante a implementação do banco de dados, recomenda-se criar índices para os
campos mais utilizados em consultas e resolução de identidade.

Índices iniciais sugeridos:

```text
Country.iso_alpha_2
Country.iso_alpha_3
Country.fifa_code

City.country_id
City.name

Stadium.country_id
Stadium.city_id
Stadium.name
```

A estratégia definitiva de indexação deverá considerar o volume de dados e o
perfil das consultas realizadas pela aplicação.

---

### 5.8 Observações de implementação

Durante a implementação das entidades persistentes deverão ser observadas as
seguintes diretrizes:

- utilizar UUID como chave primária;
- preservar integridade referencial;
- evitar exclusão física de registros relacionados;
- armazenar datas e horários em UTC;
- manter compatibilidade com múltiplos providers;
- preservar rastreabilidade da origem dos dados;
- permitir futura expansão sem alterações incompatíveis no modelo.

---

## 6. Competições e temporadas

Entidades previstas:

```text
Competition
Season
Stage
Round
```

Responsabilidades principais:

- representar competições;
- representar temporadas;
- representar fases;
- representar rodadas;
- organizar partidas dentro de um contexto esportivo.

---

## 7. Participantes do futebol

Entidades previstas:

```text
Team
Player
Coach
Referee
```

Entidades históricas previstas:

```text
PlayerTeamMembership
CoachTeamMembership
TeamStadiumAssignment
```

Responsabilidades principais:

- representar participantes canônicos;
- preservar vínculos históricos;
- evitar sobrescrita de relações antigas;
- permitir análise temporal.

---

## 8. Partidas

Entidades previstas:

```text
Match
MatchScheduleHistory
MatchStatusHistory
```

Responsabilidades principais:

- representar uma partida canônica;
- preservar alterações de data e horário;
- preservar alterações de estado;
- registrar placares;
- representar o ciclo de vida da partida.

Documento relacionado:

- [`match-lifecycle.md`](match-lifecycle.md)

---

## 9. Escalações e formações

Entidades previstas:

```text
Formation
Lineup
LineupPlayer
```

Responsabilidades principais:

- representar formações táticas;
- representar escalações previstas;
- representar escalações confirmadas;
- representar titulares;
- representar reservas;
- representar posições;
- preservar alterações de última hora.

Escalações previstas e confirmadas deverão ser registros independentes.

---

## 10. Eventos e estatísticas

Entidades previstas:

```text
MatchEvent
MatchStatistics
TeamMatchStatistics
PlayerMatchStatistics
```

Responsabilidades principais:

- registrar eventos da partida;
- registrar gols;
- registrar cartões;
- registrar substituições;
- registrar estatísticas por equipe;
- registrar estatísticas por jogador;
- preservar o momento do evento;
- permitir reconstrução da linha do tempo.

---

## 11. Disponibilidade de jogadores

Entidades previstas:

```text
Injury
Suspension
PlayerAvailability
```

Responsabilidades principais:

- registrar lesões;
- registrar suspensões;
- registrar dúvidas;
- registrar indisponibilidade;
- registrar previsão de retorno;
- registrar impacto estimado da ausência.

---

## 12. Apostas e odds

Entidades previstas:

```text
Bookmaker
MarketDefinition
MarketLine
MarketSelection
Odd
OddHistory
```

Responsabilidades principais:

- representar casas de apostas;
- representar mercados;
- representar linhas;
- representar seleções;
- armazenar odds;
- preservar histórico de alterações;
- permitir comparação entre bookmakers.

O modelo de mercados deverá ser flexível e não depender de uma classe diferente
para cada mercado de aposta.

---

## 13. Predições e recomendações

Entidades previstas:

```text
ModelVersion
Prediction
PredictionProbability
BetRecommendation
RecommendationExplanation
```

Responsabilidades principais:

- preservar previsões;
- registrar versão do modelo;
- registrar probabilidades;
- registrar odd justa;
- registrar valor esperado;
- registrar confiança;
- registrar risco;
- explicar recomendações;
- preservar o estado dos dados utilizados.

Previsões não deverão ser alteradas silenciosamente depois de produzidas.

---

## 14. Auditoria e rastreabilidade

Entidades previstas:

```text
RawProviderPayload
ProviderEntityMapping
DataConflict
DataQuarantine
AuditLog
```

Responsabilidades principais:

- preservar payloads brutos;
- relacionar IDs externos e internos;
- registrar conflitos;
- colocar dados incertos em quarentena;
- permitir reprocessamento;
- auditar decisões automáticas e manuais.

---

## 15. Tipos de dados comuns

Os seguintes tipos serão utilizados frequentemente:

```text
UUID
string
integer
decimal
boolean
date
datetime UTC
enum
JSON
```

Valores financeiros, probabilidades e odds deverão utilizar tipos decimais
adequados.

Valores monetários e probabilidades não deverão depender de números de ponto
flutuante sem controle de precisão.

---

## 16. Campos comuns

Quando aplicável, as entidades deverão possuir campos semelhantes a:

```text
id
created_at
updated_at
is_active
```

Entidades auditáveis poderão possuir:

```text
created_by
updated_by
source
raw_payload_reference
```

A inclusão desses campos dependerá da responsabilidade de cada entidade.

Eles não deverão ser adicionados automaticamente sem necessidade.

---

## 17. Datas e horários

Todas as datas e horários operacionais deverão ser armazenados em UTC.

Quando necessário, também deverão ser preservados:

```text
timezone original
horário original informado pelo provider
data e horário da coleta
data e horário da atualização
```

A interface poderá converter UTC para o fuso horário do usuário.

---

## 18. Histórico

Informações históricas relevantes não deverão ser sobrescritas.

Exemplos:

```text
mudança de equipe de um jogador
mudança de treinador
mudança de estádio
alteração de horário de partida
alteração de estado da partida
movimento de odds
mudança de disponibilidade de jogador
```

Essas alterações deverão possuir entidades históricas ou registros de auditoria.

---

## 19. Dados observados e dados estimados

O modelo deverá distinguir:

```text
fato observado
informação estimada
previsão
recomendação
```

Exemplo:

```text
escalação provável = informação estimada
escalação confirmada = fato observado
probabilidade do modelo = previsão
sugestão de aposta = recomendação
```

Esses conceitos não deverão ser armazenados como se fossem equivalentes.

---

## 20. Estado deste documento

Este documento define a estrutura inicial do modelo canônico.

As próximas etapas detalharão:

```text
entidades de identidade e localização
competições e temporadas
equipes e participantes
partidas
escalações
eventos e estatísticas
lesões e suspensões
mercados e odds
predições e recomendações
auditoria e rastreabilidade
relacionamentos
regras de integridade
```

Nenhuma implementação SQLAlchemy deverá ser iniciada antes da definição das
entidades e relacionamentos essenciais.