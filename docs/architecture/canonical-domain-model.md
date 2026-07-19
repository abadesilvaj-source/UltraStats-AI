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

As entidades deste grupo organizam toda a estrutura competitiva do futebol.

Elas definem onde uma partida acontece, em qual temporada, fase e rodada,
permitindo que análises históricas e estatísticas sejam realizadas de forma
consistente.

As entidades previstas são:

```text
Competition
Season
Stage
Round
```

Responsabilidades gerais:

- representar competições nacionais e internacionais;
- representar temporadas esportivas;
- representar fases da competição;
- representar rodadas;
- organizar partidas dentro de um contexto esportivo;
- preservar a estrutura histórica das competições;
- permitir diferentes formatos de torneio.

---

### 6.1 Competition

A entidade `Competition` representa uma competição oficial ou reconhecida dentro
do modelo canônico.

Ela poderá representar campeonatos de liga, copas, torneios internacionais,
competições continentais e outros formatos competitivos do futebol.

#### Campos principais

```text
id
country_id
name
official_name
short_name
competition_type
gender
scope
organizer
logo_url
is_active
created_at
updated_at
```

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|--------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno da entidade. |
| `country_id` | UUID | Não | País principal relacionado à competição. |
| `name` | string | Sim | Nome principal utilizado pelo sistema. |
| `official_name` | string | Não | Nome oficial completo da competição. |
| `short_name` | string | Não | Nome abreviado ou popular. |
| `competition_type` | enum | Sim | Formato principal da competição. |
| `gender` | enum | Sim | Categoria de gênero da competição. |
| `scope` | enum | Sim | Abrangência geográfica da competição. |
| `organizer` | string | Não | Entidade responsável pela organização. |
| `logo_url` | string | Não | URL opcional do logotipo. |
| `is_active` | boolean | Sim | Indica se a competição está ativa. |
| `created_at` | datetime UTC | Sim | Data de criação. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Tipos de competição previstos

```text
LEAGUE
CUP
SUPER_CUP
FRIENDLY
QUALIFIER
PLAYOFF
TOURNAMENT
YOUTH
OTHER
UNKNOWN
```

#### Escopos previstos

```text
DOMESTIC
CONTINENTAL
INTERNATIONAL
REGIONAL
WORLDWIDE
UNKNOWN
```

#### Categorias de gênero

```text
MEN
WOMEN
MIXED
UNKNOWN
```

#### Regras de integridade

- `name` não poderá ser vazio;
- `competition_type` deverá possuir um valor válido;
- `scope` deverá possuir um valor válido;
- `gender` deverá possuir um valor válido;
- competições diferentes poderão possuir o mesmo nome quando pertencerem a
  países distintos;
- competições históricas poderão permanecer inativas;
- uma competição não deverá ser removida fisicamente enquanto possuir
  temporadas associadas.

#### Relacionamentos

```text
Country     1 ─── N Competition
Competition 1 ─── N Season
```

O relacionamento com `Country` poderá ser opcional para competições
continentais, internacionais ou mundiais.

#### Regra inicial de unicidade

A unicidade de uma competição não deverá depender apenas de seu nome.

Uma combinação candidata para identificação é:

```text
country_id
normalized_name
competition_type
gender
scope
```

Para competições sem país principal, a identificação poderá considerar também:

```text
organizer
scope
normalized_name
```

#### Diretrizes de resolução de identidade

- nomes abreviados e oficiais poderão representar a mesma competição;
- diferenças de idioma não deverão criar automaticamente uma nova entidade;
- o país deverá ser considerado em competições nacionais;
- o organizador deverá ser considerado em competições internacionais;
- o gênero deverá participar da identificação;
- o tipo e o escopo deverão ser considerados;
- aliases e identificadores externos deverão ser preservados nos mapeamentos de
  providers;
- conflitos de associação deverão ser registrados para revisão.

---

### 6.2 Season

A entidade `Season` representa uma temporada específica de uma competição.

Ela deverá preservar o contexto temporal da competição, permitindo distinguir
edições diferentes de um mesmo campeonato.

Exemplos:

```text
Brasileirão 2025
Premier League 2025/2026
UEFA Champions League 2026/2027
Copa do Brasil 2026
```

#### Campos principais

```text
id
competition_id
name
start_date
end_date
is_current
status
logo_url
is_active
created_at
updated_at
```

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|--------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno da entidade. |
| `competition_id` | UUID | Sim | Competição à qual a temporada pertence. |
| `name` | string | Sim | Nome da temporada, como `2025` ou `2025/2026`. |
| `start_date` | date | Não | Data oficial de início. |
| `end_date` | date | Não | Data oficial de encerramento. |
| `is_current` | boolean | Sim | Indica se é a temporada atual da competição. |
| `status` | enum | Sim | Estado atual da temporada. |
| `logo_url` | string | Não | URL opcional de identidade visual específica. |
| `is_active` | boolean | Sim | Indica se o registro está ativo. |
| `created_at` | datetime UTC | Sim | Data de criação. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Status previstos

```text
PLANNED
ACTIVE
PAUSED
COMPLETED
CANCELLED
UNKNOWN
```

O valor `UNKNOWN` deverá ser utilizado somente quando o estado da temporada
ainda não puder ser determinado com segurança.

#### Relacionamentos

```text
Competition 1 ─── N Season
Season      1 ─── N Stage
Season      1 ─── N Round
Season      1 ─── N Match
```

#### Regras de integridade

- `competition_id` deverá referenciar uma competição existente;
- `name` não poderá ser vazio;
- `start_date`, quando informada, deverá ser anterior ou igual a `end_date`;
- apenas uma temporada por competição deverá possuir `is_current = true`;
- uma temporada concluída poderá permanecer ativa para consultas históricas;
- temporadas canceladas não deverão ser removidas fisicamente;
- uma temporada não deverá ser removida enquanto possuir fases, rodadas ou
  partidas associadas.

#### Regra inicial de unicidade

A unicidade de uma temporada deverá considerar a competição e o nome da edição.

Uma combinação candidata é:

```text
competition_id
normalized_name
```

Quando as datas estiverem disponíveis, elas poderão ser utilizadas como critério
adicional de validação.

---

### 6.3 Stage

A entidade `Stage` representa uma fase específica dentro de uma temporada.

Ela será utilizada quando a competição possuir divisões internas, como fase de
grupos, mata-mata, quartas de final, semifinal ou final.

Exemplos:

```text
Fase de grupos
Oitavas de final
Quartas de final
Semifinal
Final
```

#### Campos principais

```text
id
season_id
name
stage_type
sequence
start_date
end_date
is_active
created_at
updated_at
```

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|--------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno da entidade. |
| `season_id` | UUID | Sim | Temporada à qual a fase pertence. |
| `name` | string | Sim | Nome principal da fase. |
| `stage_type` | enum | Sim | Tipo estrutural da fase. |
| `sequence` | integer | Não | Ordem da fase dentro da temporada. |
| `start_date` | date | Não | Data de início da fase. |
| `end_date` | date | Não | Data de encerramento da fase. |
| `is_active` | boolean | Sim | Indica se o registro está ativo. |
| `created_at` | datetime UTC | Sim | Data de criação. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Tipos de fase previstos

```text
REGULAR_SEASON
GROUP_STAGE
QUALIFICATION
PLAYOFF
ROUND_OF_32
ROUND_OF_16
QUARTER_FINAL
SEMI_FINAL
THIRD_PLACE
FINAL
RELEGATION
PLAY_IN
OTHER
UNKNOWN
```

#### Relacionamentos

```text
Season 1 ─── N Stage
Stage  1 ─── N Round
Stage  1 ─── N Match
```

Uma temporada poderá possuir apenas uma fase ou diversas fases, dependendo do
formato da competição.

#### Regras de integridade

- `season_id` deverá referenciar uma temporada existente;
- `name` não poderá ser vazio;
- `stage_type` deverá possuir um valor válido;
- `sequence`, quando informada, deverá ser maior que zero;
- `start_date`, quando informada, deverá ser anterior ou igual a `end_date`;
- fases poderão existir mesmo quando a competição possuir apenas uma etapa;
- uma fase não deverá ser removida enquanto possuir rodadas ou partidas
  associadas.

#### Regra inicial de unicidade

Dentro de uma mesma temporada, duas fases não deverão compartilhar o mesmo nome.

Uma combinação candidata é:

```text
season_id
normalized_name
```

Quando existir, `sequence` poderá ser utilizada como critério complementar de
ordenação e validação.

---

### 6.4 Round

A entidade `Round` representa uma rodada, jornada ou etapa numerada dentro de uma
temporada ou fase.

Ela poderá ser utilizada tanto em competições de pontos corridos quanto em fases
eliminatórias.

Exemplos:

```text
Rodada 1
Rodada 15
Jornada 8
Oitavas de final — ida
Oitavas de final — volta
```

#### Campos principais

```text
id
season_id
stage_id
name
round_number
sequence
start_date
end_date
is_current
is_active
created_at
updated_at
```

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|--------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno da entidade. |
| `season_id` | UUID | Sim | Temporada à qual a rodada pertence. |
| `stage_id` | UUID | Não | Fase específica à qual a rodada pertence. |
| `name` | string | Sim | Nome principal da rodada. |
| `round_number` | integer | Não | Número oficial da rodada, quando aplicável. |
| `sequence` | integer | Não | Ordem interna da rodada na competição. |
| `start_date` | date | Não | Data de início da rodada. |
| `end_date` | date | Não | Data de encerramento da rodada. |
| `is_current` | boolean | Sim | Indica se a rodada é a atual. |
| `is_active` | boolean | Sim | Indica se o registro está ativo. |
| `created_at` | datetime UTC | Sim | Data de criação. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Relacionamentos

```text
Season 1 ─── N Round
Stage  1 ─── N Round
Round  1 ─── N Match
```

O relacionamento com `Stage` será opcional, pois algumas competições poderão
organizar suas rodadas diretamente dentro da temporada.

#### Regras de integridade

- `season_id` deverá referenciar uma temporada existente;
- `stage_id`, quando informado, deverá referenciar uma fase da mesma temporada;
- `name` não poderá ser vazio;
- `round_number`, quando informado, deverá ser maior que zero;
- `sequence`, quando informada, deverá ser maior que zero;
- `start_date`, quando informada, deverá ser anterior ou igual a `end_date`;
- apenas uma rodada por contexto competitivo deverá possuir
  `is_current = true`;
- uma rodada não deverá ser removida enquanto possuir partidas associadas.

#### Regra inicial de unicidade

A unicidade de uma rodada deverá considerar sua temporada e sua fase, quando
existente.

Uma combinação candidata é:

```text
season_id
stage_id
normalized_name
```

Quando `stage_id` for nulo, a unicidade deverá ser avaliada diretamente dentro
da temporada.

Quando o provider informar um número oficial de rodada, a combinação abaixo
também poderá ser utilizada para validação:

```text
season_id
stage_id
round_number
```
---

### 6.5 Observações gerais do domínio competitivo

As entidades `Competition`, `Season`, `Stage` e `Round` representam níveis
diferentes da organização esportiva e não deverão ser tratadas como
equivalentes.

A hierarquia preferencial será:

    Competition
    └── Season
        ├── Stage
        │   └── Round
        └── Round

Uma rodada poderá estar vinculada diretamente à temporada quando a competição
não utilizar fases explícitas.

#### Regras de consistência hierárquica

- uma `Season` deverá pertencer a uma única `Competition`;
- uma `Stage` deverá pertencer a uma única `Season`;
- uma `Round` deverá pertencer a uma única `Season`;
- quando uma `Round` possuir `stage_id`, a fase deverá pertencer à mesma
  temporada indicada em `season_id`;
- partidas associadas a uma fase ou rodada deverão respeitar a mesma
  hierarquia;
- dados incompletos recebidos de providers não deverão criar estruturas
  artificiais sem necessidade;
- estruturas inferidas deverão registrar sua origem e nível de confiança.

#### Tratamento de estruturas simplificadas

Alguns providers poderão fornecer apenas competição, temporada e rodada.

Nesses casos:

    Competition
    └── Season
        └── Round

A ausência de `Stage` será válida e não deverá ser considerada erro.

Outros providers poderão fornecer competição, temporada e fase, mas não uma
rodada explícita.

Nesses casos:

    Competition
    └── Season
        └── Stage

A ausência de `Round` também será válida.

#### Diretrizes de normalização

- nomes deverão ser preservados no idioma original recebido;
- versões normalizadas poderão ser utilizadas para comparação;
- nomes traduzidos deverão ser armazenados separadamente;
- números de rodada não deverão ser extraídos sem validação;
- datas poderão auxiliar na ordenação, mas não deverão substituir a
  identidade;
- aliases de competição, temporada, fase e rodada deverão ser preservados;
- identificadores externos deverão permanecer vinculados ao provider de
  origem.
---

### 6.6 Índices recomendados

Os índices desta seção representam uma estratégia inicial para PostgreSQL.

A implementação definitiva deverá considerar:

- volume real de dados;
- frequência das consultas;
- cardinalidade das colunas;
- planos de execução;
- custo de escrita;
- retenção histórica;
- sincronização com múltiplos providers.

Índices não deverão ser criados apenas por precaução. Cada índice deverá possuir
uma finalidade clara e ser validado com consultas reais do sistema.

#### Índices de Competition

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_competition_country_id` | `country_id` | Buscar competições de um país. |
| `ix_competition_normalized_name` | `normalized_name` | Localizar competições por nome normalizado. |
| `ix_competition_type` | `competition_type` | Filtrar competições por tipo. |
| `ix_competition_scope` | `scope` | Filtrar competições por escopo. |
| `ix_competition_gender` | `gender` | Filtrar competições por categoria de gênero. |
| `ix_competition_is_active` | `is_active` | Consultar competições ativas ou históricas. |
| `ix_competition_country_active` | `country_id, is_active` | Consultar competições ativas de um país. |
| `ix_competition_scope_active` | `scope, is_active` | Consultar competições ativas por escopo. |

Uma restrição ou índice de unicidade candidato poderá utilizar:

    country_id
    normalized_name
    competition_type
    gender
    scope

Entretanto, a presença de valores nulos deverá ser analisada antes da criação da
restrição física.

Competições internacionais, continentais ou mundiais poderão não possuir
`country_id`.

Nesses casos, a unicidade poderá utilizar uma estratégia complementar baseada
em:

    organizer
    normalized_name
    competition_type
    gender
    scope

A restrição definitiva não deverá impedir o armazenamento de competições
legítimas que compartilhem nomes semelhantes.

#### Índices de Season

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_season_competition_id` | `competition_id` | Buscar temporadas de uma competição. |
| `ix_season_status` | `status` | Filtrar temporadas pelo estado atual. |
| `ix_season_start_date` | `start_date` | Ordenar ou filtrar pelo início. |
| `ix_season_end_date` | `end_date` | Ordenar ou filtrar pelo encerramento. |
| `ix_season_is_current` | `is_current` | Localizar temporadas atuais. |
| `ix_season_is_active` | `is_active` | Separar registros ativos e históricos. |
| `ix_season_competition_status` | `competition_id, status` | Buscar temporadas de uma competição por status. |
| `ix_season_competition_dates` | `competition_id, start_date, end_date` | Consultar temporadas por intervalo temporal. |

A combinação inicial de unicidade será:

    competition_id
    normalized_name

Para garantir que apenas uma temporada atual exista por competição, poderá ser
utilizado um índice único parcial no PostgreSQL.

Exemplo conceitual:

    UNIQUE (competition_id)
    WHERE is_current = true

Essa restrição física deverá ser aplicada apenas depois que os dados existentes
forem validados.

#### Índices de Stage

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_stage_season_id` | `season_id` | Buscar fases de uma temporada. |
| `ix_stage_type` | `stage_type` | Filtrar fases por tipo. |
| `ix_stage_sequence` | `sequence` | Ordenar fases pela sequência. |
| `ix_stage_start_date` | `start_date` | Consultar fases pelo início. |
| `ix_stage_end_date` | `end_date` | Consultar fases pelo encerramento. |
| `ix_stage_is_active` | `is_active` | Separar fases ativas e históricas. |
| `ix_stage_season_sequence` | `season_id, sequence` | Ordenar as fases de uma temporada. |
| `ix_stage_season_type` | `season_id, stage_type` | Consultar fases por temporada e tipo. |

A combinação inicial de unicidade será:

    season_id
    normalized_name

Quando o provider fornecer uma sequência confiável, a combinação abaixo também
poderá ser validada:

    season_id
    sequence

A sequência não deverá substituir o nome como identidade principal, pois alguns
providers poderão apresentar ordenações diferentes.

#### Índices de Round

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_round_season_id` | `season_id` | Buscar rodadas de uma temporada. |
| `ix_round_stage_id` | `stage_id` | Buscar rodadas de uma fase. |
| `ix_round_number` | `round_number` | Filtrar pelo número oficial. |
| `ix_round_sequence` | `sequence` | Ordenar rodadas internamente. |
| `ix_round_start_date` | `start_date` | Consultar rodadas pelo início. |
| `ix_round_end_date` | `end_date` | Consultar rodadas pelo encerramento. |
| `ix_round_is_current` | `is_current` | Localizar a rodada atual. |
| `ix_round_is_active` | `is_active` | Separar rodadas ativas e históricas. |
| `ix_round_season_stage` | `season_id, stage_id` | Consultar rodadas por temporada e fase. |
| `ix_round_season_sequence` | `season_id, sequence` | Ordenar rodadas de uma temporada. |
| `ix_round_stage_sequence` | `stage_id, sequence` | Ordenar rodadas de uma fase. |
| `ix_round_season_number` | `season_id, round_number` | Buscar rodada numerada na temporada. |

A combinação inicial de unicidade será:

    season_id
    stage_id
    normalized_name

Quando o número oficial estiver disponível, também poderá ser considerada:

    season_id
    stage_id
    round_number

Como `stage_id` poderá ser nulo, a implementação da unicidade deverá tratar
separadamente os seguintes contextos:

- rodadas vinculadas diretamente à temporada;
- rodadas vinculadas a uma fase específica.

Para rodadas sem fase, poderá existir uma restrição parcial equivalente a:

    UNIQUE (
        season_id,
        normalized_name
    )
    WHERE stage_id IS NULL

Para rodadas com fase, poderá existir uma restrição equivalente a:

    UNIQUE (
        season_id,
        stage_id,
        normalized_name
    )
    WHERE stage_id IS NOT NULL

A sintaxe definitiva deverá ser criada nas migrations do Alembic e validada no
PostgreSQL.

#### Índices para ordenação cronológica

Consultas cronológicas serão frequentes em:

- calendários;
- páginas de competição;
- páginas de temporada;
- filtros de jogos;
- sincronizações incrementais;
- análises históricas.

Por isso, os índices compostos deverão começar pela coluna utilizada para
limitar o contexto da consulta.

Exemplos:

    competition_id, start_date
    season_id, start_date
    stage_id, start_date
    season_id, sequence
    stage_id, sequence

Um índice iniciado por `season_id` será mais adequado quando a consulta sempre
for limitada a uma temporada.

Um índice iniciado apenas pela data poderá ser útil para consultas globais, mas
deverá ser criado somente quando esse padrão estiver confirmado.

#### Índices para registros ativos

Filtros por `is_active` isoladamente poderão apresentar baixa seletividade.

Por esse motivo, índices compostos ou parciais poderão ser mais úteis do que um
índice simples.

Exemplo conceitual para competições ativas:

    INDEX ON competition (
        country_id,
        normalized_name
    )
    WHERE is_active = true

Exemplo conceitual para temporadas ativas:

    INDEX ON season (
        competition_id,
        start_date
    )
    WHERE is_active = true

O uso de índices parciais deverá ser avaliado de acordo com a proporção entre
registros ativos e históricos.

#### Índices para sincronização com providers

Identificadores externos não deverão ser armazenados diretamente nas entidades
canônicas como identidade principal.

Eles deverão ser mantidos em tabelas de mapeamento específicas.

A estrutura conceitual poderá utilizar:

    provider
    entity_type
    external_id
    canonical_entity_id

A combinação abaixo deverá ser única dentro do mapeamento:

    provider
    entity_type
    external_id

Também deverá existir índice sobre:

    canonical_entity_id

Isso permitirá:

- localizar rapidamente a entidade canônica correspondente;
- evitar duplicidade de IDs externos;
- listar todos os providers associados a uma entidade;
- reprocessar associações;
- revisar conflitos de resolução de identidade.

#### Índices para nomes e aliases

A busca por nomes poderá utilizar:

- nome original;
- nome normalizado;
- nome oficial;
- nome abreviado;
- aliases;
- traduções.

Os aliases não deverão ser armazenados em uma coluna única contendo listas.

Eles deverão ser normalizados em estruturas próprias, permitindo índices
independentes.

Uma tabela de aliases poderá utilizar conceitualmente:

    id
    entity_type
    entity_id
    language_code
    alias
    normalized_alias
    alias_type
    created_at

Índices recomendados para aliases:

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_entity_alias_entity` | `entity_type, entity_id` | Listar aliases de uma entidade. |
| `ix_entity_alias_normalized` | `normalized_alias` | Buscar entidades por alias normalizado. |
| `ix_entity_alias_language` | `language_code, normalized_alias` | Buscar aliases por idioma. |
| `ux_entity_alias_identity` | `entity_type, entity_id, language_code, normalized_alias` | Evitar aliases duplicados. |

#### Busca textual aproximada

A resolução de identidade poderá exigir busca aproximada por nomes.

No PostgreSQL, poderá ser considerada futuramente a extensão:

    pg_trgm

Ela poderá auxiliar em:

- similaridade textual;
- correção de pequenas diferenças de escrita;
- comparação de abreviações;
- busca por aliases próximos;
- sugestões para revisão manual.

Exemplos de diferenças que poderão exigir similaridade:

    Manchester United
    Man United
    Manchester Utd
    Man. United

A busca aproximada não deverá criar associações automaticamente sem critérios
adicionais.

Ela deverá ser combinada com informações como:

- país;
- competição;
- organizador;
- temporada;
- tipo da entidade;
- identificadores conhecidos;
- nível de confiança.

#### Diretrizes de implementação

- nomes dos índices deverão seguir um padrão consistente;
- índices únicos deverão ser diferenciados de índices comuns;
- índices parciais deverão possuir condições documentadas;
- migrations deverão permitir aplicação e reversão;
- índices redundantes deverão ser evitados;
- chaves estrangeiras deverão possuir índices quando forem usadas em consultas;
- índices deverão ser revisados com `EXPLAIN` e `EXPLAIN ANALYZE`;
- índices não utilizados deverão ser avaliados para remoção;
- alterações de indexação deverão ser medidas em ambiente de teste;
- a integridade dos dados não deverá depender somente da aplicação.

#### Padrão sugerido de nomenclatura

Para índices comuns:

    ix_<tabela>_<colunas>

Exemplos:

    ix_season_competition_id
    ix_stage_season_sequence
    ix_round_stage_sequence

Para índices únicos:

    ux_<tabela>_<colunas>

Exemplos:

    ux_season_competition_name
    ux_stage_season_name
    ux_round_stage_name

Para restrições de unicidade:

    uq_<tabela>_<colunas>

Exemplos:

    uq_season_competition_name
    uq_provider_mapping_external_identity

Para chaves estrangeiras:

    fk_<tabela>_<coluna>_<tabela_referenciada>

Exemplos:

    fk_season_competition_id_competition
    fk_stage_season_id_season
    fk_round_stage_id_stage

O padrão definitivo deverá ser aplicado de forma uniforme nas models e nas
migrations do projeto.

---

### 6.7 Resumo das entidades do domínio competitivo

A estrutura canônica definida nesta seção será:

    Competition
    └── Season
        ├── Stage
        │   ├── Round
        │   └── Match
        ├── Round
        │   └── Match
        └── Match

As responsabilidades principais serão:

| Entidade | Responsabilidade |
|----------|------------------|
| `Competition` | Representar o campeonato, copa ou torneio. |
| `Season` | Representar uma edição temporal da competição. |
| `Stage` | Representar uma fase interna da temporada. |
| `Round` | Representar uma rodada ou jornada. |

A hierarquia deverá ser flexível o suficiente para representar:

- ligas de pontos corridos;
- copas eliminatórias;
- competições com fase de grupos;
- competições com qualificatórias;
- competições com playoffs;
- torneios curtos;
- competições sem rodadas explícitas;
- competições sem fases explícitas;
- estruturas incompletas recebidas de providers.

Nenhuma estrutura artificial deverá ser criada apenas para preencher todos os
níveis da hierarquia.

A ausência legítima de `Stage` ou `Round` deverá ser representada com valores
nulos e relacionamentos opcionais, conforme as regras documentadas nesta seção.
---

## 7. Participantes do futebol


Esta seção define as entidades responsáveis por representar os participantes
envolvidos nas competições, temporadas e partidas.

O domínio deverá permitir representar:

- clubes profissionais;
- seleções nacionais;
- equipes de base;
- equipes femininas;
- equipes reservas;
- equipes temporárias;
- jogadores;
- treinadores;
- árbitros;
- membros de comissão técnica;
- outras pessoas relacionadas às partidas.

As principais entidades desta seção serão:

    Team
    Person
    Player
    Coach
    Referee
    TeamMembership
    SquadRegistration

A entidade `Team` representará organizações esportivas coletivas.

A entidade `Person` representará a identidade humana canônica.

Entidades especializadas, como `Player`, `Coach` e `Referee`, deverão utilizar
`Person` como base, evitando a criação de identidades humanas duplicadas.

---

### 7.1 Team

A entidade `Team` representa uma equipe participante de competições e partidas.

Ela poderá representar tanto clubes quanto seleções nacionais, equipes de base,
equipes femininas, equipes reservas ou outras organizações esportivas
reconhecidas pelos providers.

Exemplos:

    Flamengo
    Palmeiras
    Real Madrid
    Manchester City
    Seleção Brasileira
    Seleção Argentina
    Barcelona Feminino
    Real Madrid Castilla
    Brasil Sub-20

Uma equipe deverá possuir uma identidade canônica própria, independente dos
identificadores utilizados pelos providers.

#### Responsabilidades

A entidade `Team` será responsável por:

- identificar uma equipe de forma canônica;
- armazenar seus nomes principais;
- indicar seu tipo;
- relacionar a equipe a um país;
- diferenciar clubes, seleções e equipes de base;
- preservar informações históricas;
- permitir associação com competições e partidas;
- servir como referência para jogadores e comissões técnicas;
- permitir associação com estádios;
- permitir resolução de identidade entre múltiplos providers.

#### Campos principais

    id
    country_id
    city_id
    stadium_id
    name
    official_name
    short_name
    common_name
    normalized_name
    team_type
    gender
    age_category
    foundation_date
    primary_color
    secondary_color
    logo_url
    website_url
    is_national_team
    is_reserve_team
    is_active
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno e canônico da equipe. |
| `country_id` | UUID | Não | País principal associado à equipe. |
| `city_id` | UUID | Não | Cidade principal da equipe. |
| `stadium_id` | UUID | Não | Estádio principal utilizado pela equipe. |
| `name` | string | Sim | Nome principal utilizado pelo sistema. |
| `official_name` | string | Não | Nome oficial completo da equipe. |
| `short_name` | string | Não | Nome abreviado para interfaces compactas. |
| `common_name` | string | Não | Nome pelo qual a equipe é conhecida publicamente. |
| `normalized_name` | string | Sim | Nome normalizado para busca e comparação. |
| `team_type` | enum | Sim | Classificação estrutural da equipe. |
| `gender` | enum | Sim | Categoria de gênero da equipe. |
| `age_category` | enum | Sim | Categoria etária da equipe. |
| `foundation_date` | date | Não | Data oficial de fundação. |
| `primary_color` | string | Não | Cor principal em formato padronizado. |
| `secondary_color` | string | Não | Cor secundária em formato padronizado. |
| `logo_url` | string | Não | URL da identidade visual da equipe. |
| `website_url` | string | Não | Site oficial da equipe. |
| `is_national_team` | boolean | Sim | Indica se representa uma seleção. |
| `is_reserve_team` | boolean | Sim | Indica se é uma equipe reserva ou secundária. |
| `is_active` | boolean | Sim | Indica se a equipe está ativa no domínio. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Tipos de equipe previstos

    CLUB
    NATIONAL_TEAM
    REGIONAL_TEAM
    ACADEMY
    RESERVE
    UNIVERSITY
    SCHOOL
    AMATEUR
    TEMPORARY
    OTHER
    UNKNOWN

O valor `CLUB` deverá ser utilizado para clubes profissionais ou amadores que
possuam identidade própria.

O valor `NATIONAL_TEAM` deverá ser utilizado para equipes que representem
oficialmente um país.

O valor `ACADEMY` deverá ser utilizado para equipes vinculadas a estruturas de
formação.

O valor `RESERVE` deverá representar equipes secundárias, como equipes B ou
equipes de desenvolvimento.

#### Categorias de gênero previstas

    MEN
    WOMEN
    MIXED
    UNKNOWN

A categoria de gênero deverá fazer parte da identidade competitiva da equipe.

Equipes masculinas e femininas pertencentes à mesma organização não deverão ser
tratadas como uma única entidade esportiva.

Exemplo:

    Barcelona Masculino
    Barcelona Feminino

Essas equipes poderão compartilhar uma organização ou marca, mas deverão possuir
identificadores canônicos distintos.

#### Categorias etárias previstas

    SENIOR
    U23
    U21
    U20
    U19
    U18
    U17
    U16
    U15
    YOUTH
    OTHER
    UNKNOWN

A categoria `SENIOR` deverá representar a equipe principal sem limitação etária.

As categorias iniciadas por `U` deverão representar limites máximos de idade.

A categoria `YOUTH` poderá ser utilizada quando o provider informar apenas que
a equipe é de base, sem indicar uma faixa etária exata.

#### Relacionamentos principais

    Country  1 ─── N Team
    City     1 ─── N Team
    Stadium  1 ─── N Team

    Team     1 ─── N TeamMembership
    Team     1 ─── N SquadRegistration

    Team     1 ─── N Match como mandante
    Team     1 ─── N Match como visitante

Os relacionamentos com `Country`, `City` e `Stadium` poderão ser opcionais,
dependendo da disponibilidade e da confiabilidade dos dados.

Uma seleção nacional normalmente deverá possuir `country_id`, mas poderá não
possuir `city_id`.

Um clube normalmente poderá possuir `country_id` e `city_id`.

O estádio principal não deverá impedir que a equipe participe de partidas em
outros estádios.

#### Regras de integridade

- `name` não poderá ser vazio;
- `normalized_name` não poderá ser vazio;
- `team_type` deverá possuir um valor válido;
- `gender` deverá possuir um valor válido;
- `age_category` deverá possuir um valor válido;
- `country_id`, quando informado, deverá referenciar um país existente;
- `city_id`, quando informado, deverá referenciar uma cidade existente;
- a cidade informada deverá ser compatível com o país da equipe;
- `stadium_id`, quando informado, deverá referenciar um estádio existente;
- `foundation_date` não poderá estar no futuro;
- `is_national_team = true` deverá ser compatível com o tipo
  `NATIONAL_TEAM`;
- equipes de seleções nacionais normalmente deverão possuir `country_id`;
- equipes femininas e masculinas deverão possuir identidades distintas;
- equipes de categorias etárias diferentes deverão possuir identidades
  distintas;
- equipes reservas deverão possuir identidade distinta da equipe principal;
- uma equipe inativa poderá permanecer disponível para consultas históricas;
- uma equipe não deverá ser removida fisicamente enquanto possuir partidas,
  membros ou registros históricos associados.

#### Regra inicial de unicidade

A unicidade de uma equipe não deverá depender exclusivamente de seu nome.

Uma combinação candidata para clubes será:

    country_id
    normalized_name
    gender
    age_category
    team_type

Para seleções nacionais, uma combinação candidata será:

    country_id
    gender
    age_category
    team_type

Essas combinações representam apenas uma estratégia inicial.

A resolução definitiva deverá considerar:

- aliases;
- nomes oficiais;
- nomes abreviados;
- cidade;
- país;
- tipo da equipe;
- gênero;
- categoria etária;
- organização esportiva;
- identificadores externos;
- histórico conhecido;
- nível de confiança da associação.

#### Diretrizes de resolução de identidade

Nomes semelhantes não deverão ser associados automaticamente sem contexto.

Exemplos de nomes que poderão representar a mesma equipe:

    Manchester United
    Man United
    Manchester Utd
    Man. United

Exemplos de nomes semelhantes que poderão representar equipes diferentes:

    Barcelona
    Barcelona B
    Barcelona U19
    Barcelona Feminino

A resolução deverá avaliar conjuntamente:

- nome normalizado;
- país;
- cidade;
- tipo da equipe;
- gênero;
- categoria etária;
- informação de equipe reserva;
- competição;
- provider de origem;
- identificadores externos conhecidos.

Associações automáticas deverão possuir um nível mínimo de confiança.

Associações abaixo do limite definido deverão ser registradas para revisão
manual.

#### Nomes históricos

Mudanças de nome não deverão substituir ou apagar a identidade histórica da
equipe.

Quando uma equipe alterar seu nome, deverão ser preservados:

- nome anterior;
- nome atual;
- intervalo de validade;
- motivo conhecido da alteração;
- provider que informou a mudança;
- nível de confiança da informação.

A estrutura conceitual de nomes históricos poderá utilizar:

    id
    team_id
    name
    normalized_name
    valid_from
    valid_until
    is_official
    source_provider
    created_at

Uma alteração de nome não deverá criar automaticamente uma nova equipe.

Entretanto, fusões, dissoluções, refundação ou transferência de identidade
poderão exigir entidades canônicas distintas.

Esses casos deverão ser tratados individualmente e poderão exigir revisão
manual.

#### Identidade organizacional e identidade esportiva

Uma mesma organização poderá controlar diversas equipes esportivas.

Exemplo:

    Clube principal
    Equipe feminina
    Equipe sub-20
    Equipe sub-17
    Equipe reserva

Essas equipes poderão compartilhar:

- nome institucional;
- escudo;
- estádio;
- cidade;
- estrutura administrativa.

Mesmo assim, deverão possuir entidades `Team` distintas quando disputarem
competições como participantes independentes.

Futuramente, uma entidade separada poderá representar a organização esportiva
superior.

Exemplo conceitual:

    SportsOrganization
    ├── Team principal
    ├── Team feminino
    ├── Team sub-20
    └── Team sub-17

A criação dessa entidade não será obrigatória nesta primeira implementação.

#### Equipes extintas e inativas

Equipes extintas ou temporariamente inativas deverão ser preservadas para
consultas históricas.

Nesses casos:

    is_active = false

A inativação não deverá excluir:

- partidas históricas;
- temporadas disputadas;
- estatísticas;
- elencos;
- transferências;
- nomes anteriores;
- mapeamentos de providers.

Uma equipe inativa poderá voltar a ser ativada caso retome suas atividades e a
identidade esportiva seja considerada a mesma.

#### Dados visuais

Campos como `logo_url`, `primary_color` e `secondary_color` deverão ser tratados
como dados auxiliares de apresentação.

Eles não deverão participar diretamente da resolução principal de identidade.

Logotipos poderão mudar ao longo do tempo.

Por isso, futuras versões do domínio poderão manter histórico de identidades
visuais.

As cores deverão utilizar um formato padronizado.

Formato inicial recomendado:

    #RRGGBB

Exemplo:

    #FF0000
    #000000
    #FFFFFF

Valores recebidos em outros formatos deverão ser normalizados antes da gravação
canônica.

#### Índices recomendados para Team

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_team_country_id` | `country_id` | Buscar equipes de um país. |
| `ix_team_city_id` | `city_id` | Buscar equipes de uma cidade. |
| `ix_team_stadium_id` | `stadium_id` | Buscar equipes associadas a um estádio. |
| `ix_team_normalized_name` | `normalized_name` | Buscar equipes por nome normalizado. |
| `ix_team_type` | `team_type` | Filtrar equipes pelo tipo. |
| `ix_team_gender` | `gender` | Filtrar equipes pela categoria de gênero. |
| `ix_team_age_category` | `age_category` | Filtrar equipes pela categoria etária. |
| `ix_team_is_national_team` | `is_national_team` | Localizar seleções. |
| `ix_team_is_active` | `is_active` | Separar equipes ativas e históricas. |
| `ix_team_country_name` | `country_id, normalized_name` | Buscar equipes pelo país e nome. |
| `ix_team_identity` | `country_id, normalized_name, gender, age_category` | Apoiar resolução de identidade. |
| `ix_team_active_country` | `country_id, is_active` | Buscar equipes ativas de um país. |

A criação de índices individuais para colunas booleanas deverá ser avaliada com
cuidado, pois elas poderão apresentar baixa seletividade.

Índices compostos ou parciais poderão ser mais úteis.

Exemplo conceitual:

    INDEX ON team (
        country_id,
        normalized_name
    )
    WHERE is_active = true

#### Dependências futuras

A entidade `Team` será utilizada por:

- partidas;
- escalações;
- elencos;
- transferências;
- estatísticas de equipes;
- tabelas de classificação;
- odds;
- mercados de apostas;
- modelos de previsão;
- suspensões;
- lesões;
- treinadores;
- jogadores;
- histórico de confrontos;
- desempenho como mandante;
- desempenho como visitante.

Por isso, sua identidade deverá ser estável e não depender de um provider
específico.

---

### 7.2 Person

A entidade `Person` representa a identidade humana canônica dentro do domínio do
futebol.

Ela será utilizada como base para representar diferentes funções exercidas por
uma mesma pessoa ao longo do tempo.

Exemplos:

    jogador
    treinador
    auxiliar técnico
    preparador físico
    árbitro
    assistente de arbitragem
    dirigente
    membro de comissão técnica

Uma pessoa poderá exercer mais de uma função durante sua carreira.

Exemplos:

    jogador que posteriormente se tornou treinador
    treinador que também atuou como auxiliar técnico
    ex-jogador que passou a exercer função de dirigente
    árbitro que posteriormente passou a atuar como instrutor

Por isso, a identidade humana não deverá ser duplicada apenas porque a função
profissional foi alterada.

#### Responsabilidades

A entidade `Person` será responsável por:

- representar uma pessoa de forma canônica;
- armazenar nomes principais e nomes conhecidos;
- preservar informações biográficas;
- registrar nacionalidade;
- permitir associação com diferentes funções profissionais;
- evitar duplicidade entre jogadores, treinadores e árbitros;
- preservar identidades históricas;
- permitir associação com múltiplos providers;
- apoiar a resolução de identidade;
- servir como base para entidades especializadas.

#### Campos principais

    id
    country_of_birth_id
    nationality_country_id
    city_of_birth_id
    first_name
    middle_name
    last_name
    full_name
    common_name
    display_name
    normalized_name
    date_of_birth
    date_of_death
    gender
    height_cm
    weight_kg
    preferred_foot
    photo_url
    is_active
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno e canônico da pessoa. |
| `country_of_birth_id` | UUID | Não | País de nascimento. |
| `nationality_country_id` | UUID | Não | Nacionalidade principal conhecida. |
| `city_of_birth_id` | UUID | Não | Cidade de nascimento. |
| `first_name` | string | Não | Primeiro nome. |
| `middle_name` | string | Não | Nome intermediário. |
| `last_name` | string | Não | Sobrenome principal. |
| `full_name` | string | Sim | Nome completo ou melhor nome disponível. |
| `common_name` | string | Não | Nome pelo qual a pessoa é conhecida publicamente. |
| `display_name` | string | Sim | Nome utilizado na interface. |
| `normalized_name` | string | Sim | Nome normalizado para busca e comparação. |
| `date_of_birth` | date | Não | Data de nascimento. |
| `date_of_death` | date | Não | Data de falecimento, quando aplicável. |
| `gender` | enum | Sim | Categoria de gênero informada ou conhecida. |
| `height_cm` | integer | Não | Altura em centímetros. |
| `weight_kg` | decimal | Não | Peso em quilogramas. |
| `preferred_foot` | enum | Não | Pé preferencial, quando aplicável. |
| `photo_url` | string | Não | URL de fotografia ou imagem de perfil. |
| `is_active` | boolean | Sim | Indica se a pessoa está ativa no domínio. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Estratégia de nomes

Os campos relacionados a nome possuem funções diferentes.

`full_name` deverá armazenar o nome completo ou o melhor nome oficial disponível.

Exemplo:

    Neymar da Silva Santos Júnior

`common_name` deverá armazenar o nome pelo qual a pessoa é amplamente conhecida.

Exemplo:

    Neymar

`display_name` deverá armazenar o nome preferencial para exibição na interface.

Exemplo:

    Neymar Jr.

`normalized_name` deverá armazenar uma versão preparada para comparação e busca.

Exemplo conceitual:

    neymar da silva santos junior

A normalização poderá incluir:

- conversão para letras minúsculas;
- remoção controlada de acentos;
- remoção de pontuação;
- normalização de espaços;
- padronização de caracteres;
- remoção de espaços duplicados.

A normalização não deverá substituir os nomes originais.

#### Categorias de gênero previstas

    MALE
    FEMALE
    NON_BINARY
    OTHER
    UNKNOWN

O valor `UNKNOWN` deverá ser utilizado quando o dado não estiver disponível ou
não puder ser confirmado.

O gênero não deverá ser inferido automaticamente com base apenas no nome.

#### Valores previstos para pé preferencial

    RIGHT
    LEFT
    BOTH
    UNKNOWN

O campo `preferred_foot` será principalmente utilizado para jogadores.

Para pessoas que não exerçam funções esportivas em campo, o valor poderá
permanecer nulo.

O valor `BOTH` deverá ser utilizado quando o provider indicar que a pessoa possui
habilidade equivalente com os dois pés.

#### Relacionamentos principais

    Country  1 ─── N Person como país de nascimento
    Country  1 ─── N Person como nacionalidade
    City     1 ─── N Person como cidade de nascimento

    Person   1 ─── 0..1 Player
    Person   1 ─── 0..1 Coach
    Person   1 ─── 0..1 Referee

    Person   1 ─── N TeamMembership
    Person   1 ─── N SquadRegistration

Uma pessoa poderá possuir simultaneamente mais de um perfil especializado,
desde que isso represente corretamente sua trajetória profissional.

Exemplo:

    Person
    ├── Player
    └── Coach

Esse cenário poderá ocorrer quando um jogador também exercer função de treinador
ou quando os dados históricos precisarem preservar as duas funções.

#### Regras de integridade

- `full_name` não poderá ser vazio;
- `display_name` não poderá ser vazio;
- `normalized_name` não poderá ser vazio;
- `gender` deverá possuir um valor válido;
- `country_of_birth_id`, quando informado, deverá referenciar um país existente;
- `nationality_country_id`, quando informado, deverá referenciar um país
  existente;
- `city_of_birth_id`, quando informado, deverá referenciar uma cidade existente;
- a cidade de nascimento deverá ser compatível com o país de nascimento, quando
  ambos forem informados;
- `date_of_birth` não poderá estar no futuro;
- `date_of_death`, quando informada, deverá ser posterior ou igual à data de
  nascimento;
- `height_cm`, quando informada, deverá ser maior que zero;
- `weight_kg`, quando informado, deverá ser maior que zero;
- `preferred_foot`, quando informado, deverá possuir um valor válido;
- a ausência de data de nascimento não deverá impedir a criação da pessoa;
- uma pessoa inativa deverá permanecer disponível para consultas históricas;
- uma pessoa não deverá ser removida fisicamente enquanto possuir funções,
  partidas, estatísticas ou vínculos associados.

#### Validações adicionais de dados físicos

Valores físicos recebidos de providers poderão conter erros de unidade ou
digitação.

Exemplos de problemas:

    altura informada como 1.80 em campo esperado em centímetros
    altura informada como 1800
    peso informado em libras sem identificação da unidade
    peso informado como zero
    altura e peso trocados

Antes da gravação canônica, os dados deverão ser normalizados e validados.

Faixas plausíveis poderão ser utilizadas para gerar alertas de qualidade.

Essas faixas não deverão necessariamente bloquear todos os registros, pois
existem exceções reais.

Exemplo de validação inicial:

    height_cm entre 100 e 230
    weight_kg entre 30 e 200

Valores fora dessas faixas deverão ser marcados para revisão.

#### Regra inicial de unicidade

A identidade de uma pessoa não deverá depender exclusivamente do nome.

Uma combinação candidata será:

    normalized_name
    date_of_birth
    nationality_country_id

Quando a cidade ou o país de nascimento estiverem disponíveis, poderão ser
utilizados como critérios adicionais:

    normalized_name
    date_of_birth
    country_of_birth_id
    city_of_birth_id

Nenhuma dessas combinações deverá ser considerada universalmente suficiente.

Pessoas diferentes poderão possuir:

- o mesmo nome;
- a mesma data de nascimento;
- a mesma nacionalidade;
- nomes muito semelhantes;
- nomes artísticos iguais.

Uma mesma pessoa também poderá aparecer com:

- nome completo;
- nome abreviado;
- apelido;
- nome artístico;
- nome com ordem diferente;
- nome transliterado;
- nome traduzido;
- nome com ou sem acentos.

#### Diretrizes de resolução de identidade

A resolução de identidade deverá considerar múltiplos atributos.

Critérios possíveis:

- nome completo;
- nome conhecido;
- data de nascimento;
- nacionalidade;
- país de nascimento;
- cidade de nascimento;
- altura;
- posição;
- equipe atual;
- equipes anteriores;
- função profissional;
- provider de origem;
- identificadores externos;
- fotografia;
- período de atividade.

Exemplos de nomes que poderão representar a mesma pessoa:

    Cristiano Ronaldo dos Santos Aveiro
    Cristiano Ronaldo
    C. Ronaldo
    Ronaldo

Exemplos de nomes semelhantes que poderão representar pessoas diferentes:

    Ronaldo
    Cristiano Ronaldo
    Ronaldo Nazário
    Ronaldinho

A associação automática não deverá ocorrer somente por similaridade textual.

A similaridade deverá ser combinada com informações biográficas e contextuais.

#### Nomes alternativos e aliases

Uma pessoa poderá possuir múltiplos nomes conhecidos.

Exemplos:

    nome civil
    nome esportivo
    apelido
    abreviação
    transliteração
    nome anterior
    nome em outro idioma

Esses nomes deverão ser armazenados em uma estrutura de aliases.

Estrutura conceitual:

    id
    person_id
    alias
    normalized_alias
    alias_type
    language_code
    valid_from
    valid_until
    is_primary
    source_provider
    created_at

Tipos de alias previstos:

    OFFICIAL
    COMMON
    NICKNAME
    SPORTING_NAME
    ABBREVIATION
    TRANSLITERATION
    TRANSLATION
    FORMER_NAME
    OTHER

Um alias não deverá substituir automaticamente o nome principal.

O sistema deverá preservar a origem de cada alias.

#### Nacionalidade e país de nascimento

Nacionalidade e país de nascimento representam conceitos distintos.

Exemplo:

    uma pessoa poderá nascer em um país
    e representar esportivamente outro país

Por isso, deverão existir campos separados:

    country_of_birth_id
    nationality_country_id

Futuramente, uma pessoa poderá possuir múltiplas nacionalidades.

Nesse cenário, poderá ser criada uma estrutura própria:

    PersonNationality
    ├── person_id
    ├── country_id
    ├── nationality_type
    ├── valid_from
    ├── valid_until
    └── is_primary

A primeira implementação poderá utilizar apenas uma nacionalidade principal.

#### Histórico de nacionalidade esportiva

Em algumas situações, uma pessoa poderá alterar sua representação esportiva ou
possuir múltiplas elegibilidades.

Esses casos não deverão ser resolvidos sobrescrevendo informações históricas.

Futuramente, poderá existir uma estrutura como:

    PersonSportNationality
    ├── person_id
    ├── country_id
    ├── valid_from
    ├── valid_until
    ├── is_primary
    └── source_provider

Essa estrutura será especialmente relevante para:

- jogadores de seleções;
- atletas naturalizados;
- categorias de base;
- mudanças de elegibilidade;
- registros históricos.

#### Pessoas falecidas

Pessoas falecidas deverão permanecer no domínio para preservar:

- partidas históricas;
- estatísticas;
- títulos;
- registros de carreira;
- funções exercidas;
- vínculos com equipes;
- eventos históricos.

Nesses casos, poderá ser utilizado:

    date_of_death preenchido
    is_active = false

O campo `is_active` não deverá ser interpretado exclusivamente como indicação de
vida ou falecimento.

Ele poderá indicar se o registro permanece ativo operacionalmente.

#### Pessoas aposentadas

Uma pessoa aposentada não deverá ser removida.

Ela poderá permanecer com:

    is_active = false

Entretanto, a condição de aposentadoria deverá preferencialmente ser registrada
no perfil profissional especializado, como `Player` ou `Referee`.

Isso permitirá diferenciar:

- pessoa falecida;
- jogador aposentado;
- treinador inativo;
- árbitro aposentado;
- profissional temporariamente sem vínculo.

#### Dados visuais

O campo `photo_url` deverá ser tratado como informação auxiliar de apresentação.

A fotografia não deverá ser usada como identificador único.

Imagens poderão:

- mudar ao longo do tempo;
- ficar indisponíveis;
- possuir direitos de uso;
- ser substituídas pelo provider;
- representar versões desatualizadas.

Futuramente, poderá existir histórico de imagens.

Estrutura conceitual:

    id
    person_id
    image_url
    image_type
    valid_from
    valid_until
    source_provider
    created_at

#### Privacidade e minimização de dados

A entidade `Person` deverá armazenar somente informações relevantes ao domínio
esportivo.

Dados pessoais desnecessários não deverão ser coletados.

Não deverão ser armazenados sem necessidade:

- documentos pessoais;
- endereço residencial;
- telefone pessoal;
- e-mail pessoal;
- informações financeiras;
- dados familiares privados;
- dados sensíveis sem finalidade esportiva legítima.

A modelagem deverá seguir princípios de minimização, necessidade e finalidade.

#### Índices recomendados para Person

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_person_normalized_name` | `normalized_name` | Buscar pessoas por nome normalizado. |
| `ix_person_date_of_birth` | `date_of_birth` | Filtrar ou validar pela data de nascimento. |
| `ix_person_country_of_birth_id` | `country_of_birth_id` | Buscar pessoas pelo país de nascimento. |
| `ix_person_nationality_country_id` | `nationality_country_id` | Buscar pessoas pela nacionalidade principal. |
| `ix_person_city_of_birth_id` | `city_of_birth_id` | Buscar pessoas pela cidade de nascimento. |
| `ix_person_gender` | `gender` | Filtrar pessoas pela categoria de gênero. |
| `ix_person_is_active` | `is_active` | Separar registros ativos e históricos. |
| `ix_person_name_birth_date` | `normalized_name, date_of_birth` | Apoiar resolução de identidade. |
| `ix_person_name_nationality` | `normalized_name, nationality_country_id` | Apoiar busca contextual. |
| `ix_person_identity` | `normalized_name, date_of_birth, nationality_country_id` | Apoiar identificação canônica. |

Índices isolados em campos de baixa seletividade, como `gender` e `is_active`,
deverão ser avaliados conforme o padrão real de consultas.

Índices compostos ou parciais poderão ser mais adequados.

Exemplo conceitual:

    INDEX ON person (
        normalized_name,
        date_of_birth
    )
    WHERE is_active = true

#### Busca aproximada por nome

A busca aproximada poderá ser utilizada para localizar possíveis correspondências.

Ela poderá considerar:

- similaridade entre nomes;
- aliases;
- transliterações;
- abreviações;
- remoção de acentos;
- inversão de ordem;
- nomes esportivos.

Exemplo:

    João Pedro Silva
    Joao Pedro Silva
    João P. Silva
    J. Pedro Silva

A busca aproximada deverá apenas gerar candidatos.

A associação final deverá considerar também:

- data de nascimento;
- nacionalidade;
- equipes relacionadas;
- função;
- provider;
- identificadores externos;
- nível de confiança.

#### Dependências futuras

A entidade `Person` será utilizada por:

- jogadores;
- treinadores;
- árbitros;
- assistentes;
- comissões técnicas;
- escalações;
- elencos;
- transferências;
- eventos de partidas;
- gols;
- cartões;
- substituições;
- estatísticas individuais;
- lesões;
- suspensões;
- modelos de desempenho;
- histórico profissional.

Por isso, sua identidade deverá permanecer estável mesmo quando a pessoa mudar
de equipe, função, país ou situação profissional.

---

### 7.3 Player

A entidade `Player` representa o perfil esportivo de uma pessoa que atua ou
atuou como jogador de futebol.

A identidade humana deverá permanecer armazenada em `Person`.

A entidade `Player` deverá armazenar somente informações específicas da carreira
do atleta.

Exemplo conceitual:

    Person
    └── Player

Uma pessoa deverá possuir no máximo um perfil canônico principal de jogador.

Mudanças de equipe, posição, número de camisa ou situação profissional não
deverão criar novos registros de `Player`.

#### Responsabilidades

A entidade `Player` será responsável por:

- representar o perfil esportivo de um jogador;
- vincular o jogador à identidade humana canônica;
- armazenar sua posição principal;
- registrar posições secundárias;
- indicar seu pé preferencial esportivo;
- registrar seu estado profissional;
- indicar se o jogador está aposentado;
- servir como referência para elencos;
- servir como referência para escalações;
- permitir associação com transferências;
- permitir associação com estatísticas;
- permitir associação com eventos de partidas;
- preservar o histórico profissional do atleta.

#### Campos principais

    id
    person_id
    primary_position
    secondary_position
    player_status
    professional_debut_date
    retirement_date
    market_value
    market_value_currency
    shirt_name
    is_retired
    is_active
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno e canônico do perfil de jogador. |
| `person_id` | UUID | Sim | Pessoa canônica associada ao jogador. |
| `primary_position` | enum | Sim | Posição principal conhecida do jogador. |
| `secondary_position` | enum | Não | Posição secundária mais relevante. |
| `player_status` | enum | Sim | Estado profissional atual do jogador. |
| `professional_debut_date` | date | Não | Data conhecida da estreia profissional. |
| `retirement_date` | date | Não | Data conhecida da aposentadoria. |
| `market_value` | decimal | Não | Valor de mercado informado por uma fonte. |
| `market_value_currency` | string | Não | Código da moeda utilizada no valor de mercado. |
| `shirt_name` | string | Não | Nome normalmente exibido na camisa. |
| `is_retired` | boolean | Sim | Indica se o jogador está aposentado. |
| `is_active` | boolean | Sim | Indica se o perfil permanece ativo no domínio. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Posições principais previstas

    GOALKEEPER
    DEFENDER
    MIDFIELDER
    FORWARD
    UNKNOWN

Essas categorias representam agrupamentos gerais.

Elas poderão ser utilizadas quando o provider não fornecer uma posição mais
específica.

#### Posições detalhadas previstas

    GOALKEEPER
    SWEEPER
    CENTRE_BACK
    LEFT_CENTRE_BACK
    RIGHT_CENTRE_BACK
    LEFT_BACK
    RIGHT_BACK
    LEFT_WING_BACK
    RIGHT_WING_BACK
    DEFENSIVE_MIDFIELDER
    CENTRAL_MIDFIELDER
    LEFT_MIDFIELDER
    RIGHT_MIDFIELDER
    ATTACKING_MIDFIELDER
    LEFT_WINGER
    RIGHT_WINGER
    SECOND_STRIKER
    CENTRE_FORWARD
    STRIKER
    UTILITY_PLAYER
    OTHER
    UNKNOWN

A implementação inicial poderá utilizar apenas uma enumeração de posição.

Entretanto, a modelagem deverá permitir evolução futura para separar:

    position_group
    primary_position
    secondary_positions

Exemplo:

    position_group = DEFENDER
    primary_position = RIGHT_BACK
    secondary_positions = RIGHT_WING_BACK, LEFT_BACK

#### Estratégia para múltiplas posições

Um jogador poderá atuar em diversas posições.

O campo `primary_position` deverá representar a posição principal conhecida.

O campo `secondary_position` poderá armazenar temporariamente uma posição
secundária mais relevante.

Entretanto, uma modelagem futura mais completa deverá utilizar uma estrutura
própria.

Exemplo conceitual:

    PlayerPosition
    ├── id
    ├── player_id
    ├── position
    ├── is_primary
    ├── proficiency_level
    ├── valid_from
    ├── valid_until
    ├── source_provider
    └── created_at

Essa estrutura permitirá registrar:

- múltiplas posições;
- posição principal;
- nível de familiaridade;
- mudanças ao longo da carreira;
- posições informadas por providers diferentes;
- histórico temporal.

A primeira versão poderá manter apenas `primary_position` e
`secondary_position`.

#### Pé preferencial

O pé preferencial deverá permanecer armazenado canonicamente em `Person`.

A entidade `Player` deverá consultar esse valor por meio do relacionamento:

    Player.person_id
    Person.preferred_foot

Essa decisão evita duas fontes canônicas para o mesmo atributo.

Quando providers esportivos informarem um pé preferencial diferente do valor
atualmente armazenado em `Person`, o sistema deverá:

- preservar a observação do provider;
- comparar a confiabilidade das fontes;
- registrar o conflito;
- evitar sobrescrita silenciosa;
- atualizar o valor canônico somente após resolução.

Os valores previstos continuarão sendo:

    RIGHT
    LEFT
    BOTH
    UNKNOWN

Informações contextuais mais específicas, como o pé utilizado em uma cobrança,
passe, finalização ou evento de partida, deverão permanecer nas entidades de
eventos e estatísticas.

#### Status profissionais previstos

    YOUTH
    AMATEUR
    PROFESSIONAL
    FREE_AGENT
    LOANED
    SUSPENDED
    INJURED
    INACTIVE
    RETIRED
    UNKNOWN

O status `YOUTH` deverá indicar um jogador em formação.

O status `AMATEUR` deverá indicar atuação não profissional.

O status `PROFESSIONAL` deverá indicar atividade profissional regular.

O status `FREE_AGENT` deverá indicar que o jogador está sem vínculo com uma
equipe.

O status `LOANED` deverá ser utilizado somente quando a condição de empréstimo
estiver confirmada.

O status `SUSPENDED` poderá representar uma suspensão administrativa ou
esportiva ampla, mas suspensões por partidas deverão preferencialmente utilizar
uma entidade específica.

O status `INJURED` poderá indicar uma indisponibilidade atual, mas lesões deverão
ser armazenadas em uma estrutura histórica própria.

O status `RETIRED` deverá ser compatível com `is_retired = true`.

#### Relacionamentos principais

    Person  1 ─── 0..1 Player

    Player  1 ─── N TeamMembership
    Player  1 ─── N SquadRegistration
    Player  1 ─── N LineupEntry
    Player  1 ─── N MatchEvent
    Player  1 ─── N PlayerStatistic
    Player  1 ─── N Transfer
    Player  1 ─── N Injury
    Player  1 ─── N Suspension

O relacionamento com `Person` será obrigatório.

Nenhuma informação humana básica deverá ser duplicada desnecessariamente em
`Player`.

Dados como nome, data de nascimento, nacionalidade, altura e peso deverão
preferencialmente permanecer em `Person`.

#### Regras de integridade

- `person_id` deverá referenciar uma pessoa existente;
- cada `person_id` deverá possuir no máximo um perfil principal de jogador;
- `primary_position` deverá possuir um valor válido;
- `secondary_position`, quando informada, deverá possuir um valor válido;
- `player_status` deverá possuir um valor válido;
- `professional_debut_date` não poderá estar no futuro;
- `retirement_date`, quando informada, não poderá estar no futuro;
- `retirement_date`, quando informada, deverá ser posterior ou igual à data de
  estreia profissional;
- `market_value`, quando informado, deverá ser maior ou igual a zero;
- `market_value_currency`, quando informada, deverá utilizar um código
  padronizado;
- `is_retired = true` deverá ser compatível com `player_status = RETIRED`;
- `player_status = RETIRED` deverá ser compatível com `is_retired = true`;
- um jogador aposentado poderá permanecer ativo no domínio para consultas
  históricas;
- um jogador não deverá ser removido fisicamente enquanto possuir vínculos,
  estatísticas, eventos ou transferências associadas.

#### Regra inicial de unicidade

A combinação principal de unicidade será:

    person_id

Isso significa que uma mesma pessoa não deverá possuir múltiplos perfis
canônicos equivalentes de jogador.

Uma restrição única deverá existir sobre:

    player.person_id

A identidade esportiva do jogador será derivada da pessoa canônica associada.

Mudanças de:

- equipe;
- posição;
- número de camisa;
- status;
- valor de mercado;
- categoria;
- competição;
- país de atuação;

não deverão criar um novo perfil de jogador.

#### Número de camisa

O número de camisa não deverá ser armazenado diretamente em `Player` como valor
permanente.

Um jogador poderá utilizar números diferentes:

- em equipes diferentes;
- em temporadas diferentes;
- em competições diferentes;
- na seleção;
- em partidas específicas.

O número deverá ser armazenado em estruturas contextuais.

Exemplo para elenco:

    SquadRegistration
    ├── player_id
    ├── team_id
    ├── season_id
    ├── shirt_number
    ├── valid_from
    └── valid_until

Exemplo para partida:

    LineupEntry
    ├── match_id
    ├── player_id
    ├── team_id
    ├── shirt_number
    ├── is_starter
    └── position

O campo `shirt_name` poderá permanecer em `Player`, pois representa o nome
esportivo normalmente utilizado na camisa, e não o número.

#### Equipe atual

A equipe atual não deverá ser armazenada diretamente em `Player` como uma
relação definitiva.

A associação atual deverá ser derivada dos vínculos profissionais.

Exemplo conceitual:

    TeamMembership
    ├── player_id
    ├── team_id
    ├── membership_type
    ├── valid_from
    ├── valid_until
    ├── is_current
    └── status

Essa abordagem permitirá representar:

- transferências;
- empréstimos;
- fim de contrato;
- períodos sem equipe;
- múltiplos vínculos;
- equipes de base;
- equipe principal;
- seleções nacionais;
- histórico completo.

#### Empréstimos

Um empréstimo não deverá substituir o vínculo histórico com a equipe de origem.

O domínio deverá permitir representar simultaneamente:

    equipe detentora dos direitos
    equipe atual por empréstimo

Essa situação poderá utilizar:

    TeamMembership
    Transfer
    Contract

A estrutura definitiva será detalhada em uma seção própria.

O valor `LOANED` em `player_status` deverá ser tratado apenas como resumo do
estado atual, não como fonte completa do vínculo.

#### Aposentadoria

A aposentadoria deverá ser representada por:

    is_retired = true
    player_status = RETIRED

Quando disponível, também deverá ser preenchido:

    retirement_date

A aposentadoria não deverá desativar automaticamente a entidade `Person`.

Uma pessoa aposentada como jogador poderá continuar atuando como:

- treinador;
- auxiliar técnico;
- dirigente;
- comentarista;
- membro de comissão;
- representante institucional.

Exemplo:

    Person
    ├── Player aposentado
    └── Coach ativo

#### Estreia profissional

A data de estreia profissional deverá representar a primeira participação
profissional confirmada.

Ela não deverá ser inferida automaticamente apenas pela data do primeiro
registro recebido de um provider.

A fonte deverá ser conhecida ou possuir nível de confiança adequado.

Caso a data exata não esteja disponível, ela poderá permanecer nula.

Futuramente, poderá existir uma estrutura de marcos de carreira.

Exemplo conceitual:

    PlayerCareerMilestone
    ├── player_id
    ├── milestone_type
    ├── milestone_date
    ├── team_id
    ├── competition_id
    ├── match_id
    ├── source_provider
    └── confidence_score

#### Valor de mercado

O valor de mercado é um dado variável e dependente da fonte.

Por isso, `market_value` não deverá ser considerado um atributo permanente da
identidade do jogador.

Os campos presentes em `Player` poderão representar apenas o valor mais recente
conhecido.

A estrutura histórica recomendada será:

    PlayerMarketValue
    ├── id
    ├── player_id
    ├── value
    ├── currency
    ├── reference_date
    ├── source_provider
    ├── confidence_score
    └── created_at

Essa estrutura permitirá:

- armazenar histórico;
- comparar providers;
- acompanhar valorização;
- alimentar modelos estatísticos;
- preservar a data de referência.

O valor de mercado não deverá ser confundido com:

- salário;
- multa rescisória;
- valor de transferência;
- valor contratual;
- valor pago por empréstimo.

#### Lesões e suspensões

Lesões e suspensões não deverão ser representadas apenas pelo campo
`player_status`.

Elas deverão possuir entidades históricas próprias.

Exemplo de lesão:

    Injury
    ├── player_id
    ├── injury_type
    ├── start_date
    ├── expected_return_date
    ├── actual_return_date
    ├── severity
    ├── status
    └── source_provider

Exemplo de suspensão:

    Suspension
    ├── player_id
    ├── competition_id
    ├── reason
    ├── start_date
    ├── end_date
    ├── matches_count
    ├── status
    └── source_provider

O status atual poderá ser derivado dessas estruturas.

#### Jogadores de categorias de base

Jogadores de base deverão utilizar a mesma entidade `Player`.

Não deverá existir uma identidade separada apenas porque o atleta ainda não é
profissional.

A evolução poderá ocorrer por atualização de:

    player_status
    TeamMembership
    SquadRegistration

Exemplo:

    YOUTH
    PROFESSIONAL

A promoção para a equipe principal não deverá criar um novo jogador.

#### Jogadores sem equipe

Jogadores sem equipe deverão permanecer no domínio.

Nesses casos:

    player_status = FREE_AGENT

A ausência de um vínculo atual não deverá apagar:

- equipes anteriores;
- estatísticas;
- partidas;
- transferências;
- lesões;
- suspensões;
- valor de mercado;
- histórico profissional.

#### Jogadores desconhecidos ou incompletos

Providers poderão fornecer registros incompletos.

Exemplos:

    nome sem data de nascimento
    jogador sem nacionalidade
    jogador sem posição
    identificador externo sem biografia completa

Quando houver informação mínima suficiente, poderá ser criada uma entidade
provisória.

Esses registros deverão possuir:

- origem conhecida;
- identificador externo preservado;
- campos desconhecidos explicitamente representados;
- nível de confiança;
- indicação de necessidade de enriquecimento;
- possibilidade de fusão futura.

O valor `UNKNOWN` deverá ser utilizado apenas quando o dado não puder ser
determinado.

#### Diretrizes de resolução de identidade

A resolução de um jogador deverá começar pela entidade `Person`.

Depois da resolução da pessoa, o sistema deverá localizar ou criar o perfil
`Player` correspondente.

Critérios relevantes:

- nome;
- aliases;
- data de nascimento;
- nacionalidade;
- altura;
- posição;
- pé preferencial;
- equipe atual;
- equipes anteriores;
- número de camisa contextual;
- identificadores externos;
- período de atividade.

Nomes semelhantes não deverão ser suficientes para a associação automática.

Exemplo de risco:

    dois jogadores com o mesmo nome
    dois jogadores da mesma nacionalidade
    dois jogadores nascidos no mesmo ano
    jogador de base e jogador profissional com nomes semelhantes

Associações ambíguas deverão ser encaminhadas para revisão.

#### Estatísticas do jogador

Estatísticas acumuladas não deverão ser armazenadas diretamente em `Player`.

Elas deverão existir em estruturas contextuais.

Exemplo:

    PlayerStatistic
    ├── player_id
    ├── team_id
    ├── competition_id
    ├── season_id
    ├── match_id
    ├── minutes_played
    ├── goals
    ├── assists
    ├── shots
    ├── passes
    ├── tackles
    ├── cards
    └── rating

O contexto poderá variar entre:

- partida;
- rodada;
- fase;
- temporada;
- competição;
- equipe;
- carreira.

A entidade `Player` deverá representar identidade e perfil, não agregações
estatísticas variáveis.

#### Índices recomendados para Player

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ux_player_person_id` | `person_id` | Garantir um perfil principal por pessoa. |
| `ix_player_primary_position` | `primary_position` | Filtrar jogadores pela posição principal. |
| `ix_player_secondary_position` | `secondary_position` | Filtrar jogadores pela posição secundária. |
| `ix_player_status` | `player_status` | Consultar jogadores pelo estado profissional. |
| `ix_player_is_retired` | `is_retired` | Separar jogadores ativos e aposentados. |
| `ix_player_is_active` | `is_active` | Separar perfis ativos e históricos. |
| `ix_player_status_position` | `player_status, primary_position` | Buscar jogadores por estado e posição. |
| `ix_player_active_position` | `is_active, primary_position` | Buscar jogadores ativos por posição. |

O índice mais importante será a restrição única sobre:

    person_id

Índices isolados sobre valores booleanos ou enumerações de baixa cardinalidade
deverão ser avaliados conforme as consultas reais.

Índices compostos ou parciais poderão ser mais adequados.

Exemplo conceitual:

    INDEX ON player (
        primary_position,
        player_status
    )
    WHERE is_active = true

#### Dependências futuras

A entidade `Player` será utilizada por:

- elencos;
- vínculos com equipes;
- escalações;
- bancos de reservas;
- substituições;
- gols;
- assistências;
- cartões;
- pênaltis;
- estatísticas individuais;
- transferências;
- contratos;
- empréstimos;
- lesões;
- suspensões;
- valores de mercado;
- modelos de desempenho;
- probabilidades de escalação;
- análise de disponibilidade;
- previsões de partidas;
- mercados de apostas relacionados a jogadores.

Por isso, o perfil deverá permanecer estável durante toda a carreira do atleta.

---

### 7.4 Coach

A entidade `Coach` representa o perfil profissional de uma pessoa que exerce ou
exerceu funções técnicas relacionadas a uma equipe.

A identidade humana continuará sendo representada por `Person`.

Uma mesma pessoa poderá possuir simultaneamente um perfil de `Player` e um
perfil de `Coach`.

Exemplo:

    Person
    ├── Player
    └── Coach

Esse cenário permitirá representar ex-jogadores que iniciaram carreira como
treinadores sem criar uma nova identidade humana.

#### Responsabilidades

A entidade `Coach` será responsável por:

- representar o perfil profissional de treinador;
- vincular o treinador à identidade humana;
- indicar a função técnica principal;
- armazenar licenças profissionais quando disponíveis;
- registrar o status atual da carreira;
- permitir associação com equipes;
- permitir associação com partidas;
- preservar histórico profissional;
- servir como referência para comissões técnicas.

#### Campos principais

    id
    person_id
    coach_role
    coaching_license
    coach_status
    professional_debut_date
    retirement_date
    is_retired
    is_active
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno do perfil técnico. |
| `person_id` | UUID | Sim | Pessoa canônica associada ao treinador. |
| `coach_role` | enum | Sim | Função técnica principal. |
| `coaching_license` | string | Não | Licença técnica conhecida. |
| `coach_status` | enum | Sim | Situação profissional atual. |
| `professional_debut_date` | date | Não | Primeira atuação profissional conhecida como treinador. |
| `retirement_date` | date | Não | Data de aposentadoria como treinador. |
| `is_retired` | boolean | Sim | Indica aposentadoria da carreira técnica. |
| `is_active` | boolean | Sim | Indica se o perfil permanece ativo. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Funções técnicas previstas

    HEAD_COACH
    ASSISTANT_COACH
    GOALKEEPER_COACH
    FITNESS_COACH
    TECHNICAL_DIRECTOR
    INTERIM_COACH
    YOUTH_COACH
    OTHER
    UNKNOWN

A função principal representa apenas o perfil predominante da carreira.

Mudanças de função ao longo do tempo deverão ser registradas em vínculos
históricos com equipes.

#### Status profissionais previstos

    ACTIVE
    UNEMPLOYED
    SUSPENDED
    RETIRED
    INACTIVE
    UNKNOWN

O status representa apenas um resumo da situação atual.

Mudanças de equipe, licenças ou afastamentos deverão possuir registros
históricos próprios.

#### Relacionamentos principais

    Person 1 ─── 0..1 Coach

    Coach 1 ─── N TeamMembership
    Coach 1 ─── N Match
    Coach 1 ─── N TechnicalStaffMembership

O relacionamento com `Person` será obrigatório.

#### Regras de integridade

- `person_id` deverá referenciar uma pessoa existente;
- deverá existir no máximo um perfil principal de treinador por pessoa;
- `coach_role` deverá possuir valor válido;
- `coach_status` deverá possuir valor válido;
- `professional_debut_date` não poderá estar no futuro;
- `retirement_date`, quando informada, deverá ser posterior à estreia;
- `is_retired = true` deverá ser compatível com `coach_status = RETIRED`;
- treinadores históricos não deverão ser removidos fisicamente.

#### Regra inicial de unicidade

A identidade do treinador será derivada da pessoa.

Deverá existir uma restrição única sobre:

    coach.person_id

Mudanças de:

- equipe;
- competição;
- cargo;
- licença;
- situação profissional;

não deverão gerar um novo perfil de treinador.

#### Licenças técnicas

Alguns providers poderão informar certificações emitidas por entidades como:

- UEFA
- CONMEBOL
- CBF
- FIFA
- Federações nacionais

Inicialmente a licença poderá ser armazenada apenas como texto.

No futuro, poderá existir uma estrutura específica:

    CoachingLicense
    ├── coach_id
    ├── license_type
    ├── issuing_authority
    ├── issue_date
    ├── expiration_date
    └── status

#### Histórico profissional

A equipe atual não deverá ser armazenada diretamente em `Coach`.

O vínculo deverá ser derivado de registros históricos.

Exemplo conceitual:

    TechnicalStaffMembership
    ├── coach_id
    ├── team_id
    ├── role
    ├── valid_from
    ├── valid_until
    ├── is_current
    └── status

Isso permitirá representar:

- mudanças de equipe;
- promoções;
- treinadores interinos;
- retorno ao clube;
- múltiplas passagens.

#### Relação com Player

Um treinador poderá possuir histórico como jogador.

Exemplo:

    Person
    ├── Player
    └── Coach

A existência de um perfil `Player` não será obrigatória.

Da mesma forma, um treinador poderá nunca ter atuado profissionalmente como
jogador.

#### Estatísticas do treinador

Estatísticas não deverão ser armazenadas diretamente em `Coach`.

Elas deverão ser derivadas de partidas e temporadas.

Exemplos:

- partidas comandadas;
- vitórias;
- empates;
- derrotas;
- aproveitamento;
- títulos;
- média de gols;
- sequência invicta.

Esses dados deverão ser calculados ou armazenados em estruturas próprias.

#### Índices recomendados para Coach

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ux_coach_person_id` | `person_id` | Garantir um único perfil por pessoa. |
| `ix_coach_role` | `coach_role` | Buscar treinadores por função. |
| `ix_coach_status` | `coach_status` | Filtrar pelo status profissional. |
| `ix_coach_is_active` | `is_active` | Separar perfis ativos e históricos. |
| `ix_coach_role_status` | `coach_role, coach_status` | Consultas combinadas. |

O índice mais importante será:

    person_id

#### Dependências futuras

A entidade `Coach` será utilizada por:

- partidas;
- equipes;
- comissões técnicas;
- temporadas;
- competições;
- estatísticas;
- histórico profissional;
- mudanças de treinador;
- modelos de desempenho de equipes;
- análises de impacto técnico.

Assim como `Player`, o perfil `Coach` deverá permanecer estável durante toda a
carreira da pessoa.

---

### 7.5 Referee

A entidade `Referee` representa o perfil profissional de uma pessoa que exerce
ou exerceu funções relacionadas à arbitragem no futebol.

A identidade humana continuará sendo representada por `Person`.

A entidade `Referee` deverá armazenar somente informações específicas da
carreira de arbitragem.

Exemplo conceitual:

    Person
    └── Referee

Uma pessoa deverá possuir no máximo um perfil canônico principal de árbitro.

Mudanças de função, federação, competição, categoria ou situação profissional
não deverão criar novos registros de `Referee`.

#### Responsabilidades

A entidade `Referee` será responsável por:

- representar o perfil profissional de arbitragem;
- vincular o árbitro à identidade humana canônica;
- indicar sua função principal;
- registrar sua categoria profissional;
- armazenar a federação ou associação principal;
- indicar seu status profissional atual;
- registrar datas relevantes da carreira;
- permitir associação com partidas;
- permitir associação com eventos disciplinares;
- preservar o histórico profissional;
- servir como referência para análises de arbitragem.

#### Campos principais

    id
    person_id
    primary_role
    referee_category
    federation_name
    international_badge
    referee_status
    professional_debut_date
    international_debut_date
    retirement_date
    is_international
    is_retired
    is_active
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno e canônico do perfil de arbitragem. |
| `person_id` | UUID | Sim | Pessoa canônica associada ao árbitro. |
| `primary_role` | enum | Sim | Função principal exercida na arbitragem. |
| `referee_category` | enum | Não | Categoria ou nível profissional conhecido. |
| `federation_name` | string | Não | Federação ou associação principal relacionada ao árbitro. |
| `international_badge` | string | Não | Identificação de certificação internacional, quando disponível. |
| `referee_status` | enum | Sim | Situação profissional atual. |
| `professional_debut_date` | date | Não | Data conhecida da estreia profissional. |
| `international_debut_date` | date | Não | Data conhecida da estreia internacional. |
| `retirement_date` | date | Não | Data conhecida da aposentadoria. |
| `is_international` | boolean | Sim | Indica atuação reconhecida em âmbito internacional. |
| `is_retired` | boolean | Sim | Indica aposentadoria da carreira de arbitragem. |
| `is_active` | boolean | Sim | Indica se o perfil permanece ativo no domínio. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Funções de arbitragem previstas

    MAIN_REFEREE
    ASSISTANT_REFEREE
    FOURTH_OFFICIAL
    VIDEO_ASSISTANT_REFEREE
    ASSISTANT_VIDEO_ASSISTANT_REFEREE
    ADDITIONAL_ASSISTANT_REFEREE
    RESERVE_ASSISTANT_REFEREE
    REFEREE_OBSERVER
    OTHER
    UNKNOWN

O valor `MAIN_REFEREE` deverá representar o árbitro principal da partida.

O valor `ASSISTANT_REFEREE` deverá representar os assistentes de campo.

O valor `FOURTH_OFFICIAL` deverá representar o quarto árbitro.

O valor `VIDEO_ASSISTANT_REFEREE` deverá representar o árbitro responsável pelo
VAR.

O valor `ASSISTANT_VIDEO_ASSISTANT_REFEREE` deverá representar o auxiliar do
VAR.

A função principal deverá representar o papel predominante na carreira.

Funções exercidas em partidas específicas deverão ser registradas no contexto
da partida.

#### Categorias profissionais previstas

    LOCAL
    REGIONAL
    NATIONAL
    CONTINENTAL
    INTERNATIONAL
    ELITE
    AMATEUR
    OTHER
    UNKNOWN

A categoria deverá representar o nível profissional conhecido do árbitro.

O valor `INTERNATIONAL` deverá ser utilizado quando existir reconhecimento
internacional confirmado.

O valor `ELITE` poderá ser utilizado para categorias superiores oficialmente
definidas por uma organização esportiva.

A categoria não deverá ser inferida apenas pela competição em que o árbitro
atuou.

#### Status profissionais previstos

    ACTIVE
    INACTIVE
    SUSPENDED
    TEMPORARILY_UNAVAILABLE
    RETIRED
    UNKNOWN

O status `ACTIVE` deverá indicar que o árbitro está em atividade.

O status `INACTIVE` poderá indicar ausência de atuação atual sem aposentadoria
confirmada.

O status `SUSPENDED` deverá indicar impedimento disciplinar ou administrativo.

O status `TEMPORARILY_UNAVAILABLE` poderá representar afastamento temporário.

O status `RETIRED` deverá ser compatível com `is_retired = true`.

#### Relacionamentos principais

    Person 1 ─── 0..1 Referee

    Referee 1 ─── N MatchOfficial
    Referee 1 ─── N MatchEvent
    Referee 1 ─── N RefereeAssignment
    Referee 1 ─── N RefereeStatistic
    Referee 1 ─── N DisciplinaryRecord

O relacionamento com `Person` será obrigatório.

Uma partida poderá possuir múltiplos árbitros, cada um com uma função
específica.

Por isso, a associação entre partida e árbitro deverá utilizar uma entidade
intermediária.

Exemplo:

    Match
    └── MatchOfficial
        ├── referee_id
        ├── official_role
        ├── sequence
        └── source_provider

#### Regras de integridade

- `person_id` deverá referenciar uma pessoa existente;
- cada `person_id` deverá possuir no máximo um perfil principal de árbitro;
- `primary_role` deverá possuir um valor válido;
- `referee_category`, quando informada, deverá possuir um valor válido;
- `referee_status` deverá possuir um valor válido;
- `professional_debut_date` não poderá estar no futuro;
- `international_debut_date` não poderá estar no futuro;
- `retirement_date`, quando informada, não poderá estar no futuro;
- `retirement_date`, quando informada, deverá ser posterior ou igual à estreia
  profissional;
- `international_debut_date`, quando informada, deverá ser posterior ou igual à
  estreia profissional;
- `is_international = true` deverá possuir evidência confiável;
- `is_retired = true` deverá ser compatível com `referee_status = RETIRED`;
- `referee_status = RETIRED` deverá ser compatível com `is_retired = true`;
- árbitros históricos não deverão ser removidos fisicamente;
- um árbitro não deverá ser removido enquanto possuir partidas ou registros
  associados.

#### Regra inicial de unicidade

A identidade profissional do árbitro será derivada da pessoa canônica.

Deverá existir uma restrição única sobre:

    referee.person_id

Mudanças de:

- federação;
- categoria;
- função;
- competição;
- país de atuação;
- certificação;
- status profissional;

não deverão gerar um novo perfil de árbitro.

#### Função principal e função na partida

A função principal armazenada em `Referee` representa a atividade predominante
da carreira.

Ela não deverá substituir a função exercida em uma partida específica.

Exemplo:

    Referee.primary_role = MAIN_REFEREE

Em uma determinada partida, a mesma pessoa poderá atuar como:

    MatchOfficial.official_role = VIDEO_ASSISTANT_REFEREE

A função da partida deverá sempre ser registrada em `MatchOfficial`.

Isso permitirá representar mudanças de função ao longo do tempo.

#### Associação com federações

O campo `federation_name` poderá ser utilizado inicialmente para armazenar a
organização principal relacionada ao árbitro.

Exemplos:

    CBF
    CONMEBOL
    UEFA
    FIFA
    Federação Paulista de Futebol

Entretanto, o campo textual não deverá ser considerado uma relação canônica
definitiva.

Futuramente, poderá existir uma entidade específica.

Exemplo conceitual:

    SportsFederation
    ├── id
    ├── country_id
    ├── name
    ├── normalized_name
    ├── federation_type
    └── is_active

O histórico de vínculos poderá utilizar:

    RefereeFederationMembership
    ├── referee_id
    ├── federation_id
    ├── valid_from
    ├── valid_until
    ├── membership_status
    └── is_current

Essa estrutura permitirá representar mudanças de federação e múltiplas
associações.

#### Certificações internacionais

Certificações ou distintivos internacionais não deverão ser armazenados apenas
como um estado permanente.

O campo `international_badge` poderá representar temporariamente a certificação
atual conhecida.

Futuramente, deverá existir uma estrutura histórica.

Exemplo conceitual:

    RefereeCertification
    ├── id
    ├── referee_id
    ├── certification_type
    ├── issuing_authority
    ├── issue_date
    ├── expiration_date
    ├── status
    └── source_provider

Isso permitirá preservar:

- certificações anteriores;
- renovações;
- expirações;
- suspensões;
- diferentes entidades emissoras;
- níveis profissionais.

#### Nomeação para partidas

A nomeação de árbitros deverá ser registrada por partida.

Exemplo conceitual:

    MatchOfficial
    ├── id
    ├── match_id
    ├── referee_id
    ├── official_role
    ├── sequence
    ├── appointment_status
    ├── appointed_at
    ├── confirmed_at
    ├── replaced_referee_id
    ├── source_provider
    └── created_at

Essa estrutura permitirá representar:

- árbitro principal;
- assistentes;
- quarto árbitro;
- equipe de VAR;
- substituições de última hora;
- nomeações provisórias;
- nomeações confirmadas;
- diferentes sequências de assistentes.

#### Status de nomeação previstos

    APPOINTED
    CONFIRMED
    REPLACED
    CANCELLED
    COMPLETED
    UNKNOWN

O status de nomeação pertence à relação entre árbitro e partida.

Ele não deverá ser armazenado em `Referee`.

#### Árbitro substituído

Em alguns casos, um árbitro inicialmente nomeado poderá ser substituído antes da
partida.

A nomeação original deverá ser preservada.

Exemplo:

    árbitro A nomeado
    árbitro A substituído
    árbitro B confirmado

A estrutura deverá permitir consultar:

- quem foi inicialmente nomeado;
- quem realizou a partida;
- quando ocorreu a substituição;
- motivo conhecido;
- provider que informou a alteração.

#### Eventos da partida

Cartões, expulsões, pênaltis e outras decisões poderão estar relacionados ao
árbitro principal da partida.

Entretanto, os eventos não deverão duplicar o perfil do árbitro.

O vínculo deverá ocorrer por meio de:

    match_official_id

ou:

    referee_id

A escolha definitiva dependerá do nível de detalhamento disponível.

A referência a `MatchOfficial` será mais precisa, pois preservará a função
exercida na partida.

#### Estatísticas do árbitro

Estatísticas acumuladas não deverão ser armazenadas diretamente em `Referee`.

Elas deverão ser derivadas ou armazenadas em estruturas contextuais.

Exemplo conceitual:

    RefereeStatistic
    ├── id
    ├── referee_id
    ├── competition_id
    ├── season_id
    ├── team_id
    ├── match_count
    ├── yellow_cards
    ├── red_cards
    ├── penalties_awarded
    ├── fouls_called
    ├── home_wins
    ├── draws
    ├── away_wins
    └── calculated_at

As estatísticas poderão ser calculadas por:

- partida;
- temporada;
- competição;
- país;
- equipe;
- período;
- função de arbitragem.

A entidade `Referee` deverá representar identidade e perfil profissional, não
agregações estatísticas.

#### Uso analítico em apostas

Dados de arbitragem poderão ser relevantes para análises como:

- média de cartões;
- média de faltas;
- frequência de pênaltis;
- tendência de cartões por equipe;
- diferença entre mandantes e visitantes;
- comportamento por competição;
- impacto de jogos decisivos;
- padrão disciplinar histórico.

Esses indicadores não deverão ser utilizados isoladamente.

Eles deverão considerar:

- tamanho da amostra;
- competição;
- temporada;
- estilo das equipes;
- contexto da partida;
- mudança de regulamentos;
- função exercida pelo árbitro;
- qualidade e origem dos dados.

O sistema deverá evitar conclusões determinísticas baseadas apenas no histórico
do árbitro.

#### Suspensões e afastamentos

Suspensões e afastamentos não deverão ser representados apenas pelo
`referee_status`.

Eles deverão possuir uma estrutura histórica própria.

Exemplo conceitual:

    RefereeAvailability
    ├── id
    ├── referee_id
    ├── availability_type
    ├── reason
    ├── start_date
    ├── expected_end_date
    ├── actual_end_date
    ├── status
    ├── source_provider
    └── created_at

Tipos possíveis:

    SUSPENSION
    INJURY
    ADMINISTRATIVE_LEAVE
    PERSONAL_LEAVE
    TEMPORARY_UNAVAILABILITY
    OTHER

O status atual poderá ser derivado dos registros de disponibilidade.

#### Aposentadoria

A aposentadoria deverá ser representada por:

    is_retired = true
    referee_status = RETIRED

Quando conhecida, também deverá ser preenchida:

    retirement_date

A aposentadoria como árbitro não deverá desativar automaticamente a entidade
`Person`.

A pessoa poderá continuar atuando como:

- observador de arbitragem;
- instrutor;
- dirigente;
- analista;
- membro de comissão;
- representante de federação.

#### Árbitros com múltiplas funções

Uma pessoa poderá exercer diferentes funções de arbitragem durante sua carreira.

Exemplo:

    assistente de arbitragem
    árbitro principal
    árbitro de vídeo
    observador

A primeira versão poderá armazenar apenas `primary_role`.

Futuramente, poderá existir uma estrutura histórica.

Exemplo conceitual:

    RefereeRoleHistory
    ├── id
    ├── referee_id
    ├── role
    ├── valid_from
    ├── valid_until
    ├── is_primary
    ├── source_provider
    └── created_at

Isso permitirá representar corretamente a evolução profissional.

#### Registros incompletos

Providers poderão fornecer informações limitadas.

Exemplos:

    nome sem data de nascimento
    árbitro sem nacionalidade
    função desconhecida
    federação não informada
    apenas identificador externo

A resolução deverá começar pela entidade `Person`.

Quando houver informação mínima suficiente, poderá ser criado um perfil
provisório de `Referee`.

Esses registros deverão preservar:

- provider de origem;
- identificador externo;
- nível de confiança;
- campos desconhecidos;
- necessidade de enriquecimento;
- possibilidade de fusão futura.

#### Diretrizes de resolução de identidade

A resolução de identidade deverá considerar:

- nome completo;
- aliases;
- data de nascimento;
- nacionalidade;
- país de atuação;
- federação;
- função principal;
- categoria;
- competições em que atuou;
- período de atividade;
- identificadores externos.

A similaridade textual isolada não deverá ser suficiente.

Exemplo de risco:

    árbitros com nomes iguais
    nomes abreviados
    diferenças de transliteração
    ausência de data de nascimento
    providers que informam apenas sobrenomes

Associações ambíguas deverão ser encaminhadas para revisão manual.

#### Índices recomendados para Referee

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ux_referee_person_id` | `person_id` | Garantir um único perfil por pessoa. |
| `ix_referee_primary_role` | `primary_role` | Filtrar árbitros pela função principal. |
| `ix_referee_category` | `referee_category` | Filtrar pela categoria profissional. |
| `ix_referee_status` | `referee_status` | Consultar árbitros pelo status. |
| `ix_referee_federation_name` | `federation_name` | Buscar árbitros pela federação informada. |
| `ix_referee_is_international` | `is_international` | Localizar árbitros internacionais. |
| `ix_referee_is_retired` | `is_retired` | Separar árbitros ativos e aposentados. |
| `ix_referee_is_active` | `is_active` | Separar perfis ativos e históricos. |
| `ix_referee_role_status` | `primary_role, referee_status` | Consultar função e status conjuntamente. |
| `ix_referee_category_status` | `referee_category, referee_status` | Consultar categoria e status conjuntamente. |

O índice mais importante será a restrição única sobre:

    person_id

Índices simples em colunas booleanas ou enums de baixa cardinalidade deverão ser
avaliados conforme as consultas reais.

Índices compostos ou parciais poderão ser mais adequados.

Exemplo conceitual:

    INDEX ON referee (
        primary_role,
        referee_category
    )
    WHERE is_active = true

#### Dependências futuras

A entidade `Referee` será utilizada por:

- partidas;
- nomeações de arbitragem;
- equipes de VAR;
- eventos disciplinares;
- cartões;
- pênaltis;
- estatísticas;
- suspensões;
- análises de comportamento;
- modelos estatísticos;
- previsões relacionadas a cartões;
- mercados de apostas disciplinares;
- histórico de competições;
- auditoria de dados esportivos.

Por isso, o perfil deverá permanecer estável durante toda a carreira de
arbitragem da pessoa.
---

### 7.6 TeamMembership

A entidade `TeamMembership` representa um vínculo histórico entre uma pessoa e
uma equipe.

Ela deverá ser utilizada para registrar relações profissionais, esportivas ou
institucionais que possuam duração temporal.

Exemplos:

    jogador vinculado a um clube
    jogador convocado para uma seleção
    treinador contratado por uma equipe
    auxiliar técnico integrante de uma comissão
    jogador emprestado a outro clube
    atleta promovido da base para o time principal
    profissional temporariamente afastado
    jogador sem vínculo após o encerramento do contrato

A entidade não deverá representar apenas a equipe atual.

Ela deverá preservar todo o histórico de vínculos da pessoa.

#### Responsabilidades

A entidade `TeamMembership` será responsável por:

- relacionar uma pessoa a uma equipe;
- indicar a função exercida no vínculo;
- preservar datas de início e encerramento;
- representar vínculos atuais e históricos;
- indicar o tipo de vínculo;
- registrar empréstimos;
- registrar convocações para seleções;
- representar equipes principais e de base;
- permitir múltiplos vínculos simultâneos;
- preservar a origem dos dados;
- servir como base para reconstrução da carreira;
- apoiar consultas de disponibilidade e pertencimento.

#### Campos principais

    id
    person_id
    team_id
    player_id
    coach_id
    membership_role
    membership_type
    membership_status
    squad_category
    valid_from
    valid_until
    joined_at
    left_at
    is_current
    is_primary
    is_on_loan
    parent_team_id
    loan_origin_team_id
    source_provider
    confidence_score
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno e canônico do vínculo. |
| `person_id` | UUID | Sim | Pessoa canônica relacionada à equipe. |
| `team_id` | UUID | Sim | Equipe associada ao vínculo. |
| `player_id` | UUID | Não | Perfil de jogador, quando aplicável. |
| `coach_id` | UUID | Não | Perfil de treinador, quando aplicável. |
| `membership_role` | enum | Sim | Função exercida pela pessoa na equipe. |
| `membership_type` | enum | Sim | Natureza estrutural do vínculo. |
| `membership_status` | enum | Sim | Situação atual ou histórica do vínculo. |
| `squad_category` | enum | Não | Categoria esportiva do grupo ou elenco. |
| `valid_from` | date | Não | Início da validade histórica do vínculo. |
| `valid_until` | date | Não | Final da validade histórica do vínculo. |
| `joined_at` | datetime UTC | Não | Momento conhecido da entrada na equipe. |
| `left_at` | datetime UTC | Não | Momento conhecido da saída da equipe. |
| `is_current` | boolean | Sim | Indica se o vínculo está vigente. |
| `is_primary` | boolean | Sim | Indica se este é o vínculo principal da pessoa. |
| `is_on_loan` | boolean | Sim | Indica se o vínculo ocorre por empréstimo. |
| `parent_team_id` | UUID | Não | Equipe principal à qual a equipe vinculada pertence. |
| `loan_origin_team_id` | UUID | Não | Equipe de origem em caso de empréstimo. |
| `source_provider` | string | Não | Provider que originou ou confirmou o vínculo. |
| `confidence_score` | decimal | Não | Nível de confiança atribuído ao registro. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Funções de vínculo previstas

    PLAYER
    HEAD_COACH
    ASSISTANT_COACH
    GOALKEEPER_COACH
    FITNESS_COACH
    TECHNICAL_DIRECTOR
    MEDICAL_STAFF
    ANALYST
    SCOUT
    TEAM_MANAGER
    STAFF_MEMBER
    OTHER
    UNKNOWN

O valor `PLAYER` deverá ser utilizado para atletas vinculados à equipe.

As funções de treinador deverão ser compatíveis com o perfil `Coach`.

Funções como `MEDICAL_STAFF`, `ANALYST` e `SCOUT` poderão existir mesmo quando
não houver um perfil profissional especializado no domínio.

A criação de perfis adicionais poderá ocorrer futuramente, sem alterar o
histórico existente em `TeamMembership`.

Árbitros não deverão utilizar `TeamMembership` para representar sua atuação
normal em partidas.

A relação de árbitros deverá ocorrer por meio de entidades como:

    RefereeAssignment
    MatchOfficial
    RefereeFederationMembership

Um árbitro somente poderá possuir `TeamMembership` em uma situação excepcional
na qual também exerça uma função interna real em uma equipe, como analista,
instrutor ou membro administrativo.

#### Tipos de vínculo previstos

    PERMANENT
    TEMPORARY
    LOAN
    YOUTH
    RESERVE
    NATIONAL_TEAM_CALLUP
    TRIAL
    SHORT_TERM
    VOLUNTEER
    ADMINISTRATIVE
    OTHER
    UNKNOWN

O valor `PERMANENT` deverá indicar um vínculo regular sem prazo temporário
conhecido.

O valor `TEMPORARY` deverá indicar uma relação limitada no tempo.

O valor `LOAN` deverá indicar vínculo por empréstimo.

O valor `YOUTH` deverá representar vínculo com equipe de formação.

O valor `RESERVE` deverá representar vínculo com equipe secundária.

O valor `NATIONAL_TEAM_CALLUP` deverá representar convocação para seleção.

O valor `TRIAL` deverá indicar período de avaliação.

O valor `SHORT_TERM` deverá representar vínculos de curta duração.

#### Status de vínculo previstos

    PLANNED
    ACTIVE
    SUSPENDED
    INACTIVE
    COMPLETED
    TERMINATED
    CANCELLED
    EXPIRED
    UNKNOWN

O status `PLANNED` poderá ser utilizado para vínculos confirmados com início
futuro.

O status `ACTIVE` deverá indicar vínculo vigente.

O status `SUSPENDED` deverá indicar interrupção temporária.

O status `COMPLETED` deverá representar encerramento regular.

O status `TERMINATED` deverá indicar encerramento antecipado.

O status `CANCELLED` deverá representar vínculo cancelado antes de produzir
efeitos.

O status `EXPIRED` deverá indicar término automático pelo fim do período de
validade.

#### Categorias de elenco previstas

    FIRST_TEAM
    RESERVE_TEAM
    U23
    U21
    U20
    U19
    U18
    U17
    U16
    U15
    YOUTH
    WOMEN_FIRST_TEAM
    WOMEN_YOUTH
    NATIONAL_SENIOR
    NATIONAL_YOUTH
    OTHER
    UNKNOWN

A categoria de elenco deverá representar o grupo esportivo em que a pessoa está
inserida.

Ela não deverá substituir a identidade da equipe.

Quando houver uma entidade `Team` específica para a categoria, o vínculo deverá
referenciar diretamente essa equipe.

Exemplo:

    Barcelona
    Barcelona B
    Barcelona U19
    Barcelona Feminino

Cada uma dessas equipes poderá possuir sua própria identidade canônica.

#### Relacionamentos principais

    Person 1 ─── N TeamMembership
    Team   1 ─── N TeamMembership

    Player 0..1 ─── N TeamMembership
    Coach  0..1 ─── N TeamMembership

    TeamMembership N ─── 0..1 Team como equipe principal
    TeamMembership N ─── 0..1 Team como origem do empréstimo

O relacionamento obrigatório deverá ocorrer por meio de:

    person_id
    team_id

Os campos `player_id` e `coach_id` poderão ser utilizados para facilitar
consultas específicas, mas deverão permanecer compatíveis com `person_id`.

#### Uso de person_id e perfis especializados

`person_id` será a referência humana principal.

`player_id` deverá ser preenchido quando:

    membership_role = PLAYER

`coach_id` deverá ser preenchido quando a função estiver relacionada à carreira
técnica.

Exemplos:

    HEAD_COACH
    ASSISTANT_COACH
    GOALKEEPER_COACH
    FITNESS_COACH

A aplicação deverá validar que:

    player.person_id = team_membership.person_id

e:

    coach.person_id = team_membership.person_id

O vínculo não poderá relacionar uma pessoa e um perfil pertencente a outra
pessoa.

#### Regras de integridade

- `person_id` deverá referenciar uma pessoa existente;
- `team_id` deverá referenciar uma equipe existente;
- `membership_role` deverá possuir um valor válido;
- `membership_type` deverá possuir um valor válido;
- `membership_status` deverá possuir um valor válido;
- `squad_category`, quando informada, deverá possuir um valor válido;
- `valid_until`, quando informada, deverá ser posterior ou igual a
  `valid_from`;
- `left_at`, quando informado, deverá ser posterior ou igual a `joined_at`;
- `is_current = true` deverá ser compatível com um status vigente;
- `is_current = false` deverá ser compatível com vínculo encerrado, suspenso ou
  futuro;
- `is_on_loan = true` deverá ser compatível com `membership_type = LOAN`;
- `membership_type = LOAN` deverá ser compatível com `is_on_loan = true`;
- `loan_origin_team_id` deverá ser informado quando a origem do empréstimo for
  conhecida;
- `loan_origin_team_id` não poderá ser igual a `team_id`;
- `parent_team_id` não poderá ser igual a `team_id`;
- `player_id`, quando informado, deverá pertencer à mesma pessoa;
- `coach_id`, quando informado, deverá pertencer à mesma pessoa;
- vínculos históricos não deverão ser removidos fisicamente;
- vínculos conflitantes deverão ser sinalizados para revisão;
- o encerramento de um vínculo não deverá apagar partidas, estatísticas ou
  registros associados.

#### Regra inicial de unicidade

Não deverá existir uma restrição simples baseada apenas em:

    person_id
    team_id

Uma pessoa poderá possuir múltiplos vínculos com a mesma equipe em períodos
diferentes.

Exemplo:

    jogador contratado em 2015
    jogador transferido em 2018
    jogador retornou em 2022

Também poderá exercer funções diferentes na mesma organização.

Exemplo:

    Player
    Coach

Uma combinação candidata será:

    person_id
    team_id
    membership_role
    valid_from

Quando `valid_from` não estiver disponível, a resolução de duplicidade deverá
considerar:

- provider;
- identificador externo;
- tipo do vínculo;
- status;
- período conhecido;
- perfil especializado;
- nível de confiança.

#### Vínculos atuais

O campo `is_current` deverá permitir consultas rápidas.

Entretanto, ele deverá ser compatível com as datas e o status.

Exemplo de vínculo atual:

    valid_from preenchido
    valid_until nulo
    membership_status = ACTIVE
    is_current = true

Exemplo de vínculo encerrado:

    valid_from preenchido
    valid_until preenchido
    membership_status = COMPLETED
    is_current = false

O campo `is_current` poderá ser derivado, mas poderá permanecer armazenado para
otimizar consultas.

Nesse caso, deverá existir uma rotina de validação para evitar inconsistências.

#### Múltiplos vínculos simultâneos

Uma pessoa poderá possuir mais de um vínculo ativo.

Exemplos:

    jogador vinculado ao clube
    jogador convocado para a seleção

    treinador de clube
    membro temporário de uma comissão nacional

    jogador contratado por uma equipe
    jogador emprestado a outra equipe

Portanto, não deverá existir uma restrição global garantindo apenas um vínculo
ativo por pessoa.

A unicidade de vínculo atual deverá considerar o contexto.

#### Vínculo principal

O campo `is_primary` poderá indicar o vínculo profissional predominante.

Exemplo:

    clube atual = vínculo principal
    seleção nacional = vínculo secundário temporário

Um jogador emprestado poderá possuir:

    equipe de destino = vínculo esportivo principal atual
    equipe de origem = vínculo contratual preservado

A interpretação definitiva de `is_primary` deverá ser documentada nos serviços
de domínio.

Não deverá existir mais de um vínculo principal ativo para o mesmo contexto
profissional, salvo exceções formalmente tratadas.

#### Convocações para seleções

Convocações para seleções não deverão substituir o vínculo com o clube.

Exemplo:

    vínculo com clube:
        membership_type = PERMANENT
        is_current = true

    vínculo com seleção:
        membership_type = NATIONAL_TEAM_CALLUP
        is_current = true

A convocação poderá possuir duração curta.

Quando possível, deverão ser registrados:

    valid_from
    valid_until

Convocações individuais também poderão ser representadas futuramente por uma
entidade específica.

Exemplo conceitual:

    NationalTeamCallup
    ├── player_id
    ├── team_id
    ├── competition_id
    ├── callup_date
    ├── release_date
    ├── status
    └── source_provider

`TeamMembership` deverá representar o vínculo geral, enquanto
`NationalTeamCallup` poderá representar cada convocação específica.

#### Empréstimos

Um empréstimo deverá preservar pelo menos:

    jogador
    equipe de destino
    equipe de origem
    data de início
    data de encerramento
    status

Exemplo:

    person_id = jogador
    team_id = equipe de destino
    membership_type = LOAN
    is_on_loan = true
    loan_origin_team_id = equipe de origem

O vínculo com a equipe de origem não deverá ser automaticamente excluído.

A equipe de origem poderá continuar associada por meio de:

- vínculo contratual;
- contrato;
- transferência;
- registro de direitos esportivos.

A equipe de destino deverá representar onde o jogador está atuando durante o
empréstimo.

#### Promoção entre categorias

A promoção de um atleta não deverá criar uma nova pessoa ou um novo perfil de
jogador.

Ela deverá resultar em novos vínculos ou atualização do contexto esportivo.

Exemplo:

    equipe sub-20
    equipe principal

Caso as categorias sejam representadas por entidades `Team` distintas, deverão
existir vínculos separados.

Exemplo:

    TeamMembership com Flamengo U20
    TeamMembership com Flamengo

O vínculo anterior poderá permanecer ativo caso o jogador continue elegível
para ambas as equipes.

#### Equipes reservas

Equipes reservas deverão possuir identidade própria quando participarem de
competições independentes.

Exemplo:

    Bayern München
    Bayern München II

Nesse caso, o jogador poderá possuir vínculos simultâneos com as duas equipes.

A movimentação entre equipe principal e reserva não deverá criar novo perfil de
jogador.

#### Treinadores interinos

Treinadores interinos deverão ser representados com:

    membership_role = HEAD_COACH
    membership_type = TEMPORARY

ou por uma função específica no contexto histórico.

A condição de interino poderá ser registrada em uma futura entidade de função.

Exemplo conceitual:

    TechnicalStaffMembership
    ├── coach_id
    ├── team_id
    ├── role
    ├── appointment_type
    ├── valid_from
    ├── valid_until
    └── is_current

Valor possível:

    appointment_type = INTERIM

#### Suspensão do vínculo

Uma suspensão não deverá encerrar automaticamente o vínculo.

Exemplo:

    membership_status = SUSPENDED
    is_current = true

Isso poderá ocorrer em:

- suspensões disciplinares;
- afastamentos administrativos;
- licenças;
- indisponibilidade temporária;
- conflitos contratuais.

O motivo da suspensão deverá ser armazenado em estrutura própria quando houver
necessidade de histórico detalhado.

#### Encerramento do vínculo

O encerramento deverá atualizar:

    valid_until
    left_at
    membership_status
    is_current

Exemplo:

    membership_status = COMPLETED
    is_current = false

O encerramento não deverá excluir o registro.

A permanência histórica será necessária para:

- reconstrução de carreira;
- estatísticas;
- escalações;
- transferências;
- contratos;
- análises por equipe;
- auditoria de dados.

#### Sobreposição de períodos

Sobreposições poderão ser legítimas ou indicar erro.

Exemplos legítimos:

    clube e seleção
    equipe principal e equipe sub-20
    vínculo contratual e empréstimo
    múltiplas funções na mesma equipe

Exemplos potencialmente conflitantes:

    dois clubes diferentes como vínculo principal permanente
    no mesmo período

    dois empréstimos simultâneos incompatíveis

    duas funções idênticas ativas na mesma equipe
    com períodos duplicados

A validação deverá considerar:

- função;
- tipo de vínculo;
- equipe;
- categoria;
- datas;
- condição de empréstimo;
- vínculo principal;
- provider;
- confiança.

#### Origem e confiança do vínculo

O campo `source_provider` poderá armazenar temporariamente a origem principal.

A arquitetura definitiva deverá utilizar estruturas próprias de proveniência.

Exemplo conceitual:

    EntitySource
    ├── entity_type
    ├── entity_id
    ├── provider
    ├── external_id
    ├── observed_at
    ├── confidence_score
    └── raw_reference

O `confidence_score` poderá variar conceitualmente entre:

    0.0
    1.0

Exemplo:

    1.0 = confirmação oficial
    0.8 = provider confiável
    0.5 = informação parcial
    0.2 = associação incerta

O nível de confiança não deverá substituir a preservação da fonte.

#### Resolução de duplicidade

Providers diferentes poderão informar o mesmo vínculo de formas distintas.

Exemplo:

    início em 01/07/2025
    início em 02/07/2025
    início informado apenas como julho de 2025
    vínculo sem data de início

A fusão deverá considerar:

- mesma pessoa;
- mesma equipe;
- mesma função;
- mesmo tipo de vínculo;
- períodos compatíveis;
- identificadores externos;
- status;
- origem;
- confiança.

Quando houver conflito, os valores não deverão ser sobrescritos silenciosamente.

O sistema deverá preservar as observações dos providers e produzir um valor
canônico.

#### Vínculos desconhecidos ou incompletos

Alguns providers poderão informar apenas:

    jogador atual da equipe

sem fornecer datas ou tipo de contrato.

Nesses casos, poderá ser criado um vínculo com:

    valid_from = null
    valid_until = null
    membership_status = ACTIVE
    is_current = true
    membership_type = UNKNOWN

O registro deverá permanecer marcado para enriquecimento futuro.

A ausência de datas não deverá impedir a preservação de uma associação
confiável.

#### Relação com contratos

`TeamMembership` não deverá substituir a entidade `Contract`.

Um vínculo esportivo e um vínculo contratual representam conceitos diferentes.

Exemplo:

    jogador emprestado atua pela equipe de destino
    mas mantém contrato com a equipe de origem

O domínio futuro poderá utilizar:

    Contract
    ├── player_id
    ├── team_id
    ├── start_date
    ├── end_date
    ├── contract_type
    ├── status
    └── source_provider

`TeamMembership` deverá responder:

    para qual equipe a pessoa está vinculada esportivamente

`Contract` deverá responder:

    com qual organização existe relação contratual

#### Relação com transferências

`TeamMembership` também não deverá substituir `Transfer`.

A transferência representa um evento de movimentação.

O vínculo representa um período de associação.

Exemplo:

    Transfer
        equipe de origem
        equipe de destino
        data
        tipo

    TeamMembership
        equipe de destino
        período do vínculo

Uma transferência confirmada poderá iniciar ou encerrar vínculos, mas deverá
permanecer registrada separadamente.

#### Relação com escalações

Um vínculo com a equipe não garante participação em uma partida.

A escalação deverá utilizar uma entidade específica.

Exemplo:

    LineupEntry
    ├── match_id
    ├── player_id
    ├── team_id
    ├── is_starter
    ├── shirt_number
    └── position

`TeamMembership` deverá ser usado como evidência de pertencimento, mas não como
registro de participação.

#### Relação com registros de elenco

`TeamMembership` representa o vínculo amplo entre pessoa e equipe.

`SquadRegistration` deverá representar a inscrição do jogador em um elenco,
temporada ou competição específica.

Exemplo:

    jogador possui vínculo com o clube
    mas não foi inscrito em determinada competição

Portanto:

    TeamMembership = vínculo com a equipe
    SquadRegistration = inscrição esportiva contextual

Essa separação será detalhada na próxima subseção.

#### Índices recomendados para TeamMembership

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_team_membership_person_id` | `person_id` | Buscar vínculos de uma pessoa. |
| `ix_team_membership_team_id` | `team_id` | Buscar membros de uma equipe. |
| `ix_team_membership_player_id` | `player_id` | Buscar vínculos de um jogador. |
| `ix_team_membership_coach_id` | `coach_id` | Buscar vínculos de um treinador. |
| `ix_team_membership_role` | `membership_role` | Filtrar vínculos pela função. |
| `ix_team_membership_type` | `membership_type` | Filtrar pelo tipo de vínculo. |
| `ix_team_membership_status` | `membership_status` | Filtrar pelo status. |
| `ix_team_membership_is_current` | `is_current` | Localizar vínculos atuais. |
| `ix_team_membership_valid_from` | `valid_from` | Consultar início de vínculos. |
| `ix_team_membership_valid_until` | `valid_until` | Consultar encerramento de vínculos. |
| `ix_team_membership_person_current` | `person_id, is_current` | Buscar vínculos atuais da pessoa. |
| `ix_team_membership_team_current` | `team_id, is_current` | Buscar membros atuais da equipe. |
| `ix_team_membership_team_role` | `team_id, membership_role` | Buscar membros por equipe e função. |
| `ix_team_membership_person_period` | `person_id, valid_from, valid_until` | Consultar histórico temporal. |
| `ix_team_membership_team_period` | `team_id, valid_from, valid_until` | Consultar composição histórica. |
| `ix_team_membership_loan_origin` | `loan_origin_team_id` | Localizar empréstimos por equipe de origem. |

Índices simples sobre campos booleanos poderão apresentar baixa seletividade.

Índices parciais poderão ser mais eficientes.

Exemplo conceitual para vínculos atuais de jogadores:

    INDEX ON team_membership (
        team_id,
        person_id
    )
    WHERE is_current = true
      AND membership_role = 'PLAYER'

Exemplo conceitual para vínculos atuais de treinadores:

    INDEX ON team_membership (
        team_id,
        coach_id
    )
    WHERE is_current = true
      AND coach_id IS NOT NULL

#### Restrições parciais recomendadas

Para evitar duplicidade de vínculos ativos equivalentes, poderá ser considerada
uma restrição parcial.

Exemplo conceitual:

    UNIQUE (
        person_id,
        team_id,
        membership_role,
        membership_type
    )
    WHERE is_current = true

Essa restrição não deverá ser aplicada antes de validar casos legítimos de
múltiplos vínculos simultâneos.

Pode ser necessário incluir:

    squad_category
    is_primary
    loan_origin_team_id

A restrição definitiva deverá ser definida somente após testes com dados reais.

#### Dependências futuras

A entidade `TeamMembership` será utilizada por:

- elencos;
- escalações;
- transferências;
- empréstimos;
- contratos;
- convocações;
- equipes de base;
- equipes reservas;
- comissões técnicas;
- treinadores;
- jogadores;
- histórico de carreira;
- estatísticas por equipe;
- disponibilidade de atletas;
- modelos de escalação;
- análise de continuidade do elenco;
- cálculo de experiência coletiva;
- reconstrução temporal de equipes.

Por isso, os períodos de validade e a preservação histórica deverão ser tratados
como elementos centrais da entidade.
---

### 7.7 SquadRegistration

A entidade `SquadRegistration` representa a inscrição esportiva de um jogador
em um elenco, temporada, competição ou período de registro específico.

Ela não deverá substituir o vínculo histórico representado por
`TeamMembership`.

Exemplo conceitual:

    Person
    └── Player
        ├── TeamMembership
        └── SquadRegistration

Um jogador poderá possuir vínculo ativo com uma equipe, mas não estar inscrito
em todas as competições disputadas por ela.

Exemplo:

    jogador vinculado ao clube
    jogador inscrito no campeonato nacional
    jogador não inscrito na competição continental

A entidade deverá preservar esse contexto.

#### Responsabilidades

A entidade `SquadRegistration` será responsável por:

- relacionar um jogador a uma equipe;
- indicar a temporada da inscrição;
- indicar a competição, quando aplicável;
- indicar o elenco ou categoria esportiva;
- armazenar o número de camisa contextual;
- registrar a posição declarada na inscrição;
- indicar o status da inscrição;
- preservar datas de validade;
- representar inscrições provisórias e definitivas;
- registrar inscrições em equipes principais e de base;
- registrar inscrições em seleções nacionais;
- permitir múltiplas inscrições simultâneas;
- preservar histórico de alterações;
- apoiar validações de escalação;
- apoiar consultas de elegibilidade esportiva.

#### Campos principais

    id
    player_id
    team_id
    season_id
    competition_id
    stage_id
    team_membership_id
    squad_category
    registration_type
    registration_status
    registration_number
    shirt_number
    registered_position
    registered_at
    valid_from
    valid_until
    deregistered_at
    is_current
    is_primary
    is_eligible
    eligibility_reason
    source_provider
    confidence_score
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno e canônico da inscrição. |
| `player_id` | UUID | Sim | Jogador inscrito no elenco ou competição. |
| `team_id` | UUID | Sim | Equipe responsável pela inscrição. |
| `season_id` | UUID | Não | Temporada relacionada à inscrição. |
| `competition_id` | UUID | Não | Competição específica da inscrição. |
| `stage_id` | UUID | Não | Fase específica, quando a inscrição for limitada a uma etapa. |
| `team_membership_id` | UUID | Não | Vínculo histórico que sustenta a inscrição. |
| `squad_category` | enum | Não | Categoria ou tipo de elenco. |
| `registration_type` | enum | Sim | Natureza da inscrição. |
| `registration_status` | enum | Sim | Situação atual ou histórica da inscrição. |
| `registration_number` | string | Não | Identificador oficial da inscrição. |
| `shirt_number` | integer | Não | Número de camisa utilizado no contexto da inscrição. |
| `registered_position` | enum | Não | Posição declarada na inscrição. |
| `registered_at` | datetime UTC | Não | Momento conhecido da realização da inscrição. |
| `valid_from` | date | Não | Início da validade esportiva da inscrição. |
| `valid_until` | date | Não | Final da validade esportiva da inscrição. |
| `deregistered_at` | datetime UTC | Não | Momento conhecido do cancelamento ou encerramento. |
| `is_current` | boolean | Sim | Indica se a inscrição permanece vigente. |
| `is_primary` | boolean | Sim | Indica se esta é a inscrição principal do jogador no contexto. |
| `is_eligible` | boolean | Sim | Indica se o jogador está elegível para atuar. |
| `eligibility_reason` | string | Não | Motivo conhecido de elegibilidade ou impedimento. |
| `source_provider` | string | Não | Provider que informou ou confirmou a inscrição. |
| `confidence_score` | decimal | Não | Nível de confiança do registro canônico. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Tipos de inscrição previstos

    SEASON
    COMPETITION
    STAGE
    SQUAD
    NATIONAL_TEAM
    YOUTH
    RESERVE
    TEMPORARY
    EMERGENCY
    REPLACEMENT
    TRIAL
    OTHER
    UNKNOWN

O valor `SEASON` deverá representar uma inscrição válida para uma temporada.

O valor `COMPETITION` deverá representar uma inscrição específica para uma
competição.

O valor `STAGE` deverá representar uma inscrição limitada a uma fase.

O valor `SQUAD` deverá representar a participação geral em um elenco.

O valor `NATIONAL_TEAM` deverá representar inscrição em uma seleção nacional.

O valor `YOUTH` deverá representar inscrição em categoria de base.

O valor `RESERVE` deverá representar inscrição em equipe reserva.

O valor `TEMPORARY` deverá representar uma inscrição com duração limitada.

O valor `EMERGENCY` poderá representar uma inscrição excepcional permitida por
regulamento.

O valor `REPLACEMENT` poderá representar um jogador inscrito em substituição a
outro atleta.

O valor `TRIAL` deverá representar participação provisória ou em avaliação,
quando esse conceito for aplicável ao provider.

#### Status de inscrição previstos

    PENDING
    SUBMITTED
    APPROVED
    ACTIVE
    SUSPENDED
    REJECTED
    CANCELLED
    EXPIRED
    REPLACED
    DEREGISTERED
    COMPLETED
    UNKNOWN

O status `PENDING` deverá indicar uma inscrição ainda não enviada ou não
confirmada.

O status `SUBMITTED` deverá indicar que a inscrição foi submetida à entidade
organizadora.

O status `APPROVED` deverá indicar aprovação formal, mas sem necessariamente
indicar que o período de validade já começou.

O status `ACTIVE` deverá indicar inscrição vigente.

O status `SUSPENDED` deverá indicar impedimento temporário sem exclusão da
inscrição.

O status `REJECTED` deverá indicar que a inscrição não foi aceita.

O status `CANCELLED` deverá indicar cancelamento antes ou durante sua validade.

O status `EXPIRED` deverá indicar encerramento automático pelo fim do período.

O status `REPLACED` deverá indicar que o jogador foi substituído na lista.

O status `DEREGISTERED` deverá indicar retirada formal da inscrição.

O status `COMPLETED` deverá indicar conclusão regular do período de inscrição.

#### Categorias de elenco previstas

    FIRST_TEAM
    RESERVE_TEAM
    SECOND_TEAM
    U23
    U21
    U20
    U19
    U18
    U17
    U16
    U15
    YOUTH
    WOMEN_FIRST_TEAM
    WOMEN_RESERVE
    WOMEN_YOUTH
    NATIONAL_SENIOR
    NATIONAL_OLYMPIC
    NATIONAL_YOUTH
    OTHER
    UNKNOWN

A categoria deverá representar o contexto esportivo da inscrição.

Ela não deverá substituir a identidade da equipe.

Quando uma categoria possuir uma equipe canônica própria, `team_id` deverá
referenciar diretamente essa equipe.

Exemplo:

    Team = Santos
    squad_category = FIRST_TEAM

ou:

    Team = Santos U20
    squad_category = U20

A estratégia utilizada deverá ser consistente em todo o domínio.

#### Posições registradas previstas

    GOALKEEPER
    CENTRE_BACK
    LEFT_BACK
    RIGHT_BACK
    WING_BACK
    DEFENSIVE_MIDFIELDER
    CENTRAL_MIDFIELDER
    ATTACKING_MIDFIELDER
    LEFT_MIDFIELDER
    RIGHT_MIDFIELDER
    LEFT_WINGER
    RIGHT_WINGER
    SECOND_STRIKER
    CENTRE_FORWARD
    STRIKER
    UTILITY_PLAYER
    OTHER
    UNKNOWN

A posição registrada poderá ser diferente da posição principal armazenada em
`Player`.

Exemplo:

    Player.primary_position = RIGHT_BACK
    SquadRegistration.registered_position = MIDFIELDER

Isso poderá ocorrer por:

- decisão administrativa;
- exigência do regulamento;
- simplificação do provider;
- mudança de função;
- categoria genérica da competição;
- inscrição emergencial.

A posição contextual não deverá alterar automaticamente o perfil permanente do
jogador.

#### Relacionamentos principais

    Player      1 ─── N SquadRegistration
    Team        1 ─── N SquadRegistration
    Season      0..1 ─── N SquadRegistration
    Competition 0..1 ─── N SquadRegistration
    Stage       0..1 ─── N SquadRegistration

    TeamMembership 0..1 ─── N SquadRegistration

A relação obrigatória deverá ocorrer por meio de:

    player_id
    team_id

Pelo menos um contexto adicional deverá ser conhecido sempre que possível:

    season_id
    competition_id
    stage_id
    squad_category

Uma inscrição poderá existir sem competição específica quando representar apenas
a composição geral do elenco.

#### Relação com TeamMembership

`TeamMembership` representa o vínculo da pessoa com a equipe.

`SquadRegistration` representa a inscrição esportiva do jogador.

Exemplo:

    TeamMembership:
        jogador vinculado ao clube entre 2025 e 2028

    SquadRegistration:
        jogador inscrito no campeonato nacional de 2026

Um vínculo poderá possuir várias inscrições.

Exemplo:

    campeonato estadual
    campeonato nacional
    copa nacional
    competição continental

A ausência de `team_membership_id` não deverá invalidar automaticamente uma
inscrição quando o provider não fornecer dados suficientes para localizar o
vínculo correspondente.

Entretanto, o sistema deverá tentar relacionar a inscrição ao vínculo histórico
mais compatível.

#### Compatibilidade entre jogador e vínculo

Quando `team_membership_id` for informado, deverão ser validadas as seguintes
condições:

    team_membership.person_id = player.person_id

e:

    team_membership.team_id = squad_registration.team_id

Além disso, o vínculo deverá possuir função compatível com jogador.

Exemplo:

    membership_role = PLAYER

Uma inscrição não deverá apontar para um vínculo de treinador, comissão técnica
ou outra pessoa.

#### Relação com Season

`season_id` deverá indicar a temporada esportiva relacionada à inscrição.

Exemplo:

    Brasileirão 2026
    Premier League 2026/2027
    Copa Libertadores 2026

A temporada deverá pertencer à competição quando `competition_id` também estiver
preenchido.

Regra esperada:

    season.competition_id = squad_registration.competition_id

Quando a temporada representar um calendário geral da equipe e não uma
competição específica, essa validação poderá depender da modelagem final de
`Season`.

#### Relação com Competition

`competition_id` deverá ser preenchido quando a inscrição for específica para
uma competição.

Exemplo:

    jogador inscrito no campeonato nacional
    jogador não inscrito na competição continental

A inscrição em uma competição não deverá ser inferida apenas pela existência de
um vínculo com a equipe.

A confirmação deverá vir de:

- lista oficial;
- provider confiável;
- escalação válida;
- registro da competição;
- associação canônica previamente confirmada.

#### Relação com Stage

Algumas competições poderão permitir alterações de elenco entre fases.

Exemplo:

    fase preliminar
    fase de grupos
    mata-mata
    fase final

Nesses casos, `stage_id` poderá limitar a validade da inscrição.

Quando `stage_id` for informado:

- deverá pertencer à competição indicada;
- deverá pertencer à temporada indicada, quando aplicável;
- não deverá representar uma fase de outra competição;
- a validade da inscrição deverá respeitar o período da fase.

#### Número de camisa

O número de camisa deverá ser contextual.

Ele não deverá ser armazenado como atributo permanente em `Player`.

Um jogador poderá utilizar números diferentes:

- em equipes diferentes;
- em temporadas diferentes;
- em competições diferentes;
- na seleção nacional;
- em categorias de base;
- em partidas específicas.

Exemplo:

    SquadRegistration A:
        team = clube
        shirt_number = 10

    SquadRegistration B:
        team = seleção
        shirt_number = 7

O número registrado em `SquadRegistration` deverá representar o número associado
ao elenco ou competição.

O número utilizado em uma partida específica deverá permanecer em
`LineupEntry`.

#### Validação do número de camisa

Quando informado, `shirt_number` deverá ser um inteiro positivo.

A faixa permitida poderá depender do regulamento.

Exemplos possíveis:

    1 a 23
    1 a 30
    1 a 50
    1 a 99

O modelo canônico não deverá impor inicialmente uma faixa universal rígida.

A validação específica deverá ocorrer conforme:

- competição;
- temporada;
- regulamento;
- categoria;
- provider.

Números como zero ou valores acima de 99 deverão ser preservados somente quando
houver evidência confiável de que foram utilizados oficialmente.

#### Número duplicado

Dois jogadores poderão possuir o mesmo número em contextos diferentes.

Exemplo:

    equipes diferentes
    categorias diferentes
    competições diferentes
    temporadas diferentes

Dentro do mesmo elenco e período, números duplicados poderão indicar:

- erro do provider;
- troca de numeração;
- períodos de validade diferentes;
- inscrição cancelada;
- inscrição provisória;
- exceção regulamentar.

Por isso, não deverá existir inicialmente uma restrição global simples sobre:

    team_id
    shirt_number

Uma restrição contextual futura poderá considerar:

    team_id
    season_id
    competition_id
    squad_category
    shirt_number
    is_current

Antes de sua aplicação, deverão ser analisados dados reais.

#### Status atual

O campo `is_current` deverá permitir consultas rápidas.

Exemplo de inscrição atual:

    registration_status = ACTIVE
    is_current = true
    valid_until = null

ou:

    registration_status = ACTIVE
    is_current = true
    valid_until >= data atual

Exemplo de inscrição encerrada:

    registration_status = COMPLETED
    is_current = false

Exemplo de inscrição retirada:

    registration_status = DEREGISTERED
    is_current = false
    deregistered_at preenchido

O campo `is_current` poderá ser derivado das datas e do status, mas poderá
permanecer armazenado por desempenho.

Nesse caso, deverá existir validação periódica de consistência.

#### Elegibilidade esportiva

O campo `is_eligible` deverá indicar se o jogador está apto a atuar dentro do
contexto da inscrição.

Uma inscrição ativa não significa necessariamente elegibilidade imediata.

Exemplos de impedimento:

- suspensão disciplinar;
- documentação pendente;
- limite de estrangeiros;
- restrição etária;
- inscrição fora do prazo;
- lesão não impeditiva administrativamente;
- transferência ainda não homologada;
- sanção da competição;
- irregularidade contratual;
- restrição específica do regulamento.

O campo `eligibility_reason` poderá armazenar temporariamente uma descrição
textual.

Futuramente, deverá existir uma estrutura própria.

Exemplo conceitual:

    PlayerEligibility
    ├── id
    ├── squad_registration_id
    ├── eligibility_status
    ├── reason_type
    ├── reason_description
    ├── valid_from
    ├── valid_until
    ├── source_provider
    └── created_at

#### Status de elegibilidade previstos

Uma futura estrutura poderá utilizar:

    ELIGIBLE
    INELIGIBLE
    CONDITIONALLY_ELIGIBLE
    PENDING_DOCUMENTATION
    SUSPENDED
    NOT_REGISTERED
    REGISTRATION_EXPIRED
    UNKNOWN

A elegibilidade deverá considerar uma data de referência.

Um jogador poderá estar inelegível em uma rodada e elegível na rodada seguinte.

#### Inscrição provisória

Inscrições provisórias deverão ser preservadas.

Exemplo:

    registration_type = TEMPORARY
    registration_status = PENDING

ou:

    registration_type = EMERGENCY
    registration_status = ACTIVE

Quando uma inscrição provisória for convertida em definitiva, o histórico não
deverá ser sobrescrito silenciosamente.

A aplicação poderá:

- atualizar o mesmo registro quando houver continuidade comprovada;
- criar um novo registro quando houver mudança de natureza;
- preservar o evento de alteração;
- manter a origem de cada observação.

#### Substituição de jogador inscrito

Algumas competições permitem substituir jogadores inscritos.

Exemplo:

    jogador A removido
    jogador B inscrito em seu lugar

A entidade deverá permitir registrar:

    jogador substituído
    jogador substituto
    data da substituição
    motivo
    regra utilizada
    provider de origem

Futuramente, poderá existir:

    SquadRegistrationReplacement
    ├── id
    ├── outgoing_registration_id
    ├── incoming_registration_id
    ├── replacement_date
    ├── replacement_reason
    ├── regulation_reference
    └── source_provider

O status do jogador removido poderá ser:

    REPLACED

O status do novo jogador poderá ser:

    ACTIVE

#### Cancelamento e retirada

O cancelamento da inscrição não deverá apagar o registro.

Exemplos:

    registro rejeitado
    jogador retirado da lista
    inscrição cancelada
    documentação irregular
    jogador transferido
    jogador substituído

Deverão ser preservados:

    registration_status
    deregistered_at
    valid_until
    is_current
    motivo conhecido
    provider de origem

A retirada deverá permitir reconstruir a composição histórica do elenco.

#### Múltiplas inscrições simultâneas

Um jogador poderá possuir várias inscrições ativas simultaneamente.

Exemplos:

    campeonato nacional
    copa nacional
    competição continental

Também poderá estar inscrito por:

    clube
    seleção nacional

Além disso, poderá estar elegível para:

    equipe principal
    equipe sub-20

Portanto, não deverá existir uma restrição global garantindo apenas uma inscrição
ativa por jogador.

A unicidade deverá considerar o contexto esportivo.

#### Inscrição principal

O campo `is_primary` poderá indicar a inscrição esportiva predominante dentro de
um contexto.

Exemplo:

    equipe principal = inscrição principal
    equipe reserva = inscrição secundária

ou:

    lista definitiva = inscrição principal
    lista provisória = inscrição secundária

A interpretação deverá ser documentada pelos serviços de domínio.

Não deverá existir mais de uma inscrição principal equivalente no mesmo
contexto, salvo exceções regulamentares.

#### Equipes de base

Jogadores de base deverão utilizar a mesma entidade `Player`.

A inscrição deverá indicar:

    squad_category = categoria correspondente

Exemplo:

    U17
    U20
    YOUTH

A promoção para uma categoria superior não deverá criar um novo jogador.

Poderá criar:

- nova inscrição;
- novo vínculo com equipe específica;
- encerramento da inscrição anterior;
- manutenção de inscrições simultâneas.

Exemplo:

    jogador inscrito no U20
    jogador também inscrito na equipe principal

#### Equipes reservas

Equipes reservas poderão possuir inscrições independentes.

Exemplo:

    jogador inscrito no Bayern München II
    jogador relacionado à equipe principal

Quando as equipes possuírem identidades canônicas distintas, cada inscrição
deverá utilizar o `team_id` correspondente.

A transferência interna entre elenco reserva e principal não deverá criar uma
nova identidade de jogador.

#### Seleções nacionais

Inscrições em seleções deverão ser contextuais.

Exemplo:

    competição = Copa do Mundo
    temporada = edição correspondente
    team = seleção nacional
    registration_type = NATIONAL_TEAM

Uma convocação não será necessariamente igual a uma inscrição definitiva.

A convocação poderá indicar intenção ou presença em uma lista preliminar.

A inscrição poderá representar a lista oficialmente aceita pela competição.

Portanto:

    NationalTeamCallup = convocação
    SquadRegistration = inscrição esportiva
    LineupEntry = participação ou disponibilidade em partida

#### Listas preliminares e definitivas

Uma competição poderá possuir:

    lista preliminar
    lista final
    lista de reservas
    lista de emergência

A primeira versão poderá representar essas variações por:

    registration_type
    registration_status
    is_primary

Futuramente, poderá existir um campo específico:

    squad_list_type

Valores possíveis:

    PRELIMINARY
    FINAL
    RESERVE
    EMERGENCY
    EXTENDED
    OTHER

A modelagem deverá preservar mudanças entre listas.

#### Janelas de inscrição

Competições poderão possuir períodos específicos para inscrição de jogadores.

Exemplo conceitual:

    RegistrationWindow
    ├── id
    ├── competition_id
    ├── season_id
    ├── stage_id
    ├── window_type
    ├── starts_at
    ├── ends_at
    └── status

Uma `SquadRegistration` poderá futuramente referenciar:

    registration_window_id

Isso permitirá validar:

- inscrições dentro do prazo;
- inscrições emergenciais;
- substituições permitidas;
- janelas adicionais;
- alterações entre fases.

#### Registro oficial e provider

Nem todo provider fornecerá uma lista oficialmente homologada.

Alguns providers poderão inferir o elenco a partir de:

- partidas anteriores;
- páginas de equipes;
- escalações;
- transferências;
- notícias;
- listas parciais.

Por isso, o registro deverá preservar:

- origem;
- data de observação;
- identificador externo;
- nível de confiança;
- tipo da fonte;
- evidência disponível.

Uma escalação em partida poderá ser uma forte evidência de elegibilidade naquele
jogo, mas não deverá necessariamente comprovar uma inscrição válida para toda a
temporada.

#### Origem e confiança

O campo `source_provider` poderá armazenar temporariamente a fonte principal.

A arquitetura definitiva deverá utilizar uma estrutura de proveniência.

Exemplo conceitual:

    EntitySource
    ├── entity_type
    ├── entity_id
    ├── provider
    ├── external_id
    ├── observed_at
    ├── source_type
    ├── confidence_score
    └── raw_reference

O valor canônico poderá ser formado por múltiplas observações.

Conflitos não deverão ser sobrescritos silenciosamente.

#### Resolução de duplicidade

Providers diferentes poderão informar a mesma inscrição com pequenas
divergências.

Exemplo:

    número de camisa 10
    número de camisa desconhecido
    posição meia
    posição atacante
    data de inscrição diferente
    status ativo em um provider
    status pendente em outro

A resolução deverá considerar:

- jogador;
- equipe;
- temporada;
- competição;
- fase;
- categoria;
- tipo de inscrição;
- número de registro oficial;
- datas;
- provider;
- identificadores externos.

Uma combinação candidata de identidade será:

    player_id
    team_id
    season_id
    competition_id
    stage_id
    registration_type

Campos nulos deverão ser tratados explicitamente.

Não deverá ser criada uma restrição definitiva antes da análise de dados reais.

#### Registros incompletos

Uma inscrição poderá ser recebida sem todos os contextos.

Exemplo:

    jogador listado no elenco atual da equipe
    competição desconhecida
    temporada não informada
    número de camisa disponível

Nesse caso, poderá ser criado um registro com:

    player_id preenchido
    team_id preenchido
    season_id = null
    competition_id = null
    registration_type = SQUAD
    registration_status = ACTIVE
    is_current = true

O registro deverá permanecer marcado para enriquecimento.

A ausência de competição não deverá causar associação automática a todas as
competições da equipe.

#### Regras de integridade

- `player_id` deverá referenciar um jogador existente;
- `team_id` deverá referenciar uma equipe existente;
- `season_id`, quando informado, deverá referenciar uma temporada existente;
- `competition_id`, quando informado, deverá referenciar uma competição
  existente;
- `stage_id`, quando informado, deverá referenciar uma fase existente;
- `team_membership_id`, quando informado, deverá referenciar um vínculo
  existente;
- `registration_type` deverá possuir valor válido;
- `registration_status` deverá possuir valor válido;
- `squad_category`, quando informada, deverá possuir valor válido;
- `registered_position`, quando informada, deverá possuir valor válido;
- `shirt_number`, quando informado, deverá ser um número inteiro positivo;
- `valid_until`, quando informado, deverá ser posterior ou igual a
  `valid_from`;
- `deregistered_at`, quando informado, deverá ser posterior ou igual a
  `registered_at`;
- `is_current = true` deverá ser compatível com o status e o período;
- `is_current = false` deverá ser compatível com inscrição futura, encerrada,
  cancelada ou suspensa;
- `is_eligible = true` deverá ser compatível com uma inscrição válida;
- `registration_status = ACTIVE` não deverá garantir automaticamente
  `is_eligible = true`;
- `registration_status = DEREGISTERED` deverá ser compatível com
  `is_current = false`;
- `registration_status = EXPIRED` deverá ser compatível com
  `is_current = false`;
- `registration_status = CANCELLED` deverá ser compatível com
  `is_current = false`;
- `stage_id` deverá pertencer à competição indicada;
- `season_id` deverá ser compatível com a competição indicada;
- `team_membership_id` deverá relacionar a mesma pessoa e a mesma equipe;
- inscrições históricas não deverão ser removidas fisicamente;
- o encerramento da inscrição não deverá apagar escalações ou estatísticas;
- conflitos de inscrição deverão ser preservados para revisão.

#### Regra inicial de unicidade

Uma pessoa poderá possuir múltiplas inscrições no mesmo clube.

Por isso, não deverá existir uma restrição simples apenas sobre:

    player_id
    team_id

Uma combinação candidata será:

    player_id
    team_id
    season_id
    competition_id
    stage_id
    registration_type

Entretanto, essa combinação poderá conter valores nulos.

Também poderão existir:

- lista preliminar e final;
- inscrição cancelada e inscrição ativa;
- reinscrição na mesma temporada;
- mudanças entre fases;
- registros de providers diferentes;
- números de inscrição oficiais diferentes.

A restrição definitiva deverá ser criada após testes com dados reais.

#### Relação com LineupEntry

`SquadRegistration` não deverá representar participação em uma partida.

A participação deverá utilizar:

    LineupEntry

Exemplo:

    SquadRegistration:
        jogador está inscrito na competição

    LineupEntry:
        jogador foi relacionado para a partida

Um jogador inscrito poderá:

- não ser convocado;
- ficar fora da lista;
- estar suspenso;
- estar lesionado;
- permanecer no banco;
- iniciar como titular.

A escalação deverá referenciar a inscrição quando possível.

Exemplo futuro:

    LineupEntry
    ├── match_id
    ├── squad_registration_id
    ├── player_id
    ├── team_id
    ├── is_starter
    ├── shirt_number
    └── position

#### Relação com MatchSquad

Uma partida poderá possuir uma lista de jogadores disponíveis.

Futuramente, poderá existir:

    MatchSquad
    ├── id
    ├── match_id
    ├── team_id
    ├── player_id
    ├── squad_registration_id
    ├── squad_status
    ├── shirt_number
    └── source_provider

Essa estrutura poderá diferenciar:

    STARTER
    SUBSTITUTE
    RESERVE
    NOT_SELECTED
    UNAVAILABLE
    UNKNOWN

`SquadRegistration` indicará elegibilidade ampla.

`MatchSquad` indicará disponibilidade ou convocação para uma partida.

#### Relação com suspensão

Uma suspensão disciplinar não deverá apagar a inscrição.

Exemplo:

    registration_status = ACTIVE
    is_current = true
    is_eligible = false

O impedimento poderá existir em uma entidade específica.

Exemplo:

    PlayerSuspension
    ├── player_id
    ├── competition_id
    ├── season_id
    ├── start_date
    ├── end_date
    ├── matches_remaining
    └── status

A elegibilidade deverá ser recalculada conforme o contexto.

#### Relação com transferência

Uma transferência poderá encerrar uma inscrição.

Exemplo:

    jogador transferido para outro clube
    inscrição anterior encerrada
    nova inscrição criada

Entretanto, a transferência e a inscrição deverão permanecer como entidades
separadas.

A transferência representa o evento de movimentação.

A inscrição representa a autorização esportiva em um contexto.

#### Relação com contrato

O contrato não deverá garantir inscrição.

Exemplo:

    jogador possui contrato com o clube
    jogador não está inscrito na competição

Da mesma forma, uma inscrição temporária poderá existir em situações específicas
sem que todos os detalhes contratuais estejam disponíveis no sistema.

Portanto:

    Contract = relação contratual
    TeamMembership = vínculo histórico
    SquadRegistration = inscrição esportiva

#### Relação com estatísticas

Estatísticas não deverão ser armazenadas diretamente em
`SquadRegistration`.

Entretanto, a inscrição poderá ser utilizada para contextualizar:

- partidas disputadas;
- minutos jogados;
- gols;
- assistências;
- cartões;
- titularidades;
- convocações;
- disponibilidade;
- percentual de utilização.

As estatísticas deverão permanecer em entidades próprias.

#### Índices recomendados para SquadRegistration

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_squad_registration_player_id` | `player_id` | Buscar inscrições de um jogador. |
| `ix_squad_registration_team_id` | `team_id` | Buscar inscrições de uma equipe. |
| `ix_squad_registration_season_id` | `season_id` | Buscar inscrições por temporada. |
| `ix_squad_registration_competition_id` | `competition_id` | Buscar inscrições por competição. |
| `ix_squad_registration_stage_id` | `stage_id` | Buscar inscrições por fase. |
| `ix_squad_registration_membership_id` | `team_membership_id` | Localizar inscrições ligadas a um vínculo. |
| `ix_squad_registration_status` | `registration_status` | Filtrar pelo status. |
| `ix_squad_registration_type` | `registration_type` | Filtrar pelo tipo. |
| `ix_squad_registration_is_current` | `is_current` | Localizar inscrições vigentes. |
| `ix_squad_registration_is_eligible` | `is_eligible` | Localizar jogadores elegíveis. |
| `ix_squad_registration_team_current` | `team_id, is_current` | Buscar elenco atual da equipe. |
| `ix_squad_registration_player_current` | `player_id, is_current` | Buscar inscrições atuais do jogador. |
| `ix_squad_registration_competition_team` | `competition_id, team_id` | Buscar elenco da equipe em uma competição. |
| `ix_squad_registration_season_team` | `season_id, team_id` | Buscar elenco da equipe na temporada. |
| `ix_squad_registration_context` | `player_id, team_id, season_id, competition_id` | Consultar inscrição contextual. |
| `ix_squad_registration_shirt_context` | `team_id, season_id, competition_id, shirt_number` | Consultar numeração contextual. |
| `ix_squad_registration_validity` | `valid_from, valid_until` | Consultar validade temporal. |

Índices simples sobre campos booleanos poderão apresentar baixa seletividade.

Índices parciais poderão ser mais eficientes.

Exemplo para inscrições atuais de uma equipe:

    INDEX ON squad_registration (
        team_id,
        player_id
    )
    WHERE is_current = true

Exemplo para jogadores elegíveis em uma competição:

    INDEX ON squad_registration (
        competition_id,
        team_id,
        player_id
    )
    WHERE is_current = true
      AND is_eligible = true

#### Restrições parciais recomendadas

Uma possível restrição parcial poderá evitar inscrições ativas equivalentes.

Exemplo conceitual:

    UNIQUE (
        player_id,
        team_id,
        season_id,
        competition_id,
        registration_type
    )
    WHERE is_current = true

Essa restrição deverá ser avaliada com cuidado.

Ela poderá impedir casos legítimos como:

- lista preliminar e lista definitiva;
- inscrição em fases diferentes;
- reinscrição;
- múltiplas categorias;
- competição sem temporada preenchida;
- registros oficiais com números diferentes.

Poderá ser necessário incluir:

    stage_id
    squad_category
    registration_number

A restrição definitiva será definida após validação com dados reais.

#### Dependências futuras

A entidade `SquadRegistration` será utilizada por:

- elencos;
- temporadas;
- competições;
- fases;
- escalações;
- listas de relacionados;
- jogadores elegíveis;
- substituições de inscritos;
- janelas de inscrição;
- seleções nacionais;
- equipes de base;
- equipes reservas;
- suspensões;
- transferências;
- validação de participação;
- estatísticas de utilização;
- previsão de escalações;
- análise de profundidade do elenco;
- análise de disponibilidade;
- mercados de apostas relacionados a jogadores.

Por isso, a inscrição deverá preservar contexto, validade temporal, origem e
histórico de alterações.


---

### 7.8 Consolidação dos participantes do futebol

Esta subseção consolida as decisões arquiteturais das entidades relacionadas às
pessoas, equipes, perfis profissionais, vínculos e inscrições esportivas.

#### Estrutura canônica consolidada

A estrutura principal será:

    Person
    ├── Player
    ├── Coach
    └── Referee

    Team
    ├── TeamMembership
    └── SquadRegistration

`Person` representa a identidade humana.

`Player`, `Coach` e `Referee` representam perfis profissionais especializados.

`TeamMembership` representa o vínculo histórico de uma pessoa com uma equipe.

`SquadRegistration` representa a inscrição esportiva contextual de um jogador.

#### Separação de responsabilidades

As responsabilidades deverão permanecer separadas da seguinte forma:

    Person
        identidade humana
        nome
        nascimento
        nacionalidade
        características físicas
        pé preferencial
        aliases

    Player
        perfil esportivo do jogador
        posição principal
        posição secundária
        situação profissional
        estreia e aposentadoria

    Coach
        perfil profissional de treinador
        função técnica principal
        licença
        situação profissional

    Referee
        perfil profissional de arbitragem
        função principal
        categoria
        certificação
        situação profissional

    TeamMembership
        vínculo histórico entre pessoa e equipe
        função
        natureza do vínculo
        período
        situação atual ou histórica

    SquadRegistration
        inscrição esportiva de jogador
        equipe
        temporada
        competição
        fase
        categoria
        número de camisa
        elegibilidade

Nenhuma dessas entidades deverá assumir responsabilidades pertencentes às
demais.

#### Identidade humana única

Uma pessoa deverá possuir apenas uma identidade canônica em `Person`.

A mesma pessoa poderá possuir múltiplos perfis profissionais.

Exemplo:

    Person
    ├── Player aposentado
    └── Coach ativo

Também poderá existir:

    Person
    ├── Player
    └── Referee

Esse caso deverá ser permitido quando houver evidência confiável.

Entretanto, cada pessoa deverá possuir no máximo:

    um perfil Player
    um perfil Coach
    um perfil Referee

As restrições recomendadas serão:

    UNIQUE player.person_id
    UNIQUE coach.person_id
    UNIQUE referee.person_id

#### Perfis profissionais não representam vínculos

Os perfis `Player`, `Coach` e `Referee` deverão permanecer estáveis durante toda
a carreira.

Mudanças de:

- equipe;
- competição;
- temporada;
- número de camisa;
- função contextual;
- situação contratual;
- convocação;
- inscrição;
- empréstimo;

não deverão gerar novos perfis profissionais.

Essas mudanças deverão ser representadas pelas entidades contextuais
correspondentes.

#### Vínculo não representa inscrição

A distinção fundamental será:

    TeamMembership = vínculo com a equipe
    SquadRegistration = inscrição esportiva
    LineupEntry = participação ou relação com uma partida

Exemplo:

    jogador contratado pelo clube
        TeamMembership

    jogador inscrito no campeonato
        SquadRegistration

    jogador relacionado ou escalado para uma partida
        LineupEntry

Essas entidades não deverão ser fundidas.

#### Vínculo não representa contrato

A distinção futura será:

    TeamMembership
        vínculo histórico ou esportivo

    Contract
        relação contratual

    Transfer
        evento de movimentação

    SquadRegistration
        inscrição em um contexto esportivo

Um jogador poderá atuar por empréstimo na equipe de destino enquanto mantém
contrato com a equipe de origem.

Por isso, contrato, transferência, vínculo e inscrição deverão permanecer como
conceitos separados.

#### Equipes atuais deverão ser derivadas

Os campos de equipe atual não deverão ser armazenados diretamente em:

    Player
    Coach
    Referee

Para jogadores e treinadores, a associação atual deverá ser derivada de
`TeamMembership`.

Para árbitros, a associação institucional deverá ser derivada de estruturas
como:

    RefereeFederationMembership
    RefereeAssignment
    MatchOfficial

Essa regra evita divergência entre o perfil e o histórico de vínculos.

#### Número de camisa contextual

O número de camisa não deverá existir como atributo permanente de `Player`.

Ele poderá aparecer em:

    SquadRegistration
    MatchSquad
    LineupEntry

Cada entidade representa um nível diferente de contexto:

    SquadRegistration
        número registrado para elenco ou competição

    MatchSquad
        número relacionado à convocação da partida

    LineupEntry
        número efetivamente utilizado na partida

Os valores poderão divergir legitimamente.

#### Posições contextuais

A posição principal do atleta deverá permanecer em:

    Player.primary_position

Posições contextuais poderão existir em:

    SquadRegistration.registered_position
    LineupEntry.position
    MatchEvent.player_position

Uma posição contextual não deverá alterar automaticamente a posição principal
do jogador.

A atualização do perfil deverá depender da consolidação de múltiplas evidências.

#### Dados temporais

Entidades de vínculo e inscrição deverão preservar datas de validade.

Campos principais:

    valid_from
    valid_until
    joined_at
    left_at
    registered_at
    deregistered_at

Registros históricos não deverão ser removidos fisicamente.

O encerramento deverá ocorrer por:

- atualização de status;
- preenchimento de datas;
- atualização de `is_current`;
- preservação da origem;
- manutenção das referências históricas.

#### Campos derivados

Campos como:

    is_current
    is_active
    is_retired
    is_eligible
    is_on_loan

poderão ser armazenados para facilitar consultas.

Entretanto, deverão permanecer consistentes com:

- status;
- datas;
- relacionamentos;
- eventos históricos;
- regras de domínio.

Rotinas de validação deverão identificar divergências entre campos derivados e
suas fontes.

#### Valores desconhecidos

Enums poderão utilizar:

    UNKNOWN

Esse valor deverá representar ausência real de informação.

Ele não deverá ser utilizado para:

- evitar validação;
- esconder erro de normalização;
- substituir campo obrigatório conhecido;
- descartar valor recebido do provider.

O valor original deverá ser preservado na camada de proveniência.

#### Valores OTHER e UNKNOWN

A diferença será:

    OTHER
        valor conhecido, mas não contemplado pelo enum atual

    UNKNOWN
        valor não conhecido ou não informado

Exemplo:

    função conhecida, mas ainda não mapeada
        OTHER

    provider não informou a função
        UNKNOWN

Essa distinção deverá ser mantida em todos os enums do domínio.

#### Dados provenientes de providers

Campos temporários como:

    source_provider
    confidence_score

poderão permanecer nas primeiras implementações.

Entretanto, a arquitetura definitiva deverá utilizar estruturas de
proveniência independentes.

Exemplo:

    EntitySource
    ExternalEntityMapping
    ProviderObservation
    CanonicalFieldValue
    ConflictRecord

Nenhum valor divergente deverá ser sobrescrito silenciosamente.

#### Resolução de identidade

A ordem recomendada para resolução será:

    provider payload
        ↓
    external identifier
        ↓
    normalized candidate
        ↓
    Person resolution
        ↓
    professional profile resolution
        ↓
    Team resolution
        ↓
    contextual entity resolution
        ↓
    canonical record

Para jogadores:

    Person
        ↓
    Player
        ↓
    TeamMembership
        ↓
    SquadRegistration

Para treinadores:

    Person
        ↓
    Coach
        ↓
    TeamMembership

Para árbitros:

    Person
        ↓
    Referee
        ↓
    MatchOfficial ou RefereeAssignment

#### Exclusão de registros

As entidades desta seção não deverão utilizar exclusão física quando possuírem
histórico relacionado.

A desativação deverá utilizar:

    is_active = false

ou status equivalentes.

A exclusão física poderá ser considerada apenas para:

- registros criados por erro técnico;
- duplicidades ainda sem referências;
- dados de teste;
- registros nunca publicados;
- situações formalmente auditadas.

Fusões de identidade deverão preservar um redirecionamento para a entidade
canônica final.

#### Integridade entre perfis e pessoas

Toda referência especializada deverá corresponder à mesma pessoa.

Exemplos obrigatórios:

    player.person_id = team_membership.person_id

    coach.person_id = team_membership.person_id

    player.person_id =
        team_membership.person_id =
        squad_registration.player.person_id

Essas regras poderão exigir validações na aplicação quando não puderem ser
expressas apenas por chaves estrangeiras.

#### Integridade entre inscrições e contexto esportivo

Quando informados conjuntamente:

    season.competition_id =
        squad_registration.competition_id

    stage.competition_id =
        squad_registration.competition_id

    team_membership.team_id =
        squad_registration.team_id

    team_membership.person_id =
        squad_registration.player.person_id

Incompatibilidades deverão ser rejeitadas ou encaminhadas para revisão.

#### Estratégia inicial de implementação

A implementação deverá ocorrer em camadas.

Primeira camada:

    Person
    Team
    Player
    Coach
    Referee

Segunda camada:

    TeamMembership
    SquadRegistration

Terceira camada:

    ExternalEntityMapping
    EntitySource
    ProviderObservation

Quarta camada:

    Contract
    Transfer
    LineupEntry
    MatchOfficial
    MatchSquad

Essa ordem reduz dependências circulares e facilita migrations incrementais.

#### Ordem recomendada das migrations

A ordem inicial recomendada será:

    1. country
    2. city
    3. stadium
    4. competition
    5. season
    6. stage
    7. round
    8. team
    9. person
    10. player
    11. coach
    12. referee
    13. team_membership
    14. squad_registration

As tabelas de proveniência poderão ser implementadas antes ou logo após as
entidades canônicas, conforme a estratégia de ingestão.

#### Resumo da seção

A seção de participantes estabelece os seguintes princípios:

- uma identidade humana canônica por pessoa;
- perfis profissionais separados;
- perfis estáveis durante toda a carreira;
- vínculos históricos independentes;
- inscrições esportivas contextuais;
- números de camisa contextuais;
- preservação temporal;
- ausência de sobrescrita silenciosa;
- resolução de identidade antes da criação de vínculos;
- separação entre vínculo, contrato, transferência e inscrição;
- compatibilidade entre pessoa, perfil, equipe e contexto;
- preparação para integração de múltiplos providers.

Esses princípios deverão orientar a implementação das models, migrations,
repositories, serviços de domínio e rotinas de normalização.
---

## 8. Partidas e calendário esportivo

Esta seção define as entidades canônicas relacionadas a partidas, calendário,
participantes, locais, arbitragem, escalações e eventos esportivos.

A partida será um dos principais agregados do domínio.

Ela concentrará o contexto necessário para relacionar:

    competição
    temporada
    fase
    rodada
    equipes
    local
    árbitros
    escalações
    eventos
    estatísticas
    probabilidades
    mercados de apostas

Os payloads recebidos de providers não deverão ser gravados diretamente na
entidade canônica `Match`.

O fluxo esperado será:

    provider payload
        ↓
    collector
        ↓
    normalization
        ↓
    external entity mapping
        ↓
    identity resolution
        ↓
    fusion
        ↓
    Match canônica

---

### 8.1 Match

A entidade `Match` representa uma partida canônica de futebol.

Ela deverá permanecer estável mesmo quando diferentes providers utilizarem:

- identificadores diferentes;
- nomes diferentes para as equipes;
- horários divergentes;
- status diferentes;
- formatos diferentes de rodada;
- informações incompletas;
- atualizações em momentos distintos.

Uma partida não deverá ser duplicada apenas porque foi recebida de providers
diferentes.

#### Responsabilidades

A entidade `Match` será responsável por:

- representar uma partida canônica;
- relacionar a partida à competição;
- relacionar a partida à temporada;
- relacionar a partida à fase;
- relacionar a partida à rodada;
- armazenar data e horário programados;
- armazenar data e horário efetivos;
- indicar o status atual;
- indicar o tipo da partida;
- relacionar a equipe mandante;
- relacionar a equipe visitante;
- relacionar o local principal;
- armazenar o placar principal;
- indicar prorrogação e disputa por pênaltis;
- preservar alterações de calendário;
- servir como referência para eventos;
- servir como referência para escalações;
- servir como referência para estatísticas;
- servir como referência para mercados de apostas;
- servir como referência para probabilidades e recomendações;
- preservar proveniência e histórico de atualização.

#### Campos principais

    id
    competition_id
    season_id
    stage_id
    round_id
    home_team_id
    away_team_id
    stadium_id
    match_type
    match_status
    scheduled_start_at
    confirmed_start_at
    actual_start_at
    halftime_at
    actual_end_at
    scheduled_date
    timezone
    attendance
    home_score
    away_score
    home_halftime_score
    away_halftime_score
    home_extra_time_score
    away_extra_time_score
    home_penalty_score
    away_penalty_score
    winner_team_id
    duration_minutes
    stoppage_time_first_half
    stoppage_time_second_half
    has_extra_time
    has_penalty_shootout
    is_neutral_venue
    is_postponed
    is_cancelled
    is_abandoned
    is_rescheduled
    rescheduled_from_match_id
    source_provider
    confidence_score
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno e canônico da partida. |
| `competition_id` | UUID | Sim | Competição à qual a partida pertence. |
| `season_id` | UUID | Sim | Temporada relacionada à partida. |
| `stage_id` | UUID | Não | Fase da competição, quando aplicável. |
| `round_id` | UUID | Não | Rodada relacionada à partida. |
| `home_team_id` | UUID | Sim | Equipe registrada como mandante. |
| `away_team_id` | UUID | Sim | Equipe registrada como visitante. |
| `stadium_id` | UUID | Não | Estádio ou local principal da partida. |
| `match_type` | enum | Sim | Natureza esportiva da partida. |
| `match_status` | enum | Sim | Situação atual da partida. |
| `scheduled_start_at` | datetime UTC | Não | Data e horário originalmente programados. |
| `confirmed_start_at` | datetime UTC | Não | Data e horário oficialmente confirmados. |
| `actual_start_at` | datetime UTC | Não | Momento efetivo do início da partida. |
| `halftime_at` | datetime UTC | Não | Momento conhecido do intervalo. |
| `actual_end_at` | datetime UTC | Não | Momento efetivo do encerramento. |
| `scheduled_date` | date | Não | Data esportiva da partida quando o horário ainda for desconhecido. |
| `timezone` | string | Não | Fuso horário local utilizado na programação. |
| `attendance` | integer | Não | Público oficialmente informado. |
| `home_score` | integer | Não | Placar principal da equipe mandante. |
| `away_score` | integer | Não | Placar principal da equipe visitante. |
| `home_halftime_score` | integer | Não | Placar do mandante no intervalo. |
| `away_halftime_score` | integer | Não | Placar do visitante no intervalo. |
| `home_extra_time_score` | integer | Não | Placar do mandante após a prorrogação. |
| `away_extra_time_score` | integer | Não | Placar do visitante após a prorrogação. |
| `home_penalty_score` | integer | Não | Gols do mandante na disputa por pênaltis. |
| `away_penalty_score` | integer | Não | Gols do visitante na disputa por pênaltis. |
| `winner_team_id` | UUID | Não | Equipe vencedora da partida, quando aplicável. |
| `duration_minutes` | integer | Não | Duração esportiva registrada da partida. |
| `stoppage_time_first_half` | integer | Não | Acréscimos do primeiro tempo. |
| `stoppage_time_second_half` | integer | Não | Acréscimos do segundo tempo. |
| `has_extra_time` | boolean | Sim | Indica se houve ou haverá prorrogação. |
| `has_penalty_shootout` | boolean | Sim | Indica se houve disputa por pênaltis. |
| `is_neutral_venue` | boolean | Sim | Indica se o local é considerado neutro. |
| `is_postponed` | boolean | Sim | Indica adiamento da partida. |
| `is_cancelled` | boolean | Sim | Indica cancelamento definitivo. |
| `is_abandoned` | boolean | Sim | Indica abandono após o início. |
| `is_rescheduled` | boolean | Sim | Indica que houve alteração oficial da programação. |
| `rescheduled_from_match_id` | UUID | Não | Partida ou registro anterior relacionado ao reagendamento. |
| `source_provider` | string | Não | Provider principal que originou o registro atual. |
| `confidence_score` | decimal | Não | Nível de confiança do registro canônico. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Tipos de partida previstos

    REGULAR
    FRIENDLY
    QUALIFIER
    PLAYOFF
    KNOCKOUT
    GROUP_STAGE
    LEAGUE
    CUP
    SUPERCUP
    THIRD_PLACE
    FINAL
    EXHIBITION
    TRAINING
    ABANDONED_REPLAY
    OTHER
    UNKNOWN

O tipo da partida deverá representar sua natureza esportiva principal.

Ele não deverá substituir:

    competition_id
    stage_id
    round_id

Exemplo:

    match_type = FINAL
    competition_id = Copa do Mundo
    stage_id = Final

A redundância poderá ser aceita para facilitar consultas, desde que permaneça
consistente com o contexto da competição.

#### Status de partida previstos

    SCHEDULED
    DATE_DEFINED
    TIME_UNCONFIRMED
    CONFIRMED
    PRE_MATCH
    WARMUP
    FIRST_HALF
    HALFTIME
    SECOND_HALF
    EXTRA_TIME
    EXTRA_TIME_HALFTIME
    PENALTY_SHOOTOUT
    INTERRUPTED
    SUSPENDED
    POSTPONED
    DELAYED
    ABANDONED
    CANCELLED
    WALKOVER
    AWARDED
    FINISHED
    AFTER_EXTRA_TIME
    AFTER_PENALTIES
    UNKNOWN

O status deverá representar a situação esportiva mais recente conhecida.

#### Significado dos status

`SCHEDULED` deverá indicar partida programada com data ou horário conhecido.

`DATE_DEFINED` deverá indicar que apenas a data esportiva está definida.

`TIME_UNCONFIRMED` deverá indicar que a data existe, mas o horário ainda poderá
ser alterado.

`CONFIRMED` deverá indicar programação oficialmente confirmada.

`PRE_MATCH` deverá indicar período próximo ao início da partida.

`WARMUP` poderá ser utilizado quando o provider informar explicitamente o
aquecimento ou preparação imediata.

`FIRST_HALF` deverá indicar o primeiro tempo em andamento.

`HALFTIME` deverá indicar o intervalo regulamentar.

`SECOND_HALF` deverá indicar o segundo tempo em andamento.

`EXTRA_TIME` deverá indicar prorrogação em andamento.

`EXTRA_TIME_HALFTIME` deverá indicar intervalo da prorrogação.

`PENALTY_SHOOTOUT` deverá indicar disputa por pênaltis em andamento.

`INTERRUPTED` deverá indicar uma interrupção temporária durante a partida.

`SUSPENDED` deverá indicar suspensão com possibilidade de continuidade futura.

`POSTPONED` deverá indicar adiamento antes do encerramento esportivo.

`DELAYED` deverá indicar atraso, mantendo a intenção de início no mesmo contexto.

`ABANDONED` deverá indicar encerramento antecipado sem conclusão normal.

`CANCELLED` deverá indicar cancelamento definitivo antes da conclusão.

`WALKOVER` deverá indicar vitória por ausência ou impossibilidade do adversário.

`AWARDED` deverá indicar resultado atribuído administrativamente.

`FINISHED` deverá indicar encerramento no tempo regulamentar.

`AFTER_EXTRA_TIME` deverá indicar encerramento após prorrogação.

`AFTER_PENALTIES` deverá indicar encerramento após disputa por pênaltis.

`UNKNOWN` deverá ser utilizado apenas quando o status não puder ser determinado.

#### Relacionamentos principais

    Competition 1 ─── N Match
    Season      1 ─── N Match
    Stage       0..1 ─── N Match
    Round       0..1 ─── N Match

    Team 1 ─── N Match como mandante
    Team 1 ─── N Match como visitante

    Stadium 0..1 ─── N Match

    Match 1 ─── N MatchParticipant
    Match 1 ─── N MatchOfficial
    Match 1 ─── N LineupEntry
    Match 1 ─── N MatchEvent
    Match 1 ─── N MatchStatistic
    Match 1 ─── N BettingMarket
    Match 1 ─── N OddsSnapshot
    Match 1 ─── N Prediction

Os relacionamentos com competição, temporada, mandante e visitante deverão ser
obrigatórios em uma partida canônica confirmada.

Registros provisórios poderão ser preservados temporariamente durante a
resolução, mas não deverão ser publicados como partidas canônicas completas sem
essas relações.

#### Partida canônica e providers

Um provider poderá representar a mesma partida por um identificador próprio.

Exemplo:

    Provider A:
        fixture_id = 10025

    Provider B:
        event_id = 8f7d1

    Provider C:
        match_code = BRA-2026-001

Esses identificadores não deverão substituir `Match.id`.

A associação deverá ocorrer por meio de uma entidade de mapeamento externo.

Exemplo conceitual:

    ExternalEntityMapping
    ├── provider_id
    ├── entity_type
    ├── external_id
    ├── canonical_entity_id
    ├── first_seen_at
    ├── last_seen_at
    └── confidence_score

A partida canônica deverá permanecer estável mesmo quando um provider alterar
seu identificador externo.

#### Identidade inicial da partida

A identidade de uma partida não deverá depender apenas de:

    home_team_id
    away_team_id
    scheduled_start_at

Essa combinação poderá falhar em casos como:

- partidas remarcadas;
- confrontos repetidos no mesmo dia;
- torneios amistosos;
- jogos de ida e volta;
- partidas de equipes reservas;
- horários provisórios;
- registros sem horário;
- erros de provider;
- partidas anuladas e repetidas.

A resolução deverá considerar:

- competição;
- temporada;
- fase;
- rodada;
- mandante;
- visitante;
- data;
- horário;
- estádio;
- tipo de partida;
- identificadores externos;
- sequência do confronto;
- status;
- histórico de reagendamento.

#### Chave candidata inicial

Uma combinação candidata para detecção de duplicidade será:

    competition_id
    season_id
    home_team_id
    away_team_id
    scheduled_date
    round_id

Quando o horário for confiável, também poderá ser utilizado:

    scheduled_start_at

Essa combinação não deverá ser implementada imediatamente como uma restrição
única rígida.

A fusão definitiva deverá ser validada com dados reais de múltiplos providers.

#### Mandante e visitante

Os campos:

    home_team_id
    away_team_id

representam os papéis oficiais da partida.

Eles não deverão ser interpretados automaticamente como:

    equipe local
    equipe visitante fisicamente

Uma partida poderá ocorrer em campo neutro.

Exemplo:

    final disputada em estádio neutro

Nesse caso:

    home_team_id = equipe administrativamente mandante
    away_team_id = equipe administrativamente visitante
    is_neutral_venue = true

O papel de mandante poderá ser definido pelo regulamento, sorteio ou provider.

#### Equipes diferentes

As seguintes regras deverão ser respeitadas:

    home_team_id != away_team_id

Uma equipe não poderá disputar uma partida contra si mesma.

Equipes relacionadas, como:

    clube principal
    equipe reserva
    equipe sub-20
    equipe feminina

deverão possuir identidades canônicas distintas quando forem entidades
esportivas independentes.

#### Compatibilidade com competição e temporada

A temporada deverá pertencer à competição informada.

Regra esperada:

    season.competition_id = match.competition_id

Quando `stage_id` for informado:

    stage.season_id = match.season_id

ou deverá existir uma relação equivalente que comprove sua compatibilidade.

Quando `round_id` for informado:

    round.stage_id = match.stage_id

ou:

    round.season_id = match.season_id

conforme a estrutura definida para rodadas.

Incompatibilidades deverão ser rejeitadas ou encaminhadas para revisão.

#### Data e horário da partida

A aplicação deverá diferenciar:

    scheduled_date
    scheduled_start_at
    confirmed_start_at
    actual_start_at

`scheduled_date` poderá existir quando apenas o dia for conhecido.

`scheduled_start_at` deverá representar a programação inicial ou atualmente
publicada.

`confirmed_start_at` deverá representar o horário oficialmente confirmado.

`actual_start_at` deverá representar o início efetivo.

Exemplo:

    scheduled_start_at = 2026-07-10 20:00 UTC
    confirmed_start_at = 2026-07-10 20:30 UTC
    actual_start_at = 2026-07-10 20:37 UTC

Esses valores não deverão ser sobrescritos sem preservação histórica.

#### Fuso horário

Datas e horários persistidos deverão utilizar UTC.

O campo `timezone` deverá preservar o fuso local associado à programação
original.

Exemplo:

    scheduled_start_at = UTC
    timezone = America/Sao_Paulo

A exibição para o usuário deverá converter o horário conforme:

- fuso da partida;
- fuso do usuário;
- preferência da interface.

O horário local recebido do provider não deverá ser tratado como UTC sem
conversão explícita.

#### Data esportiva

Algumas competições consideram a rodada ou a data esportiva de forma diferente
do calendário UTC.

Exemplo:

    partida inicia às 00:30 no horário local
    provider anterior considera o evento como pertencente ao dia anterior

Por isso, `scheduled_date` poderá preservar a data esportiva oficial mesmo quando
o horário UTC estiver em outra data.

Essa diferença deverá ser documentada nos adaptadores de providers.

#### Reagendamento

Alterações de data e horário deverão preservar histórico.

O simples preenchimento de:

    is_rescheduled = true

não será suficiente para auditoria completa.

Futuramente, deverá existir uma entidade específica.

Exemplo conceitual:

    MatchScheduleChange
    ├── id
    ├── match_id
    ├── previous_start_at
    ├── new_start_at
    ├── previous_stadium_id
    ├── new_stadium_id
    ├── change_type
    ├── reason
    ├── announced_at
    ├── source_provider
    └── created_at

Tipos possíveis:

    DATE_CHANGE
    TIME_CHANGE
    VENUE_CHANGE
    POSTPONEMENT
    RESUMPTION
    CANCELLATION
    OTHER

A partida canônica deverá continuar utilizando o mesmo `Match.id` quando apenas
sua programação for alterada.

#### Partida adiada

Uma partida adiada deverá possuir:

    match_status = POSTPONED
    is_postponed = true

O horário anterior deverá ser preservado no histórico.

Quando uma nova data for definida, a mesma partida deverá ser atualizada.

Não deverá ser criada automaticamente uma nova `Match`.

Uma nova entidade somente deverá ser criada quando houver evidência de que o
evento original foi cancelado e substituído por uma partida distinta.

#### Partida atrasada

Uma partida atrasada deverá utilizar:

    match_status = DELAYED

O campo:

    is_postponed

deverá permanecer falso quando a partida ainda estiver prevista para iniciar no
mesmo contexto operacional.

Exemplo:

    início previsto para 20:00
    início atrasado para 20:45
    partida ainda ocorrerá no mesmo dia

#### Partida cancelada

Uma partida cancelada deverá possuir:

    match_status = CANCELLED
    is_cancelled = true

O registro não deverá ser removido.

Devem ser preservados:

- competição;
- temporada;
- equipes;
- programação anterior;
- motivo conhecido;
- provider de origem;
- mercados publicados;
- odds históricas;
- previsões já produzidas;
- momento do cancelamento.

Mercados e recomendações relacionados deverão ser invalidados conforme as regras
de apostas responsáveis.

#### Partida abandonada

Uma partida abandonada deverá possuir:

    match_status = ABANDONED
    is_abandoned = true

Ela poderá possuir:

- placar parcial;
- eventos registrados;
- escalações;
- estatísticas incompletas;
- horário de início;
- ausência de horário final normal.

A decisão administrativa posterior poderá:

- confirmar o placar;
- atribuir outro resultado;
- determinar continuação;
- determinar nova partida;
- anular o evento.

Essas decisões não deverão apagar os dados observados durante o jogo.

#### Partida suspensa

Uma partida suspensa deverá utilizar:

    match_status = SUSPENDED

A suspensão poderá ocorrer após o início.

O registro deverá permitir uma retomada futura.

Futuramente, poderá ser necessário armazenar:

    suspended_at
    resumed_at
    suspended_minute
    suspension_reason

Esses campos poderão existir em uma entidade de interrupções.

#### Interrupções

Interrupções temporárias não deverão alterar automaticamente a partida para
abandonada.

Exemplos:

- chuva;
- falha de iluminação;
- invasão de campo;
- atendimento médico;
- problema de segurança;
- análise prolongada do VAR;
- condições climáticas severas.

Uma estrutura futura poderá ser:

    MatchInterruption
    ├── id
    ├── match_id
    ├── interruption_type
    ├── started_at
    ├── ended_at
    ├── match_minute
    ├── reason
    ├── status
    └── source_provider

#### Placar principal

Os campos:

    home_score
    away_score

deverão representar o placar principal reconhecido no estado atual da partida.

Durante uma partida ao vivo, eles poderão representar o placar parcial.

Após o encerramento, deverão representar o placar oficial final, sem incluir
automaticamente a disputa por pênaltis.

Exemplo:

    resultado após prorrogação:
        home_score = 1
        away_score = 1

    disputa por pênaltis:
        home_penalty_score = 5
        away_penalty_score = 4

O placar por pênaltis deverá permanecer separado.

#### Placar no intervalo

Os campos:

    home_halftime_score
    away_halftime_score

deverão representar o placar no fim do primeiro tempo regulamentar.

Eles não deverão ser derivados apenas do placar atual quando o provider não
fornecer histórico suficiente.

A soma dos eventos de gol poderá ser utilizada como evidência, mas deverá
considerar:

- gols anulados;
- correções posteriores;
- gol contra;
- eventos duplicados;
- acréscimos;
- providers incompletos.

#### Prorrogação

Quando houver prorrogação:

    has_extra_time = true

O status final poderá ser:

    AFTER_EXTRA_TIME

Os campos:

    home_extra_time_score
    away_extra_time_score

deverão seguir uma convenção única.

A convenção recomendada será armazenar o placar total após a prorrogação.

Exemplo:

    tempo regulamentar: 1 x 1
    prorrogação: um gol do mandante
    placar após prorrogação: 2 x 1

Então:

    home_score = 2
    away_score = 1
    home_extra_time_score = 2
    away_extra_time_score = 1

Caso seja necessário armazenar apenas os gols marcados na prorrogação, deverá
existir uma entidade de períodos ou estatísticas separada.

#### Disputa por pênaltis

Quando houver disputa por pênaltis:

    has_penalty_shootout = true

O status final deverá ser:

    AFTER_PENALTIES

Os campos:

    home_penalty_score
    away_penalty_score

deverão representar apenas o resultado da disputa.

Eles não deverão ser somados a:

    home_score
    away_score

Exemplo:

    placar esportivo = 1 x 1
    pênaltis = 5 x 4

#### Vencedor

`winner_team_id` deverá ser preenchido somente quando houver um vencedor
definido.

Valores válidos:

    home_team_id
    away_team_id
    null

O valor nulo poderá representar:

- empate;
- partida não iniciada;
- partida em andamento;
- partida cancelada;
- resultado ainda indefinido;
- decisão administrativa pendente.

Quando o resultado for decidido por pênaltis, `winner_team_id` deverá considerar
a disputa.

Quando houver resultado administrativo, o vencedor deverá refletir a decisão
oficial.

#### Resultado administrativo

Partidas com resultado atribuído administrativamente deverão utilizar:

    match_status = AWARDED

Poderão existir placares como:

    3 x 0
    0 x 3

mesmo sem a partida ter sido disputada normalmente.

A origem do resultado deverá ser preservada.

Futuramente, poderá existir:

    MatchDecision
    ├── id
    ├── match_id
    ├── decision_type
    ├── home_score
    ├── away_score
    ├── winner_team_id
    ├── reason
    ├── decided_at
    ├── governing_body
    └── source_provider

#### Walkover

Uma vitória por ausência deverá utilizar:

    match_status = WALKOVER

O placar poderá ser informado quando definido pelo regulamento.

A partida não deverá ser tratada como uma partida disputada normalmente para
estatísticas de desempenho esportivo.

Modelos analíticos deverão ser capazes de excluir:

- walkovers;
- resultados administrativos;
- jogos cancelados;
- partidas abandonadas sem resultado confirmado.

#### Duração

O campo `duration_minutes` deverá representar a duração esportiva reconhecida.

Valores comuns:

    90
    120

Entretanto, partidas de categorias de base, amistosos ou torneios especiais
poderão possuir durações diferentes.

Não deverá existir uma validação universal rígida impondo apenas 90 ou 120
minutos.

#### Acréscimos

Os campos:

    stoppage_time_first_half
    stoppage_time_second_half

deverão representar os acréscimos oficialmente indicados, quando conhecidos.

Eles não deverão ser usados isoladamente para calcular o momento exato de todos
os eventos.

Eventos deverão armazenar:

    minute
    added_time
    period

Exemplo:

    minute = 45
    added_time = 3
    period = FIRST_HALF

#### Público

`attendance` deverá representar o público oficialmente informado.

O valor deverá ser:

    attendance >= 0

O valor zero deverá ser diferente de valor desconhecido.

Portanto:

    0 = partida oficialmente sem público
    null = informação desconhecida

Capacidade do estádio e público não deverão ser confundidos.

#### Local neutro

Quando:

    is_neutral_venue = true

o estádio não deverá ser interpretado como campo habitual do mandante.

Esse campo será relevante para:

- análise de vantagem de mando;
- modelos de previsão;
- estatísticas de desempenho;
- viagens;
- competições centralizadas;
- finais;
- torneios internacionais.

A condição de campo neutro deverá vir de fonte confiável ou regra da competição.

#### Estádio desconhecido

Uma partida poderá ser criada sem `stadium_id` quando:

- o local ainda não foi definido;
- o provider não informou;
- a partida foi transferida;
- a competição utiliza local confidencial;
- a resolução do estádio ainda está pendente.

A ausência do estádio não deverá impedir a criação da partida, desde que os
demais elementos essenciais estejam resolvidos.

#### Mudança de estádio

Uma mudança de local não deverá criar uma nova partida.

O valor atual de `stadium_id` poderá ser atualizado, mas o valor anterior deverá
ser preservado no histórico de alterações.

A alteração poderá afetar:

- vantagem de mando;
- capacidade;
- altitude;
- clima;
- distância;
- qualidade do gramado;
- análises estatísticas;
- mercados de apostas.

#### Regras de integridade

- `competition_id` deverá referenciar uma competição existente;
- `season_id` deverá referenciar uma temporada existente;
- `stage_id`, quando informado, deverá referenciar uma fase existente;
- `round_id`, quando informado, deverá referenciar uma rodada existente;
- `home_team_id` deverá referenciar uma equipe existente;
- `away_team_id` deverá referenciar uma equipe existente;
- `stadium_id`, quando informado, deverá referenciar um estádio existente;
- `home_team_id` não poderá ser igual a `away_team_id`;
- `season_id` deverá ser compatível com `competition_id`;
- `stage_id` deverá ser compatível com a temporada;
- `round_id` deverá ser compatível com a fase ou temporada;
- `match_type` deverá possuir valor válido;
- `match_status` deverá possuir valor válido;
- placares, quando informados, deverão ser maiores ou iguais a zero;
- `attendance`, quando informado, deverá ser maior ou igual a zero;
- `duration_minutes`, quando informado, deverá ser maior que zero;
- acréscimos, quando informados, deverão ser maiores ou iguais a zero;
- `actual_end_at`, quando informado, deverá ser posterior a `actual_start_at`;
- `halftime_at`, quando informado, deverá ser posterior a `actual_start_at`;
- `halftime_at`, quando informado, deverá ser anterior a `actual_end_at`;
- `winner_team_id`, quando informado, deverá ser igual ao mandante ou visitante;
- `home_penalty_score` e `away_penalty_score` deverão ser informados em conjunto;
- placares de prorrogação deverão ser compatíveis com `has_extra_time`;
- placares de pênaltis deverão ser compatíveis com `has_penalty_shootout`;
- `is_cancelled = true` deverá ser compatível com status de cancelamento;
- `is_abandoned = true` deverá ser compatível com status de abandono;
- `is_postponed = true` deverá ser compatível com status de adiamento;
- `rescheduled_from_match_id` não poderá apontar para a própria partida;
- partidas históricas não deverão ser removidas fisicamente;
- atualizações de placar não deverão apagar eventos já recebidos;
- conflitos entre providers deverão ser preservados para resolução.

#### Consistência entre status e campos booleanos

Os campos booleanos deverão ser consistentes com o status.

Exemplos:

    match_status = POSTPONED
    is_postponed = true

    match_status = CANCELLED
    is_cancelled = true

    match_status = ABANDONED
    is_abandoned = true

    match_status = AFTER_EXTRA_TIME
    has_extra_time = true

    match_status = AFTER_PENALTIES
    has_penalty_shootout = true

Esses campos poderão ser derivados, mas poderão permanecer armazenados para
facilitar consultas.

Rotinas de validação deverão identificar divergências.

#### Transições de status

As transições deverão seguir uma máquina de estados controlada.

Fluxo regular:

    SCHEDULED
        ↓
    CONFIRMED
        ↓
    PRE_MATCH
        ↓
    FIRST_HALF
        ↓
    HALFTIME
        ↓
    SECOND_HALF
        ↓
    FINISHED

Fluxo com prorrogação:

    SECOND_HALF
        ↓
    EXTRA_TIME
        ↓
    EXTRA_TIME_HALFTIME
        ↓
    EXTRA_TIME
        ↓
    AFTER_EXTRA_TIME

Fluxo com pênaltis:

    EXTRA_TIME
        ↓
    PENALTY_SHOOTOUT
        ↓
    AFTER_PENALTIES

Fluxo de adiamento:

    SCHEDULED
        ↓
    POSTPONED
        ↓
    SCHEDULED ou CONFIRMED

Fluxo de atraso:

    CONFIRMED
        ↓
    DELAYED
        ↓
    PRE_MATCH ou FIRST_HALF

Fluxo de interrupção:

    FIRST_HALF ou SECOND_HALF
        ↓
    INTERRUPTED
        ↓
    estado anterior

Fluxo de suspensão:

    FIRST_HALF ou SECOND_HALF
        ↓
    SUSPENDED
        ↓
    retomada ou ABANDONED

Nem toda transição inválida deverá ser rejeitada imediatamente.

Providers podem enviar estados fora de ordem.

O sistema deverá:

- preservar a observação;
- considerar o horário da observação;
- comparar a confiabilidade da fonte;
- evitar regressões incorretas;
- permitir correções auditáveis.

#### Regressão de status

Um provider poderá enviar:

    FINISHED

e posteriormente:

    SECOND_HALF

Essa regressão poderá representar:

- evento atrasado;
- cache antigo;
- erro do provider;
- correção da partida;
- mudança administrativa.

O status canônico não deverá regredir automaticamente com base apenas na última
mensagem recebida.

A fusão deverá considerar:

- ordem temporal;
- prioridade do provider;
- confiabilidade;
- status atual;
- evidências de eventos;
- placar;
- horário efetivo;
- decisão oficial.

#### Partidas futuras

Partidas futuras poderão não possuir:

    horário confirmado
    estádio
    rodada
    fase
    árbitros
    escalações

Esses campos deverão permanecer nulos até que existam dados confiáveis.

O sistema não deverá inventar valores para completar o registro.

#### Partidas ao vivo

Partidas ao vivo exigirão atualizações frequentes.

O registro canônico deverá suportar:

- atualização de status;
- atualização de placar;
- atualização de minuto;
- eventos;
- escalações;
- estatísticas parciais;
- odds ao vivo;
- suspensões;
- correções.

O minuto atual não deverá ser armazenado apenas em `Match`.

Futuramente, poderá existir um estado ao vivo.

Exemplo:

    MatchLiveState
    ├── match_id
    ├── period
    ├── minute
    ├── added_time
    ├── clock_status
    ├── possession_status
    ├── last_event_at
    └── updated_at

#### Partidas finalizadas

Uma partida finalizada deverá possuir, quando disponível:

    actual_start_at
    actual_end_at
    home_score
    away_score
    match_status final

Dependendo do contexto, também poderá possuir:

    halftime scores
    extra time scores
    penalty scores
    attendance
    winner_team_id
    officials
    lineups
    events
    statistics

A ausência de dados secundários não deverá impedir a finalização da partida.

#### Partidas incompletas

Providers poderão informar partidas incompletas.

Exemplo:

    competição conhecida
    equipes conhecidas
    data conhecida
    horário desconhecido

O registro poderá ser criado com:

    scheduled_date preenchido
    scheduled_start_at = null
    match_status = DATE_DEFINED

Outro exemplo:

    equipes conhecidas
    data desconhecida
    rodada conhecida

Esse registro poderá permanecer na camada de resolução até que haja informação
mínima suficiente para publicação canônica.

#### Resolução de duplicidade

A resolução de duplicidade deverá considerar:

- competição;
- temporada;
- fase;
- rodada;
- mandante;
- visitante;
- data programada;
- horário programado;
- estádio;
- tipo;
- identificadores externos;
- histórico de alterações;
- status;
- origem;
- confiança.

Comparações de nomes de equipes deverão ocorrer antes da criação da partida.

A resolução correta será:

    provider team
        ↓
    Team canônica
        ↓
    Match candidate

A partida não deverá ser criada utilizando nomes textuais soltos de equipes.

#### Confrontos invertidos

Providers poderão inverter mandante e visitante por erro ou diferença de
representação.

Exemplo:

    Provider A:
        Team A x Team B

    Provider B:
        Team B x Team A

A resolução não deverá considerar automaticamente os dois registros iguais.

Deverão ser verificados:

- regra da competição;
- estádio;
- mando oficial;
- rodada;
- data;
- provider confiável;
- identificadores externos.

Em partidas de campo neutro, a inversão ainda poderá ser relevante para:

- mercados;
- escalações;
- placar;
- estatísticas;
- regulamentação.

#### Partidas de ida e volta

Confrontos de ida e volta deverão gerar partidas diferentes.

Exemplo:

    ida:
        Team A x Team B

    volta:
        Team B x Team A

Mesmo quando ocorrerem na mesma fase, deverão possuir:

    Match.id distintos

A relação agregada poderá ser representada futuramente por:

    Tie
    ├── id
    ├── competition_id
    ├── season_id
    ├── stage_id
    ├── home_team_id
    ├── away_team_id
    ├── aggregate_home_score
    ├── aggregate_away_score
    └── winner_team_id

#### Partida repetida

Uma partida poderá ser anulada e repetida.

Nesse caso, poderão existir duas entidades `Match`.

Exemplo:

    partida original:
        status = ABANDONED ou CANCELLED

    nova partida:
        status = SCHEDULED

A relação poderá ser registrada por:

    rescheduled_from_match_id

ou por uma estrutura futura:

    MatchRelation
    ├── source_match_id
    ├── target_match_id
    ├── relation_type
    └── reason

Tipos possíveis:

    REPLAY_OF
    RESCHEDULED_FROM
    REPLACEMENT_FOR
    CONTINUATION_OF
    RELATED_FIXTURE

#### Continuação de partida suspensa

Uma partida suspensa e retomada poderá continuar utilizando o mesmo `Match.id`.

Quando a competição tratar a retomada como continuação oficial, deverão ser
preservados:

- placar anterior;
- minuto da suspensão;
- eventos anteriores;
- escalações;
- cartões;
- substituições;
- horário da retomada.

Uma nova `Match` somente deverá ser criada se a organização considerar o evento
uma nova partida oficial.

#### Relação com mercados de apostas

Todos os mercados deverão referenciar a partida canônica.

Exemplo:

    BettingMarket
    ├── match_id
    ├── market_type
    ├── period
    ├── line
    └── status

Odds recebidas antes da resolução da partida deverão permanecer associadas ao
identificador externo até que o mapeamento canônico seja confirmado.

Nenhuma odd deverá ser associada a uma partida apenas por similaridade textual
fraca.

#### Correções após o encerramento

Placares e status poderão ser corrigidos após o encerramento.

Exemplos:

- gol atribuído a outro jogador;
- cartão corrigido;
- resultado administrativo;
- partida anulada;
- punição posterior;
- placar alterado pela organização.

A aplicação deverá permitir correções auditáveis.

O valor anterior não deverá ser apagado sem histórico.

Futuramente, poderá existir:

    MatchRevision
    ├── match_id
    ├── field_name
    ├── previous_value
    ├── new_value
    ├── revision_reason
    ├── source_provider
    ├── revised_at
    └── approved_by

#### Proveniência

O campo `source_provider` poderá representar temporariamente a origem principal.

A arquitetura definitiva deverá utilizar estruturas como:

    ExternalEntityMapping
    EntitySource
    ProviderObservation
    CanonicalFieldValue
    ConflictRecord

Cada campo crítico poderá possuir múltiplas observações.

Exemplos:

    horário
    status
    estádio
    placar
    público
    árbitro
    vencedor

A fusão deverá selecionar o valor canônico sem descartar as observações
divergentes.

#### Confiança

O campo `confidence_score` poderá variar conceitualmente entre:

    0.0
    1.0

O valor deverá representar confiança na identidade e consistência do registro,
não a probabilidade de um resultado esportivo.

Exemplo:

    1.0
        partida confirmada por fonte oficial

    0.8
        múltiplos providers confiáveis concordam

    0.5
        registro parcial com algumas divergências

    0.2
        possível duplicidade ou contexto incompleto

Probabilidades esportivas deverão permanecer em entidades de previsão.

#### Índices recomendados para Match

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_competition_id` | `competition_id` | Buscar partidas por competição. |
| `ix_match_season_id` | `season_id` | Buscar partidas por temporada. |
| `ix_match_stage_id` | `stage_id` | Buscar partidas por fase. |
| `ix_match_round_id` | `round_id` | Buscar partidas por rodada. |
| `ix_match_home_team_id` | `home_team_id` | Buscar partidas como mandante. |
| `ix_match_away_team_id` | `away_team_id` | Buscar partidas como visitante. |
| `ix_match_stadium_id` | `stadium_id` | Buscar partidas por estádio. |
| `ix_match_status` | `match_status` | Filtrar pelo status. |
| `ix_match_type` | `match_type` | Filtrar pelo tipo. |
| `ix_match_scheduled_start_at` | `scheduled_start_at` | Consultar calendário por horário. |
| `ix_match_scheduled_date` | `scheduled_date` | Consultar calendário por data. |
| `ix_match_actual_start_at` | `actual_start_at` | Consultar início efetivo. |
| `ix_match_competition_date` | `competition_id, scheduled_start_at` | Buscar calendário da competição. |
| `ix_match_season_date` | `season_id, scheduled_start_at` | Buscar calendário da temporada. |
| `ix_match_round_date` | `round_id, scheduled_start_at` | Buscar partidas de uma rodada. |
| `ix_match_home_date` | `home_team_id, scheduled_start_at` | Consultar jogos do mandante. |
| `ix_match_away_date` | `away_team_id, scheduled_start_at` | Consultar jogos do visitante. |
| `ix_match_status_date` | `match_status, scheduled_start_at` | Buscar partidas por status e horário. |
| `ix_match_teams_date` | `home_team_id, away_team_id, scheduled_start_at` | Apoiar resolução de duplicidade. |
| `ix_match_winner_team_id` | `winner_team_id` | Buscar partidas vencidas por equipe. |

Índices simples sobre campos booleanos poderão apresentar baixa seletividade.

Índices parciais poderão ser mais eficientes.

Exemplo para partidas futuras:

    INDEX ON match (
        scheduled_start_at,
        competition_id
    )
    WHERE match_status IN (
        'SCHEDULED',
        'DATE_DEFINED',
        'TIME_UNCONFIRMED',
        'CONFIRMED',
        'POSTPONED'
    )

Exemplo para partidas ao vivo:

    INDEX ON match (
        match_status,
        actual_start_at
    )
    WHERE match_status IN (
        'PRE_MATCH',
        'WARMUP',
        'FIRST_HALF',
        'HALFTIME',
        'SECOND_HALF',
        'EXTRA_TIME',
        'PENALTY_SHOOTOUT',
        'INTERRUPTED'
    )

Exemplo para partidas finalizadas:

    INDEX ON match (
        competition_id,
        actual_end_at
    )
    WHERE match_status IN (
        'FINISHED',
        'AFTER_EXTRA_TIME',
        'AFTER_PENALTIES',
        'WALKOVER',
        'AWARDED'
    )

#### Restrições recomendadas

As seguintes restrições deverão existir:

    CHECK home_team_id <> away_team_id

    CHECK home_score >= 0
    CHECK away_score >= 0

    CHECK home_halftime_score >= 0
    CHECK away_halftime_score >= 0

    CHECK home_extra_time_score >= 0
    CHECK away_extra_time_score >= 0

    CHECK home_penalty_score >= 0
    CHECK away_penalty_score >= 0

    CHECK attendance >= 0

    CHECK duration_minutes > 0

Essas restrições deverão aceitar valores nulos quando a informação não estiver
disponível.

A validação de compatibilidade entre:

    competition
    season
    stage
    round

poderá exigir regras de aplicação ou triggers, dependendo do modelo físico.

#### Restrição de vencedor

Quando `winner_team_id` for informado, deverá ser validado:

    winner_team_id = home_team_id
    OR
    winner_team_id = away_team_id

Empates deverão possuir:

    winner_team_id = null

Partidas não concluídas também deverão normalmente possuir vencedor nulo.

#### Restrição de pênaltis

Quando um placar de pênaltis for informado:

    home_penalty_score IS NOT NULL
    away_penalty_score IS NOT NULL
    has_penalty_shootout = true

Quando:

    has_penalty_shootout = false

os placares de pênaltis deverão ser nulos, salvo registro provisório em processo
de correção.

#### Regra inicial de unicidade

Não deverá ser criada inicialmente uma restrição única rígida apenas sobre:

    competition_id
    season_id
    home_team_id
    away_team_id
    scheduled_start_at

Essa combinação poderá falhar em casos legítimos.

A primeira versão deverá utilizar:

- mapeamento externo único por provider;
- serviço de resolução de identidade;
- detecção de candidatos;
- pontuação de similaridade;
- revisão de conflitos;
- fusão controlada.

Após análise de dados reais, poderá ser criada uma restrição parcial ou
contextual.

#### Dependências futuras

A entidade `Match` será utilizada por:

- participantes da partida;
- mandante e visitante;
- estádios;
- árbitros;
- escalações;
- bancos de reservas;
- eventos;
- gols;
- cartões;
- substituições;
- estatísticas;
- posse de bola;
- finalizações;
- impedimentos;
- faltas;
- odds;
- mercados de apostas;
- probabilidades;
- previsões;
- recomendações;
- análises ao vivo;
- histórico de resultados;
- desempenho de equipes;
- desempenho de jogadores;
- cálculo de forma recente;
- modelos de machine learning;
- auditoria de providers.

Por isso, sua identidade, status, calendário e resultado deverão ser tratados
como dados canônicos de alta criticidade.
---

### 8.2 MatchParticipant

A entidade `MatchParticipant` representa a participação contextual de uma equipe
em uma partida.

Ela deverá complementar os campos rápidos existentes em `Match`:

    home_team_id
    away_team_id

Esses campos permanecerão em `Match` para consultas frequentes e compatibilidade
com o formato tradicional do futebol.

Entretanto, `MatchParticipant` deverá ser utilizada quando for necessário
representar informações específicas de cada participante.

Exemplo conceitual:

    Match
    ├── MatchParticipant
    │   ├── Team A
    │   └── Team B
    ├── MatchOfficial
    ├── LineupEntry
    ├── MatchEvent
    └── MatchStatistic

Na maioria das partidas de futebol existirão exatamente dois participantes.

A modelagem extensível permitirá representar corretamente:

- mandante;
- visitante;
- campo neutro;
- equipes administrativamente designadas;
- placares por participante;
- classificação no confronto;
- eliminação;
- avanço de fase;
- walkover;
- resultado administrativo;
- disputa por pênaltis;
- confrontos agregados;
- participantes ainda não definidos.

#### Responsabilidades

A entidade `MatchParticipant` será responsável por:

- relacionar uma equipe à partida;
- indicar o papel oficial do participante;
- indicar sua ordem na partida;
- armazenar placares contextuais;
- indicar o resultado esportivo;
- indicar classificação ou eliminação;
- indicar avanço de fase;
- representar participante ainda indefinido;
- preservar resultados administrativos;
- representar condição de walkover;
- apoiar confrontos de ida e volta;
- apoiar fases eliminatórias;
- servir como referência para escalações;
- servir como referência para estatísticas;
- servir como referência para mercados de apostas;
- preservar proveniência e confiança.

#### Campos principais

    id
    match_id
    team_id
    participant_role
    participant_order
    participant_status
    result_status
    score
    halftime_score
    extra_time_score
    penalty_score
    aggregate_score
    previous_leg_score
    awarded_score
    ranking_position_before
    ranking_position_after
    seed_number
    group_position
    qualification_status
    elimination_status
    advancement_status
    is_winner
    is_home_designation
    is_away_designation
    is_neutral
    is_walkover_winner
    is_walkover_loser
    is_disqualified
    is_tbd
    placeholder_name
    source_provider
    confidence_score
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno e canônico da participação. |
| `match_id` | UUID | Sim | Partida relacionada ao participante. |
| `team_id` | UUID | Não | Equipe canônica participante, quando já definida. |
| `participant_role` | enum | Sim | Papel oficial do participante na partida. |
| `participant_order` | integer | Sim | Ordem estável do participante dentro da partida. |
| `participant_status` | enum | Sim | Situação da participação na partida. |
| `result_status` | enum | Não | Resultado esportivo ou administrativo do participante. |
| `score` | integer | Não | Placar principal atribuído ao participante. |
| `halftime_score` | integer | Não | Placar do participante no intervalo. |
| `extra_time_score` | integer | Não | Placar total do participante após prorrogação. |
| `penalty_score` | integer | Não | Gols do participante na disputa por pênaltis. |
| `aggregate_score` | integer | Não | Placar agregado do participante em confronto de múltiplas partidas. |
| `previous_leg_score` | integer | Não | Placar acumulado anterior à partida atual. |
| `awarded_score` | integer | Não | Placar administrativo atribuído ao participante. |
| `ranking_position_before` | integer | Não | Posição do participante antes da partida. |
| `ranking_position_after` | integer | Não | Posição do participante após a partida. |
| `seed_number` | integer | Não | Cabeça de chave ou posição de sorteio. |
| `group_position` | integer | Não | Posição do participante em grupo ou chave. |
| `qualification_status` | enum | Não | Situação de classificação relacionada à partida. |
| `elimination_status` | enum | Não | Situação de eliminação relacionada à partida. |
| `advancement_status` | enum | Não | Situação de avanço para fase seguinte. |
| `is_winner` | boolean | Sim | Indica se o participante venceu a partida. |
| `is_home_designation` | boolean | Sim | Indica designação administrativa como mandante. |
| `is_away_designation` | boolean | Sim | Indica designação administrativa como visitante. |
| `is_neutral` | boolean | Sim | Indica participação em contexto de local neutro. |
| `is_walkover_winner` | boolean | Sim | Indica vitória por walkover. |
| `is_walkover_loser` | boolean | Sim | Indica derrota por walkover. |
| `is_disqualified` | boolean | Sim | Indica desclassificação administrativa. |
| `is_tbd` | boolean | Sim | Indica participante ainda não definido. |
| `placeholder_name` | string | Não | Descrição temporária do participante indefinido. |
| `source_provider` | string | Não | Provider principal que originou o registro. |
| `confidence_score` | decimal | Não | Nível de confiança da participação canônica. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Papéis de participante previstos

    HOME
    AWAY
    NEUTRAL_HOME
    NEUTRAL_AWAY
    ADMINISTRATIVE_HOME
    ADMINISTRATIVE_AWAY
    PARTICIPANT_1
    PARTICIPANT_2
    TBD_HOME
    TBD_AWAY
    OTHER
    UNKNOWN

O valor `HOME` deverá representar a equipe oficialmente registrada como
mandante.

O valor `AWAY` deverá representar a equipe oficialmente registrada como
visitante.

Os valores `NEUTRAL_HOME` e `NEUTRAL_AWAY` poderão ser utilizados quando a
partida ocorrer em campo neutro, mas os papéis administrativos de mandante e
visitante permanecerem definidos.

Os valores `ADMINISTRATIVE_HOME` e `ADMINISTRATIVE_AWAY` poderão ser utilizados
quando a designação existir apenas por regulamento, sorteio ou organização.

Os valores `PARTICIPANT_1` e `PARTICIPANT_2` poderão ser usados em contextos nos
quais o provider não utiliza conceitos explícitos de mandante e visitante.

Os valores `TBD_HOME` e `TBD_AWAY` poderão representar participantes ainda não
definidos.

A utilização desses valores deverá ser normalizada para `HOME` ou `AWAY` quando
a definição oficial se tornar disponível.

#### Status de participação previstos

    EXPECTED
    CONFIRMED
    ACTIVE
    WITHDRAWN
    DISQUALIFIED
    REPLACED
    WALKOVER
    CANCELLED
    COMPLETED
    UNKNOWN

O status `EXPECTED` deverá indicar participante previsto, mas ainda não
confirmado.

O status `CONFIRMED` deverá indicar equipe oficialmente definida para a partida.

O status `ACTIVE` deverá indicar participação válida em partida em andamento.

O status `WITHDRAWN` deverá indicar retirada voluntária ou administrativa.

O status `DISQUALIFIED` deverá indicar desclassificação.

O status `REPLACED` deverá indicar substituição por outro participante.

O status `WALKOVER` deverá indicar participação afetada por ausência ou
impossibilidade de disputa.

O status `CANCELLED` deverá indicar que a participação deixou de existir devido
ao cancelamento da partida ou alteração da chave.

O status `COMPLETED` deverá indicar participação concluída.

#### Resultados previstos

    WIN
    DRAW
    LOSS
    WALKOVER_WIN
    WALKOVER_LOSS
    AWARDED_WIN
    AWARDED_LOSS
    QUALIFIED
    ELIMINATED
    NO_RESULT
    CANCELLED
    UNKNOWN

O valor `WIN` deverá indicar vitória esportiva na partida.

O valor `DRAW` deverá indicar empate no resultado principal.

O valor `LOSS` deverá indicar derrota esportiva.

Os valores `WALKOVER_WIN` e `WALKOVER_LOSS` deverão indicar resultado por
ausência ou impossibilidade de disputa.

Os valores `AWARDED_WIN` e `AWARDED_LOSS` deverão indicar decisão
administrativa.

Os valores `QUALIFIED` e `ELIMINATED` poderão ser utilizados quando a informação
principal disponível estiver relacionada ao confronto eliminatório.

O valor `NO_RESULT` deverá indicar ausência de resultado válido.

#### Status de classificação previstos

    QUALIFIED
    CONDITIONALLY_QUALIFIED
    NOT_QUALIFIED
    QUALIFICATION_PENDING
    QUALIFICATION_CANCELLED
    NOT_APPLICABLE
    UNKNOWN

A classificação deverá representar o estado do participante em relação a uma
fase, competição ou critério específico.

Ela não deverá ser inferida apenas pelo resultado isolado da partida quando o
contexto depender de:

- saldo de gols;
- placar agregado;
- gols fora de casa;
- disputa por pênaltis;
- classificação do grupo;
- critérios disciplinares;
- decisão administrativa;
- resultados de outras partidas.

#### Status de eliminação previstos

    NOT_ELIMINATED
    ELIMINATED
    ELIMINATION_PENDING
    REINSTATED
    DISQUALIFIED
    NOT_APPLICABLE
    UNKNOWN

O status `ELIMINATED` deverá indicar que o participante não continuará na
competição ou fase.

O status `REINSTATED` poderá representar uma equipe anteriormente eliminada ou
desclassificada que retornou por decisão administrativa.

A eliminação deverá permanecer separada do resultado da partida.

Uma equipe poderá vencer uma partida e ainda assim ser eliminada no placar
agregado.

#### Status de avanço previstos

    ADVANCED
    DID_NOT_ADVANCE
    ADVANCEMENT_PENDING
    ADVANCED_BY_BYE
    ADVANCED_BY_WALKOVER
    ADVANCED_BY_ADMINISTRATIVE_DECISION
    NOT_APPLICABLE
    UNKNOWN

O avanço deverá indicar progressão para outra fase.

Uma equipe poderá avançar por:

- vitória na partida;
- placar agregado;
- disputa por pênaltis;
- bye;
- walkover;
- decisão administrativa.

A causa do avanço deverá ser preservada quando conhecida.

#### Relacionamentos principais

    Match 1 ─── N MatchParticipant
    Team  0..1 ─── N MatchParticipant

    MatchParticipant 1 ─── N LineupEntry
    MatchParticipant 1 ─── N MatchStatistic
    MatchParticipant 1 ─── N MatchEvent
    MatchParticipant 1 ─── N BettingSelection

Cada partida de futebol deverá possuir normalmente dois registros em
`MatchParticipant`.

Exemplo:

    MatchParticipant A:
        participant_role = HOME

    MatchParticipant B:
        participant_role = AWAY

A relação com `Team` poderá permanecer nula quando o participante ainda estiver
indefinido.

#### Compatibilidade com Match

Quando os participantes estiverem definidos:

    participante HOME.team_id = match.home_team_id

e:

    participante AWAY.team_id = match.away_team_id

A aplicação deverá impedir divergências entre:

    Match.home_team_id
    MatchParticipant HOME

e:

    Match.away_team_id
    MatchParticipant AWAY

Os campos em `Match` deverão ser considerados atalhos canônicos para os dois
participantes principais.

`MatchParticipant` deverá ser considerada a estrutura contextual detalhada.

#### Redundância controlada

Os seguintes dados poderão existir tanto em `Match` quanto em
`MatchParticipant`:

    equipes
    placares
    vencedor
    condição de mandante
    condição de visitante

Essa redundância será aceita para:

- consultas rápidas;
- compatibilidade com APIs;
- desempenho;
- clareza do agregado;
- integração com providers.

Entretanto, deverá existir uma única regra de atualização.

Exemplo:

    atualização canônica da partida
        ↓
    atualização de Match
        ↓
    sincronização de MatchParticipant

Não deverá existir atualização independente sem validação entre as entidades.

#### Participante ainda não definido

Uma partida futura poderá ser criada antes da definição de uma ou ambas as
equipes.

Exemplos:

    vencedor da semifinal 1
    segundo colocado do grupo A
    vencedor do confronto 25
    equipe classificada pela repescagem

Nesse caso:

    team_id = null
    is_tbd = true
    participant_status = EXPECTED
    placeholder_name preenchido

Exemplo:

    placeholder_name = "Vencedor da semifinal 1"

O placeholder não deverá criar uma entidade `Team` falsa.

Quando a equipe for definida:

    team_id deverá ser preenchido
    is_tbd deverá ser alterado para false
    participant_status deverá ser atualizado
    placeholder_name poderá ser preservado no histórico

#### Placeholders estruturados

O campo textual `placeholder_name` poderá ser utilizado inicialmente.

Futuramente, deverá existir uma estrutura mais precisa.

Exemplo conceitual:

    MatchParticipantSource
    ├── match_participant_id
    ├── source_type
    ├── source_match_id
    ├── source_group_id
    ├── source_position
    ├── source_stage_id
    └── resolution_status

Tipos possíveis:

    WINNER_OF_MATCH
    LOSER_OF_MATCH
    GROUP_POSITION
    BEST_RANKED_TEAM
    QUALIFIER_WINNER
    DRAW_SLOT
    ADMINISTRATIVE_SELECTION
    UNKNOWN

Isso permitirá resolver automaticamente os participantes quando os resultados
anteriores forem conhecidos.

#### Ordem dos participantes

O campo `participant_order` deverá ser estável dentro da partida.

Para partidas tradicionais:

    HOME = 1
    AWAY = 2

A ordem não deverá depender da ordem em que o provider enviou os participantes.

Ela deverá ser definida após normalização.

Quando um provider fornecer uma lista sem papéis explícitos, a ordem original
poderá ser preservada temporariamente, mas deverá ser validada antes da fusão
canônica.

#### Regras de quantidade

Uma partida regular de futebol deverá possuir:

    exatamente dois participantes confirmados

Entretanto, durante a criação ou resolução poderão existir:

    zero participantes definidos
    um participante definido
    dois participantes esperados

Mais de dois participantes não deverão ser permitidos em uma partida de futebol
tradicional.

Caso um provider represente um grupo, chave ou evento com múltiplas equipes como
se fosse uma partida, esse registro deverá ser normalizado para outra entidade.

#### Papéis exclusivos

Dentro da mesma partida deverá existir no máximo:

    um participante HOME
    um participante AWAY

Também deverá existir no máximo:

    um is_home_designation = true
    um is_away_designation = true

O mesmo participante não poderá possuir simultaneamente:

    is_home_designation = true
    is_away_designation = true

Os papéis deverão ser consistentes com `participant_order`.

#### Campo neutro

Em uma partida de campo neutro, os participantes ainda poderão possuir papéis de
mandante e visitante.

Exemplo:

    Match.is_neutral_venue = true

    MatchParticipant A:
        participant_role = NEUTRAL_HOME
        is_home_designation = true
        is_neutral = true

    MatchParticipant B:
        participant_role = NEUTRAL_AWAY
        is_away_designation = true
        is_neutral = true

O campo `is_neutral` deverá indicar o contexto do participante, não ausência de
papel administrativo.

#### Placar por participante

O campo `score` deverá ser compatível com:

    Match.home_score
    Match.away_score

Para o participante mandante:

    MatchParticipant.score = Match.home_score

Para o visitante:

    MatchParticipant.score = Match.away_score

A mesma regra deverá ser aplicada para:

    halftime_score
    extra_time_score
    penalty_score

Essa duplicidade deverá ser validada automaticamente.

#### Placar no intervalo

Para o participante mandante:

    MatchParticipant.halftime_score =
        Match.home_halftime_score

Para o participante visitante:

    MatchParticipant.halftime_score =
        Match.away_halftime_score

Valores nulos deverão representar informação desconhecida.

O valor zero deverá representar placar oficialmente igual a zero.

#### Placar após prorrogação

O campo `extra_time_score` deverá seguir a mesma convenção definida em `Match`.

A convenção recomendada será:

    placar total após a prorrogação

Ele não deverá representar apenas os gols marcados durante o período extra.

Exemplo:

    tempo regulamentar = 1 x 1
    após prorrogação = 2 x 1

Participante mandante:

    score = 2
    extra_time_score = 2

Participante visitante:

    score = 1
    extra_time_score = 1

#### Disputa por pênaltis

O campo `penalty_score` deverá representar apenas os gols marcados na disputa
por pênaltis.

Ele não deverá ser somado ao placar principal.

Exemplo:

    score = 1 x 1
    penalty_score = 5 x 4

O vencedor deverá ser determinado considerando a disputa quando:

    Match.match_status = AFTER_PENALTIES

#### Placar agregado

O campo `aggregate_score` poderá representar o placar total do participante em
um confronto de ida e volta ou série de partidas.

Exemplo:

    partida de ida:
        Team A 1 x 0 Team B

    partida de volta:
        Team B 2 x 0 Team A

Na partida de volta:

    Team B.aggregate_score = 2
    Team A.aggregate_score = 1

A convenção deverá sempre indicar o total acumulado após a partida atual.

O placar agregado não deverá substituir os placares individuais das partidas.

#### Placar anterior do confronto

O campo `previous_leg_score` poderá armazenar o total acumulado antes da partida
atual.

Exemplo:

    partida de ida:
        Team A 2 x 1 Team B

Na partida de volta:

    Team A.previous_leg_score = 2
    Team B.previous_leg_score = 1

Após a partida, `aggregate_score` poderá conter o total atualizado.

Esse campo poderá ser derivado, mas poderá permanecer armazenado para facilitar
consultas e auditoria.

#### Confrontos com múltiplas partidas

A relação entre partidas de um mesmo confronto deverá ser representada por uma
entidade própria.

Exemplo conceitual:

    Tie
    ├── id
    ├── competition_id
    ├── season_id
    ├── stage_id
    ├── participant_1_team_id
    ├── participant_2_team_id
    ├── leg_count
    ├── aggregate_participant_1_score
    ├── aggregate_participant_2_score
    ├── winner_team_id
    └── status

A entidade `MatchParticipant` poderá armazenar o estado contextual do placar
agregado em cada partida.

Ela não deverá substituir a entidade `Tie`.

#### Resultado do participante

O campo `result_status` deverá ser calculado ou confirmado após a interpretação
do resultado da partida.

Exemplo regular:

    mandante venceu
        HOME.result_status = WIN
        AWAY.result_status = LOSS

Exemplo empate:

    HOME.result_status = DRAW
    AWAY.result_status = DRAW

Exemplo walkover:

    HOME.result_status = WALKOVER_WIN
    AWAY.result_status = WALKOVER_LOSS

O resultado de um participante deverá ser compatível com o resultado do outro.

#### Vencedor

Somente um participante poderá possuir:

    is_winner = true

em partidas com vencedor definido.

Em partidas empatadas:

    todos os participantes deverão possuir is_winner = false

Quando `Match.winner_team_id` estiver preenchido, deverá existir exatamente um
`MatchParticipant` com:

    team_id = Match.winner_team_id
    is_winner = true

Em partidas decididas por pênaltis, o vencedor deverá refletir a disputa.

#### Resultado administrativo

O campo `awarded_score` poderá armazenar o placar atribuído por decisão
administrativa.

Exemplo:

    partida encerrada administrativamente em 3 x 0

Para o vencedor:

    awarded_score = 3
    result_status = AWARDED_WIN

Para o perdedor:

    awarded_score = 0
    result_status = AWARDED_LOSS

O placar observado em campo, quando existir, deverá ser preservado separadamente.

Futuramente, a decisão deverá ser representada por:

    MatchDecision

#### Walkover

Em uma vitória por walkover:

    vencedor:
        is_walkover_winner = true
        result_status = WALKOVER_WIN

    perdedor:
        is_walkover_loser = true
        result_status = WALKOVER_LOSS

Os dois campos não poderão ser verdadeiros no mesmo participante.

A causa do walkover deverá ser preservada em estrutura específica.

Exemplo conceitual:

    MatchDecision
    ├── match_id
    ├── decision_type
    ├── affected_team_id
    ├── awarded_team_id
    ├── reason
    ├── decided_at
    └── source_provider

#### Desclassificação

Quando:

    is_disqualified = true

o participante deverá possuir:

    participant_status = DISQUALIFIED

ou:

    elimination_status = DISQUALIFIED

A desclassificação poderá ocorrer:

- antes da partida;
- após a partida;
- durante a competição;
- por irregularidade documental;
- por punição disciplinar;
- por decisão administrativa.

O resultado observado em campo deverá ser preservado, mesmo quando posteriormente
invalidado.

#### Equipe retirada

Uma equipe retirada poderá possuir:

    participant_status = WITHDRAWN

O registro não deverá ser excluído.

Quando outra equipe assumir sua posição:

    participante original:
        participant_status = REPLACED

    novo participante:
        participant_status = CONFIRMED

A relação entre os registros poderá ser representada futuramente por:

    MatchParticipantReplacement
    ├── outgoing_participant_id
    ├── incoming_participant_id
    ├── replaced_at
    ├── reason
    └── source_provider

#### Classificação e eliminação

O resultado da partida não deverá definir automaticamente a classificação.

Exemplo:

    equipe vence por 1 x 0
    mas perde o confronto agregado por 3 x 2

Nesse caso:

    result_status = WIN
    qualification_status = NOT_QUALIFIED
    elimination_status = ELIMINATED
    advancement_status = DID_NOT_ADVANCE

Esses campos deverão permanecer separados.

#### Avanço por empate

Uma equipe poderá avançar mesmo empatando a partida.

Exemplos:

- vantagem no placar agregado;
- melhor campanha;
- empate suficiente no regulamento;
- classificação de grupo;
- critério de desempate;
- decisão administrativa.

Portanto, `is_winner` não deverá ser utilizado como sinônimo de avanço.

#### Bye

Uma equipe poderá avançar sem disputar uma partida.

Esse caso não deverá criar uma partida fictícia obrigatoriamente.

Quando a competição modelar oficialmente um slot de partida sem adversário,
poderá existir um participante com:

    advancement_status = ADVANCED_BY_BYE

e outro participante indefinido ou ausente.

A estratégia definitiva deverá depender do formato do provider e da competição.

#### Posição antes e depois da partida

Os campos:

    ranking_position_before
    ranking_position_after

poderão representar a posição do participante na classificação da competição.

Esses campos serão contextuais e opcionais.

Eles não deverão substituir uma tabela histórica de classificação.

Futuramente, deverá existir:

    StandingSnapshot
    ├── competition_id
    ├── season_id
    ├── stage_id
    ├── round_id
    ├── team_id
    ├── position
    ├── points
    ├── played
    ├── wins
    ├── draws
    ├── losses
    ├── goals_for
    ├── goals_against
    ├── goal_difference
    └── captured_at

Os campos em `MatchParticipant` poderão representar um resumo associado à
partida.

#### Cabeça de chave

O campo `seed_number` poderá indicar a posição do participante em sorteios ou
chaves eliminatórias.

Exemplo:

    seed_number = 1

Esse valor deverá ser contextual à fase ou competição.

Ele não deverá ser armazenado como atributo permanente da equipe.

#### Posição no grupo

O campo `group_position` poderá indicar a posição da equipe em um grupo
relacionado à partida.

Ele poderá ser utilizado em partidas decisivas ou na última rodada.

Entretanto, classificações completas deverão permanecer em estruturas próprias.

#### Relação com LineupEntry

`LineupEntry` deverá referenciar:

    match_id
    match_participant_id
    team_id
    player_id

A referência a `match_participant_id` permitirá validar que a equipe da escalação
participa da partida.

Regra esperada:

    lineup_entry.team_id =
        match_participant.team_id

e:

    lineup_entry.match_id =
        match_participant.match_id

Isso reduzirá associações incorretas de jogadores a equipes que não participam
da partida.

#### Relação com MatchStatistic

Estatísticas por equipe deverão referenciar `MatchParticipant` sempre que
possível.

Exemplo:

    MatchStatistic
    ├── match_id
    ├── match_participant_id
    ├── team_id
    ├── statistic_type
    ├── value
    └── period

Essa relação permitirá diferenciar facilmente os valores de cada participante.

#### Relação com MatchEvent

Eventos poderão referenciar o participante responsável ou afetado.

Exemplo:

    MatchEvent
    ├── match_id
    ├── match_participant_id
    ├── team_id
    ├── player_id
    ├── event_type
    └── minute

A referência deverá ser compatível com a equipe do evento.

#### Relação com mercados de apostas

Seleções de mercados poderão referenciar participantes.

Exemplo:

    BettingSelection
    ├── market_id
    ├── match_participant_id
    ├── selection_type
    └── outcome

Isso será útil para mercados como:

- vencedor da partida;
- dupla chance;
- empate anula aposta;
- equipe classificada;
- equipe a marcar;
- handicap;
- clean sheet;
- total de gols da equipe;
- total de cartões da equipe;
- total de escanteios da equipe.

A associação não deverá depender apenas de nomes textuais.

#### Participantes e odds

Providers poderão utilizar identificadores próprios para participantes dentro do
mercado.

Exemplo:

    home
    away
    participant_1
    participant_2
    team_a
    team_b

Esses valores deverão ser normalizados para `MatchParticipant`.

Uma odd não deverá ser associada a uma equipe apenas pela posição visual no
payload sem confirmar o papel do participante.

#### Regras de integridade

- `match_id` deverá referenciar uma partida existente;
- `team_id`, quando informado, deverá referenciar uma equipe existente;
- `participant_role` deverá possuir valor válido;
- `participant_order` deverá ser maior que zero;
- `participant_status` deverá possuir valor válido;
- `result_status`, quando informado, deverá possuir valor válido;
- placares, quando informados, deverão ser maiores ou iguais a zero;
- posições e seeds, quando informados, deverão ser maiores que zero;
- `team_id` poderá ser nulo somente quando `is_tbd = true` ou durante resolução;
- `is_tbd = false` deverá exigir `team_id` em participante confirmado;
- `is_home_designation` e `is_away_designation` não poderão ser verdadeiros ao
  mesmo tempo;
- `is_walkover_winner` e `is_walkover_loser` não poderão ser verdadeiros ao
  mesmo tempo;
- `participant_role = HOME` deverá ser compatível com
  `is_home_designation = true`;
- `participant_role = AWAY` deverá ser compatível com
  `is_away_designation = true`;
- `is_disqualified = true` deverá ser compatível com status de desclassificação;
- `is_winner = true` deverá ser compatível com o resultado da partida;
- o mesmo `team_id` não poderá aparecer duas vezes na mesma partida;
- a mesma `participant_order` não poderá aparecer duas vezes na mesma partida;
- uma partida não poderá possuir mais de um participante HOME;
- uma partida não poderá possuir mais de um participante AWAY;
- uma partida regular não deverá possuir mais de dois participantes;
- participantes históricos não deverão ser removidos fisicamente;
- substituições de participantes deverão preservar histórico;
- conflitos entre providers deverão permanecer auditáveis.

#### Compatibilidade entre placares

Os placares deverão permanecer consistentes com `Match`.

Para participante mandante:

    score = match.home_score
    halftime_score = match.home_halftime_score
    extra_time_score = match.home_extra_time_score
    penalty_score = match.home_penalty_score

Para participante visitante:

    score = match.away_score
    halftime_score = match.away_halftime_score
    extra_time_score = match.away_extra_time_score
    penalty_score = match.away_penalty_score

Uma divergência deverá:

- impedir atualização silenciosa;
- gerar conflito;
- preservar observações;
- considerar prioridade da fonte;
- exigir fusão controlada.

#### Compatibilidade entre resultados

Para uma partida finalizada sem empate:

    exatamente um participante deverá possuir is_winner = true

Para uma partida empatada:

    nenhum participante deverá possuir is_winner = true

Em uma partida cancelada:

    result_status deverá ser CANCELLED ou NO_RESULT

Em uma partida com walkover:

    um participante deverá possuir WALKOVER_WIN
    outro participante deverá possuir WALKOVER_LOSS

Em uma decisão administrativa:

    um participante poderá possuir AWARDED_WIN
    outro participante poderá possuir AWARDED_LOSS

#### Regra inicial de unicidade

Deverá existir uma restrição única sobre:

    match_id
    participant_order

Também deverá existir uma restrição única parcial sobre:

    match_id
    team_id

quando `team_id` não for nulo.

Exemplo conceitual:

    UNIQUE (
        match_id,
        participant_order
    )

e:

    UNIQUE (
        match_id,
        team_id
    )
    WHERE team_id IS NOT NULL

A restrição por papel deverá considerar os valores equivalentes de mandante e
visitante.

Exemplo:

    HOME
    NEUTRAL_HOME
    ADMINISTRATIVE_HOME
    TBD_HOME

Todos representam o slot principal de mandante.

A validação poderá ser realizada na aplicação ou por um campo normalizado de
slot.

#### Slot normalizado

Futuramente, poderá existir um campo:

    participant_slot

Valores:

    HOME_SLOT
    AWAY_SLOT

Esse campo permitiria aplicar uma restrição simples:

    UNIQUE (
        match_id,
        participant_slot
    )

A primeira versão poderá derivar o slot a partir de `participant_role`.

#### Resolução de identidade

A resolução de um participante deverá ocorrer somente após a resolução da
equipe.

Fluxo esperado:

    provider participant
        ↓
    external team identifier
        ↓
    Team resolution
        ↓
    Match resolution
        ↓
    MatchParticipant resolution

Quando o participante estiver indefinido:

    provider placeholder
        ↓
    placeholder normalization
        ↓
    source relationship
        ↓
    MatchParticipant com is_tbd = true

A aplicação não deverá criar equipes artificiais como:

    Winner Semi Final 1
    TBD
    Unknown Team
    To Be Defined

Esses valores deverão permanecer como placeholders.

#### Resolução de duplicidade

A resolução de duplicidade deverá considerar:

- partida;
- equipe;
- papel;
- ordem;
- slot;
- placeholder;
- origem;
- identificador externo;
- status;
- horário de observação.

Uma alteração de papel poderá indicar:

- correção do provider;
- inversão de mandante e visitante;
- alteração administrativa;
- erro de normalização;
- mudança real do confronto.

Ela não deverá ser aplicada silenciosamente.

#### Confrontos invertidos

Quando dois providers divergirem sobre mandante e visitante, os participantes
não deverão ser fundidos automaticamente apenas por equipe.

Exemplo:

    Provider A:
        Team A = HOME
        Team B = AWAY

    Provider B:
        Team A = AWAY
        Team B = HOME

O sistema deverá comparar:

- competição;
- regulamento;
- estádio;
- fonte oficial;
- mercados de apostas;
- escalações;
- placar;
- identificadores externos;
- histórico da partida.

A inversão poderá afetar todos os dados relacionados.

#### Participantes substituídos

Em competições eliminatórias, um participante poderá ser alterado após uma
decisão administrativa.

Exemplo:

    equipe A originalmente classificada
    equipe A desclassificada
    equipe B assume sua vaga

O registro original deverá permanecer no histórico.

A partida poderá ter:

    participante A com status REPLACED
    participante B com status CONFIRMED

A aplicação deverá garantir que apenas o participante atual seja utilizado em:

- escalações futuras;
- odds atuais;
- previsões atuais;
- estatísticas da partida ainda não realizada.

#### Proveniência

O campo `source_provider` poderá representar temporariamente a origem principal.

A arquitetura definitiva deverá utilizar:

    ExternalEntityMapping
    EntitySource
    ProviderObservation
    CanonicalFieldValue
    ConflictRecord

Campos críticos que deverão preservar observações incluem:

- equipe;
- papel;
- ordem;
- placar;
- resultado;
- classificação;
- eliminação;
- avanço;
- walkover;
- desclassificação;
- placeholder.

#### Confiança

O campo `confidence_score` deverá representar a confiança na identidade e no
contexto do participante.

Exemplo:

    1.0
        participante confirmado por fonte oficial

    0.8
        múltiplos providers confiáveis concordam

    0.5
        participante provável, mas papel divergente

    0.2
        placeholder pouco estruturado ou possível inversão

Esse valor não deverá representar probabilidade de vitória.

#### Índices recomendados para MatchParticipant

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_participant_match_id` | `match_id` | Buscar participantes de uma partida. |
| `ix_match_participant_team_id` | `team_id` | Buscar partidas de uma equipe. |
| `ix_match_participant_role` | `participant_role` | Filtrar pelo papel do participante. |
| `ix_match_participant_status` | `participant_status` | Filtrar pelo status da participação. |
| `ix_match_participant_result` | `result_status` | Consultar resultados por participante. |
| `ix_match_participant_order` | `match_id, participant_order` | Buscar participante pela ordem. |
| `ix_match_participant_match_team` | `match_id, team_id` | Localizar equipe dentro da partida. |
| `ix_match_participant_team_result` | `team_id, result_status` | Consultar histórico de resultados da equipe. |
| `ix_match_participant_winner` | `match_id, is_winner` | Localizar vencedor da partida. |
| `ix_match_participant_tbd` | `is_tbd, participant_status` | Localizar participantes ainda indefinidos. |
| `ix_match_participant_qualification` | `qualification_status` | Consultar classificação. |
| `ix_match_participant_elimination` | `elimination_status` | Consultar eliminações. |
| `ix_match_participant_advancement` | `advancement_status` | Consultar avanço de fase. |
| `ix_match_participant_walkover` | `is_walkover_winner, is_walkover_loser` | Consultar resultados por walkover. |

Índices simples em campos booleanos poderão possuir baixa seletividade.

Índices parciais poderão ser mais eficientes.

Exemplo para vencedores:

    INDEX ON match_participant (
        team_id,
        match_id
    )
    WHERE is_winner = true

Exemplo para participantes indefinidos:

    INDEX ON match_participant (
        match_id,
        participant_order
    )
    WHERE is_tbd = true

Exemplo para equipes classificadas:

    INDEX ON match_participant (
        team_id,
        match_id
    )
    WHERE qualification_status = 'QUALIFIED'

#### Restrições recomendadas

As restrições iniciais deverão incluir:

    UNIQUE (
        match_id,
        participant_order
    )

    UNIQUE (
        match_id,
        team_id
    )
    WHERE team_id IS NOT NULL

    CHECK participant_order > 0

    CHECK score >= 0
    CHECK halftime_score >= 0
    CHECK extra_time_score >= 0
    CHECK penalty_score >= 0
    CHECK aggregate_score >= 0
    CHECK previous_leg_score >= 0
    CHECK awarded_score >= 0

    CHECK ranking_position_before > 0
    CHECK ranking_position_after > 0
    CHECK seed_number > 0
    CHECK group_position > 0

As restrições numéricas deverão permitir valores nulos.

Regras envolvendo múltiplas linhas da mesma partida poderão exigir:

- serviço de domínio;
- validação transacional;
- trigger;
- constraint exclusion;
- índice parcial.

#### Dependências futuras

A entidade `MatchParticipant` será utilizada por:

- escalações;
- jogadores relacionados;
- estatísticas por equipe;
- eventos;
- gols;
- cartões;
- substituições;
- posse de bola;
- finalizações;
- escanteios;
- faltas;
- classificações;
- placares agregados;
- confrontos eliminatórios;
- avanço de fase;
- eliminação;
- walkovers;
- decisões administrativas;
- mercados de apostas;
- seleções de mercado;
- odds;
- previsões;
- análise de mando;
- análise de campo neutro;
- desempenho por participante;
- validação de providers.

Por isso, a entidade deverá preservar a identidade da equipe, seu papel, seu
resultado e seu contexto competitivo sem depender exclusivamente dos campos
resumidos de `Match`.
---

### 8.3 MatchVenue

A entidade `MatchVenue` representa o contexto físico e operacional do local
utilizado por uma partida.

Ela deverá complementar o campo resumido existente em `Match`:

    stadium_id

O campo `Match.stadium_id` continuará sendo utilizado como referência rápida ao
estádio principal atualmente reconhecido para a partida.

A entidade `MatchVenue` deverá preservar:

- o local planejado;
- o local confirmado;
- mudanças de estádio;
- locais temporários;
- locais alternativos;
- contexto de campo neutro;
- cidade relacionada;
- capacidade operacional;
- condições do gramado;
- condições ambientais;
- histórico de validade;
- proveniência das informações.

Exemplo conceitual:

    Match
    ├── stadium_id
    └── MatchVenue
        ├── local inicialmente planejado
        ├── local posteriormente confirmado
        └── local efetivamente utilizado

`MatchVenue` não deverá substituir a entidade `Stadium`.

A separação será:

    Stadium
        identidade canônica do estádio ou instalação esportiva

    Match.stadium_id
        referência rápida ao estádio principal atual

    MatchVenue
        contexto do local dentro de uma partida específica

#### Responsabilidades

A entidade `MatchVenue` será responsável por:

- relacionar uma partida a um estádio;
- relacionar uma partida a uma cidade;
- indicar o papel do local;
- indicar o status do local;
- preservar locais provisórios e confirmados;
- representar mudanças de estádio;
- indicar campo neutro;
- indicar estádio temporário;
- indicar local alternativo;
- indicar realização com portões fechados;
- armazenar capacidade conhecida;
- armazenar capacidade operacional;
- armazenar limite de público;
- armazenar público relacionado ao contexto;
- armazenar tipo de superfície;
- armazenar condição da superfície;
- armazenar condições climáticas resumidas;
- armazenar temperatura;
- armazenar umidade;
- armazenar velocidade do vento;
- armazenar altitude contextual;
- indicar ambiente coberto;
- indicar teto fechado;
- preservar períodos de validade;
- preservar origem e confiança;
- apoiar modelos estatísticos;
- apoiar análise de vantagem de mando;
- apoiar análise climática;
- apoiar mercados de apostas;
- apoiar auditoria de alterações.

#### Campos principais

    id
    match_id
    stadium_id
    city_id
    venue_role
    venue_status
    surface_type
    surface_condition
    weather_condition
    temperature_celsius
    humidity_percent
    wind_speed_kmh
    altitude_meters
    capacity
    operational_capacity
    attendance_limit
    attendance
    is_neutral
    is_indoor
    is_roof_closed
    is_closed_doors
    is_temporary
    is_alternative
    is_confirmed
    valid_from
    valid_until
    source_provider
    confidence_score
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno e canônico do contexto de local. |
| `match_id` | UUID | Sim | Partida relacionada ao local. |
| `stadium_id` | UUID | Não | Estádio canônico relacionado ao contexto. |
| `city_id` | UUID | Não | Cidade onde a partida está prevista ou foi realizada. |
| `venue_role` | enum | Sim | Papel do local dentro da partida. |
| `venue_status` | enum | Sim | Situação atual ou histórica do local. |
| `surface_type` | enum | Não | Tipo de superfície esportiva. |
| `surface_condition` | enum | Não | Condição conhecida da superfície. |
| `weather_condition` | enum | Não | Condição climática resumida. |
| `temperature_celsius` | decimal | Não | Temperatura observada em graus Celsius. |
| `humidity_percent` | decimal | Não | Umidade relativa do ar em percentual. |
| `wind_speed_kmh` | decimal | Não | Velocidade do vento em quilômetros por hora. |
| `altitude_meters` | integer | Não | Altitude contextual do local em metros. |
| `capacity` | integer | Não | Capacidade oficial ou estrutural conhecida do estádio. |
| `operational_capacity` | integer | Não | Capacidade liberada para a partida. |
| `attendance_limit` | integer | Não | Limite de público imposto para o evento. |
| `attendance` | integer | Não | Público oficialmente registrado no contexto. |
| `is_neutral` | boolean | Sim | Indica se a partida ocorre em campo neutro. |
| `is_indoor` | boolean | Sim | Indica se o ambiente é fechado ou interno. |
| `is_roof_closed` | boolean | Sim | Indica se o teto retrátil estava fechado. |
| `is_closed_doors` | boolean | Sim | Indica realização sem presença de público. |
| `is_temporary` | boolean | Sim | Indica uso temporário do local. |
| `is_alternative` | boolean | Sim | Indica local alternativo ao originalmente esperado. |
| `is_confirmed` | boolean | Sim | Indica se o local foi oficialmente confirmado. |
| `valid_from` | datetime UTC | Não | Início da validade da informação do local. |
| `valid_until` | datetime UTC | Não | Final da validade da informação do local. |
| `source_provider` | string | Não | Provider principal que originou a informação. |
| `confidence_score` | decimal | Não | Nível de confiança do contexto canônico. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Papéis de local previstos

    PRIMARY
    ALTERNATIVE
    TEMPORARY
    TRAINING
    EMERGENCY
    BACKUP
    ORIGINAL
    FINAL
    OTHER
    UNKNOWN

O valor `PRIMARY` deverá indicar o principal local associado à partida no estado
atual.

O valor `ALTERNATIVE` deverá indicar uma opção alternativa conhecida.

O valor `TEMPORARY` deverá representar um local utilizado provisoriamente.

O valor `TRAINING` poderá ser utilizado quando um provider representar uma
partida de treino ou evento não oficial em instalação de treinamento.

O valor `EMERGENCY` deverá representar uma alteração excepcional motivada por
problema operacional, climático, disciplinar ou de segurança.

O valor `BACKUP` deverá indicar um local de reserva ainda não utilizado.

O valor `ORIGINAL` deverá representar o local inicialmente programado.

O valor `FINAL` deverá indicar o local definitivamente reconhecido como utilizado
na partida.

O valor `OTHER` deverá representar um papel conhecido ainda não contemplado.

O valor `UNKNOWN` deverá representar ausência de informação.

#### Status do local previstos

    PLANNED
    PROVISIONAL
    PENDING_CONFIRMATION
    CONFIRMED
    CHANGED
    ACTIVE
    COMPLETED
    CANCELLED
    REJECTED
    UNAVAILABLE
    UNKNOWN

O status `PLANNED` deverá indicar um local previsto inicialmente.

O status `PROVISIONAL` deverá indicar um local provisório.

O status `PENDING_CONFIRMATION` deverá indicar que a informação ainda depende de
confirmação oficial.

O status `CONFIRMED` deverá indicar local oficialmente definido.

O status `CHANGED` deverá indicar que o local deixou de ser o local vigente após
uma alteração.

O status `ACTIVE` poderá ser utilizado durante a realização da partida.

O status `COMPLETED` deverá indicar o local efetivamente utilizado em uma partida
encerrada.

O status `CANCELLED` deverá indicar que o uso do local foi cancelado.

O status `REJECTED` deverá indicar que uma proposta de local não foi aceita.

O status `UNAVAILABLE` deverá indicar indisponibilidade operacional do local.

#### Tipos de gramado previstos

    NATURAL_GRASS
    HYBRID_GRASS
    ARTIFICIAL_TURF
    SYNTHETIC_TURF
    DIRT
    SAND
    INDOOR_SURFACE
    OTHER
    UNKNOWN

`NATURAL_GRASS` deverá representar gramado natural.

`HYBRID_GRASS` deverá representar uma combinação de grama natural e fibras
sintéticas.

`ARTIFICIAL_TURF` deverá representar gramado artificial utilizado em partidas
oficiais.

`SYNTHETIC_TURF` poderá ser utilizado quando o provider diferenciar esse conceito
de gramado artificial comum.

`DIRT` deverá representar campo de terra.

`SAND` deverá representar superfície de areia.

`INDOOR_SURFACE` deverá representar superfície específica de ambiente fechado,
quando o provider não fornecer classificação mais detalhada.

#### Condições do gramado previstas

    EXCELLENT
    GOOD
    REGULAR
    POOR
    DAMAGED
    DRY
    WET
    WATERLOGGED
    FROZEN
    SNOW_COVERED
    MUDDY
    UNEVEN
    OTHER
    UNKNOWN

A condição do gramado deverá representar uma observação contextual.

Ela não deverá ser armazenada permanentemente em `Stadium`, pois poderá variar
entre partidas.

Uma mesma instalação poderá possuir:

    surface_type = NATURAL_GRASS

e, em partidas distintas:

    surface_condition = GOOD

ou:

    surface_condition = WATERLOGGED

#### Condições climáticas previstas

    SUNNY
    PARTLY_CLOUDY
    CLOUDY
    OVERCAST
    LIGHT_RAIN
    RAIN
    HEAVY_RAIN
    STORM
    THUNDERSTORM
    SNOW
    HAIL
    FOG
    MIST
    WINDY
    HOT
    COLD
    OTHER
    UNKNOWN

A condição climática deverá representar um resumo observado no contexto da
partida.

Ela não deverá substituir medições estruturadas como:

    temperature_celsius
    humidity_percent
    wind_speed_kmh

Também não deverá substituir uma futura série temporal de observações
meteorológicas.

#### Relacionamentos principais

    Match   1 ─── N MatchVenue
    Stadium 0..1 ─── N MatchVenue
    City    0..1 ─── N MatchVenue

    MatchVenue 1 ─── N WeatherObservation
    MatchVenue 1 ─── N VenueConditionObservation
    MatchVenue 1 ─── N MatchScheduleChange

Uma partida poderá possuir múltiplos registros de `MatchVenue` quando houver:

- mudança de estádio;
- local inicialmente provisório;
- local alternativo;
- opção de reserva;
- alteração de cidade;
- correção de provider;
- histórico de confirmação.

Apenas um contexto deverá ser reconhecido como o local principal atual.

#### Compatibilidade com Match

O campo:

    Match.stadium_id

deverá representar o estádio principal atualmente reconhecido.

Quando existir um `MatchVenue` atual com:

    venue_role = PRIMARY
    venue_status = CONFIRMED
    is_confirmed = true

deverá existir compatibilidade:

    match.stadium_id = match_venue.stadium_id

Quando `stadium_id` estiver nulo em `MatchVenue`, essa compatibilidade não poderá
ser exigida.

Isso poderá ocorrer quando:

- apenas a cidade for conhecida;
- o estádio ainda não estiver definido;
- o local for descrito textualmente por um provider;
- a resolução canônica ainda estiver pendente;
- a partida ocorrer em instalação ainda não cadastrada.

#### Redundância controlada

`Match.stadium_id` e `MatchVenue.stadium_id` representam uma redundância
controlada.

Ela será aceita para:

- consultas rápidas;
- compatibilidade com APIs;
- filtros por estádio;
- redução de joins;
- integração com calendários;
- performance de leitura.

A atualização deverá ocorrer de maneira coordenada.

Fluxo esperado:

    confirmação do local
        ↓
    atualização de MatchVenue
        ↓
    atualização de Match.stadium_id
        ↓
    preservação do local anterior

Alterações isoladas não deverão produzir divergências permanentes.

#### Compatibilidade com Stadium

`MatchVenue` deverá referenciar a identidade canônica definida em `Stadium`.

Ela não deverá duplicar permanentemente dados estruturais como:

- nome oficial;
- cidade principal;
- país;
- coordenadas;
- capacidade estrutural padrão;
- data de inauguração;
- identidade histórica;
- aliases.

Entretanto, poderá armazenar valores contextuais da partida, como:

- capacidade operacional;
- limite de público;
- condição do gramado;
- teto fechado;
- portões fechados;
- condição climática;
- uso temporário;
- condição de campo neutro.

#### Cidade da partida

`city_id` deverá indicar a cidade associada ao local da partida.

Quando `stadium_id` estiver preenchido, a cidade normalmente deverá ser
compatível com a cidade do estádio.

Regra esperada:

    match_venue.city_id = stadium.city_id

Entretanto, divergências poderão ocorrer quando:

- o provider utilizar divisão administrativa diferente;
- o estádio estiver na região metropolitana;
- houver mudança de limites municipais;
- o cadastro do estádio estiver desatualizado;
- o provider utilizar a cidade comercialmente associada;
- o local ainda estiver em processo de resolução.

A divergência não deverá ser sobrescrita silenciosamente.

Ela deverá gerar revisão ou enriquecimento.

#### Cidade sem estádio definido

Uma partida poderá possuir cidade conhecida e estádio desconhecido.

Exemplo:

    city_id preenchido
    stadium_id = null
    venue_status = PLANNED

Isso poderá ocorrer quando a organização confirmar apenas a cidade-sede.

O sistema não deverá selecionar automaticamente um estádio apenas com base na
cidade.

#### Campo neutro

Quando a partida ocorrer em campo neutro:

    is_neutral = true

Essa condição não deverá alterar automaticamente:

    Match.home_team_id
    Match.away_team_id

As equipes continuarão possuindo papéis administrativos de mandante e visitante.

O campo neutro será relevante para:

- modelos de vantagem de mando;
- desempenho histórico;
- distância de viagem;
- apoio da torcida;
- mercados de apostas;
- finais;
- competições centralizadas;
- partidas internacionais;
- punições de mando;
- mudanças emergenciais de local.

#### Compatibilidade de campo neutro

Quando:

    Match.is_neutral_venue = true

deverá existir pelo menos um `MatchVenue` atual com:

    is_neutral = true

Quando:

    Match.is_neutral_venue = false

o `MatchVenue` principal não deverá normalmente possuir:

    is_neutral = true

Divergências deverão ser identificadas por validações de domínio.

#### Campo alternativo

Um local poderá ser considerado alternativo quando a equipe mandante não utilizar
seu estádio habitual.

Exemplos:

- estádio em reforma;
- punição disciplinar;
- indisponibilidade do campo;
- exigência de capacidade mínima;
- mudança por segurança;
- competição continental;
- problema de iluminação;
- problema no gramado.

Nesse caso:

    is_alternative = true

A partida poderá ou não ser considerada neutra.

Um estádio alternativo ainda poderá ser tratado como mando da equipe.

Portanto:

    is_alternative = true

não implica automaticamente:

    is_neutral = true

#### Estádio temporário

Um local temporário deverá utilizar:

    is_temporary = true

e poderá utilizar:

    venue_role = TEMPORARY

Esse contexto poderá representar:

- estádio provisório durante reforma;
- campo utilizado durante suspensão do estádio principal;
- instalação montada temporariamente;
- uso excepcional de outro município;
- local empregado apenas em uma fase da competição.

O uso temporário não deverá alterar a identidade permanente da equipe.

#### Local provisório

Um local ainda não confirmado poderá possuir:

    venue_status = PROVISIONAL
    is_confirmed = false

Quando houver confirmação:

    venue_status = CONFIRMED
    is_confirmed = true

O histórico da informação provisória deverá ser preservado.

A confirmação não deverá apagar a origem anterior.

#### Mudança de estádio

Uma mudança de estádio não deverá criar uma nova entidade `Match`.

O mesmo `Match.id` deverá ser preservado.

O local anterior deverá ser encerrado:

    venue_status = CHANGED
    valid_until preenchido
    is_confirmed = false

O novo local deverá ser criado ou ativado:

    venue_status = CONFIRMED
    valid_from preenchido
    is_confirmed = true

Exemplo:

    MatchVenue A:
        stadium = Estádio original
        venue_role = ORIGINAL
        venue_status = CHANGED
        valid_until preenchido

    MatchVenue B:
        stadium = Novo estádio
        venue_role = PRIMARY
        venue_status = CONFIRMED
        valid_from preenchido

#### Mudança de cidade

Uma mudança de estádio poderá também alterar a cidade.

Nesse caso, deverão ser atualizados de forma coordenada:

    stadium_id
    city_id

O histórico anterior deverá permanecer disponível.

A mudança poderá afetar:

- distância de viagem;
- altitude;
- clima;
- fuso horário;
- vantagem de mando;
- presença de torcida;
- capacidade;
- logística;
- probabilidades;
- odds.

#### Alteração de local e calendário

Mudanças de estádio poderão ocorrer juntamente com alterações de data e horário.

Futuramente, deverá existir uma entidade integrada de alteração.

Exemplo conceitual:

    MatchScheduleChange
    ├── id
    ├── match_id
    ├── previous_start_at
    ├── new_start_at
    ├── previous_stadium_id
    ├── new_stadium_id
    ├── previous_city_id
    ├── new_city_id
    ├── change_type
    ├── reason
    ├── announced_at
    ├── source_provider
    └── created_at

Tipos possíveis:

    DATE_CHANGE
    TIME_CHANGE
    VENUE_CHANGE
    CITY_CHANGE
    POSTPONEMENT
    EMERGENCY_RELOCATION
    OTHER

#### Capacidade

O campo `capacity` deverá representar a capacidade oficial ou estrutural
conhecida do local no contexto recebido.

Preferencialmente, a capacidade estrutural deverá permanecer em `Stadium`.

O campo contextual poderá ser utilizado quando:

- o provider informar uma capacidade específica;
- houver configuração temporária;
- parte do estádio estiver interditada;
- setores não estiverem disponíveis;
- houver redução por segurança;
- houver exigência da competição.

#### Capacidade operacional

`operational_capacity` deverá representar a capacidade efetivamente liberada
para a partida.

Exemplo:

    capacity = 50000
    operational_capacity = 42000

A diferença poderá ocorrer por:

- setores interditados;
- obras;
- separação de torcidas;
- zonas de segurança;
- equipamentos temporários;
- restrições administrativas;
- exigências da organização;
- bloqueios de visibilidade.

A capacidade operacional não deverá substituir a capacidade estrutural do
estádio.

#### Limite de público

`attendance_limit` deverá representar um limite específico imposto para a
partida.

Exemplo:

    operational_capacity = 42000
    attendance_limit = 30000

Isso poderá ocorrer por:

- punição;
- restrição sanitária;
- determinação de segurança;
- regulamento;
- decisão judicial;
- venda parcial de ingressos;
- fechamento de setores.

#### Público

`attendance` deverá representar o público oficialmente informado.

As diferenças deverão ser mantidas:

    capacity
        capacidade estrutural ou oficial

    operational_capacity
        capacidade liberada operacionalmente

    attendance_limit
        limite máximo imposto

    attendance
        público efetivamente registrado

Nenhum desses campos deverá substituir os demais.

#### Portões fechados

Quando uma partida ocorrer oficialmente sem público:

    is_closed_doors = true
    attendance = 0

O valor zero deverá ser diferente de valor desconhecido.

Portanto:

    attendance = 0
        partida oficialmente sem público

    attendance = null
        público desconhecido

`is_closed_doors = true` deverá ser confirmado por fonte confiável.

Uma partida com público zero por ausência de torcedores não deverá ser
classificada automaticamente como portões fechados.

#### Ambiente interno

Quando:

    is_indoor = true

o local deverá representar um ambiente fechado ou predominantemente interno.

Isso poderá afetar:

- clima;
- vento;
- iluminação;
- temperatura;
- comportamento da bola;
- análise estatística.

O valor não deverá ser inferido apenas pela existência de cobertura parcial.

#### Teto fechado

Quando o estádio possuir teto retrátil:

    is_roof_closed = true

deverá indicar que o teto estava fechado no contexto da partida.

Esse valor poderá mudar entre partidas realizadas no mesmo estádio.

Por isso, deverá permanecer em `MatchVenue` ou em uma observação contextual, e
não como valor permanente em `Stadium`.

#### Altitude

`altitude_meters` deverá representar a altitude contextual do local.

Preferencialmente, a altitude geográfica principal deverá permanecer em
`Stadium` ou `City`.

O campo contextual poderá ser utilizado quando:

- o provider informar diretamente;
- houver divergência de fonte;
- o local não estiver resolvido;
- a instalação temporária possuir altitude diferente;
- a modelagem inicial ainda não possuir coordenadas completas.

A altitude será relevante para:

- desempenho físico;
- fadiga;
- comportamento da bola;
- adaptação das equipes;
- análise de mando;
- modelos preditivos.

#### Temperatura

`temperature_celsius` deverá representar uma observação associada à partida ou
ao local.

O campo deverá aceitar valores negativos.

Ele não deverá ser utilizado como temperatura média da cidade ou do estádio.

Uma futura série temporal poderá armazenar:

- temperatura antes da partida;
- temperatura no início;
- temperatura no intervalo;
- temperatura no encerramento.

#### Umidade

`humidity_percent` deverá respeitar:

    0 <= humidity_percent <= 100

O valor deverá representar uma observação contextual.

Ele não deverá ser preenchido por média climática genérica sem indicação de que
se trata de estimativa.

#### Velocidade do vento

`wind_speed_kmh` deverá ser maior ou igual a zero.

O valor deverá representar velocidade observada ou informada.

Direção do vento poderá ser modelada futuramente.

Exemplo:

    wind_direction_degrees
    wind_gust_speed_kmh

#### Condições climáticas

A informação climática resumida poderá vir de:

- provider esportivo;
- estação meteorológica;
- serviço climático;
- observação oficial;
- dados do estádio;
- inferência contextual.

A origem deverá ser preservada.

Uma condição textual não deverá sobrescrever medições mais precisas sem
resolução.

#### Observações meteorológicas futuras

Futuramente, deverá existir:

    WeatherObservation
    ├── id
    ├── match_id
    ├── match_venue_id
    ├── observed_at
    ├── weather_condition
    ├── temperature_celsius
    ├── feels_like_celsius
    ├── humidity_percent
    ├── pressure_hpa
    ├── wind_speed_kmh
    ├── wind_direction_degrees
    ├── precipitation_mm
    ├── visibility_meters
    ├── source_provider
    └── confidence_score

`MatchVenue` deverá manter apenas um resumo contextual quando necessário.

#### Condição do gramado

A condição do gramado deverá permanecer contextual.

Uma mesma superfície poderá mudar por:

- chuva;
- drenagem;
- manutenção;
- excesso de uso;
- neve;
- gelo;
- calor;
- falha estrutural;
- substituição temporária.

A condição não deverá ser inferida apenas pelo clima.

Exemplo:

    weather_condition = RAIN
    surface_condition = GOOD

ou:

    weather_condition = CLOUDY
    surface_condition = WATERLOGGED

Ambos os casos poderão ser válidos.

#### Observações de condição futuras

Futuramente, poderá existir:

    VenueConditionObservation
    ├── id
    ├── match_venue_id
    ├── observed_at
    ├── surface_type
    ├── surface_condition
    ├── drainage_status
    ├── lighting_status
    ├── roof_status
    ├── temperature_celsius
    ├── notes
    ├── source_provider
    └── confidence_score

Isso permitirá acompanhar mudanças ao longo do evento.

#### Histórico de alterações

Os registros de `MatchVenue` deverão preservar períodos de validade.

Exemplo:

    local original:
        valid_from = data da primeira programação
        valid_until = data da alteração
        venue_status = CHANGED

    local novo:
        valid_from = data da confirmação
        valid_until = null
        venue_status = CONFIRMED

O histórico não deverá ser removido fisicamente.

#### Local atual

Um local poderá ser considerado atual quando:

    valid_until = null

e:

    venue_status IN (
        PLANNED,
        PROVISIONAL,
        PENDING_CONFIRMATION,
        CONFIRMED,
        ACTIVE
    )

Entretanto, apenas um local deverá ser considerado principal e confirmado no
mesmo momento.

#### Múltiplos locais candidatos

Uma partida poderá possuir vários locais candidatos antes da confirmação.

Exemplo:

    Estádio A = opção principal
    Estádio B = alternativa
    Estádio C = reserva

Nesse caso:

    apenas um poderá possuir venue_role = PRIMARY

Os demais poderão utilizar:

    ALTERNATIVE
    BACKUP
    TEMPORARY

Quando um local for confirmado, os demais deverão permanecer como histórico ou
alternativas inativas.

#### Regras de integridade

- `match_id` deverá referenciar uma partida existente;
- `stadium_id`, quando informado, deverá referenciar um estádio existente;
- `city_id`, quando informado, deverá referenciar uma cidade existente;
- `venue_role` deverá possuir valor válido;
- `venue_status` deverá possuir valor válido;
- `surface_type`, quando informado, deverá possuir valor válido;
- `surface_condition`, quando informada, deverá possuir valor válido;
- `weather_condition`, quando informada, deverá possuir valor válido;
- `capacity`, quando informada, deverá ser maior ou igual a zero;
- `operational_capacity`, quando informada, deverá ser maior ou igual a zero;
- `attendance_limit`, quando informado, deverá ser maior ou igual a zero;
- `attendance`, quando informado, deverá ser maior ou igual a zero;
- `humidity_percent`, quando informado, deverá estar entre zero e cem;
- `wind_speed_kmh`, quando informado, deverá ser maior ou igual a zero;
- `operational_capacity` não deverá normalmente superar `capacity`;
- `attendance_limit` não deverá normalmente superar `operational_capacity`;
- `attendance` não deverá normalmente superar `attendance_limit`;
- `attendance` não deverá normalmente superar `operational_capacity`;
- `valid_until`, quando informado, deverá ser posterior ou igual a `valid_from`;
- `is_closed_doors = true` deverá ser compatível com `attendance = 0` ou
  `attendance = null` enquanto o público ainda não estiver confirmado;
- `is_roof_closed = true` deverá ser compatível com local que possua estrutura
  coberta;
- `is_confirmed = true` deverá ser compatível com `venue_status = CONFIRMED`,
  `ACTIVE` ou `COMPLETED`;
- `venue_status = CANCELLED` não deverá possuir `is_confirmed = true`;
- `venue_status = CHANGED` deverá possuir período encerrado quando possível;
- apenas um local principal confirmado deverá estar vigente por partida;
- mudanças de local não deverão criar uma nova partida;
- locais históricos não deverão ser removidos fisicamente;
- divergências entre `Match.stadium_id` e `MatchVenue` deverão ser auditadas;
- conflitos entre providers deverão ser preservados.

#### Validações contextuais

Algumas regras não deverão ser implementadas inicialmente como constraints
rígidas.

Exemplo:

    operational_capacity <= capacity

Essa regra poderá possuir exceções quando:

- a capacidade oficial estiver desatualizada;
- houver arquibancada temporária;
- o provider informar valores divergentes;
- a capacidade depender da configuração do evento.

Nesses casos, a aplicação deverá:

- preservar os valores recebidos;
- marcar o conflito;
- comparar fontes;
- encaminhar para resolução;
- evitar descarte silencioso.

#### Regra do local principal

Dentro de uma mesma partida, deverá existir no máximo um registro vigente com:

    venue_role = PRIMARY
    is_confirmed = true

Uma possível restrição parcial futura será:

    UNIQUE (
        match_id
    )
    WHERE venue_role = 'PRIMARY'
      AND is_confirmed = true
      AND valid_until IS NULL

Essa restrição deverá ser avaliada com dados reais antes da implementação
definitiva.

#### Regra de unicidade contextual

Não deverá existir uma restrição simples apenas sobre:

    match_id
    stadium_id

O mesmo estádio poderá aparecer mais de uma vez no histórico da partida.

Exemplo:

    estádio inicialmente planejado
    estádio removido
    estádio posteriormente reconfirmado

Uma combinação candidata para identificação poderá considerar:

    match_id
    stadium_id
    venue_role
    valid_from

Valores nulos deverão ser tratados explicitamente.

#### Resolução de identidade do estádio

Antes de criar um `MatchVenue`, o estádio deverá passar por resolução de
identidade.

Fluxo esperado:

    provider venue
        ↓
    external stadium identifier
        ↓
    normalization
        ↓
    city matching
        ↓
    geographic matching
        ↓
    Stadium resolution
        ↓
    MatchVenue

A aplicação não deverá criar automaticamente um novo `Stadium` apenas por
diferença de grafia.

#### Critérios de resolução

A resolução de estádio deverá considerar:

- identificador externo;
- nome oficial;
- aliases;
- cidade;
- país;
- coordenadas;
- capacidade;
- equipe habitual;
- competição;
- endereço;
- histórico de nomes;
- provider;
- confiança.

Exemplos de nomes que poderão representar o mesmo estádio:

    Estádio Municipal Paulo Machado de Carvalho
    Pacaembu
    Estádio do Pacaembu

Esses nomes deverão ser resolvidos para uma única entidade canônica quando houver
evidência suficiente.

#### Local não resolvido

Quando o provider informar um local que ainda não puder ser resolvido:

    stadium_id = null

A observação original deverá permanecer na camada de proveniência.

O `MatchVenue` poderá ser criado provisoriamente quando houver contexto
suficiente, como:

    match_id
    city_id
    venue_status
    source_provider

A publicação como local confirmado deverá depender das regras de qualidade.

#### Resolução de duplicidade

A resolução de duplicidade deverá considerar:

- partida;
- estádio;
- cidade;
- papel;
- status;
- período de validade;
- condição de confirmação;
- identificador externo;
- provider;
- momento da observação.

Dois providers poderão informar:

    mesmo estádio
    mesmo status
    horários de observação diferentes

Essas observações poderão ser fundidas em um único registro canônico.

Entretanto, divergências reais de local deverão permanecer separadas até a
resolução.

#### Proveniência

O campo `source_provider` poderá representar temporariamente a origem principal.

A arquitetura definitiva deverá utilizar:

    ExternalEntityMapping
    EntitySource
    ProviderObservation
    CanonicalFieldValue
    ConflictRecord

Campos críticos que deverão preservar observações incluem:

- estádio;
- cidade;
- papel;
- status;
- campo neutro;
- capacidade;
- capacidade operacional;
- limite de público;
- público;
- superfície;
- condição do gramado;
- clima;
- temperatura;
- umidade;
- vento;
- altitude;
- portões fechados;
- teto fechado.

#### Confiança

O campo `confidence_score` deverá representar confiança na identidade e no
contexto do local.

Exemplo:

    1.0
        local confirmado por fonte oficial

    0.8
        múltiplos providers confiáveis concordam

    0.5
        cidade conhecida, mas estádio não confirmado

    0.2
        local textual pouco estruturado ou divergente

Esse valor não deverá representar probabilidade esportiva.

#### Índices recomendados para MatchVenue

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_venue_match_id` | `match_id` | Buscar locais relacionados à partida. |
| `ix_match_venue_stadium_id` | `stadium_id` | Buscar partidas relacionadas a um estádio. |
| `ix_match_venue_city_id` | `city_id` | Buscar partidas relacionadas a uma cidade. |
| `ix_match_venue_role` | `venue_role` | Filtrar pelo papel do local. |
| `ix_match_venue_status` | `venue_status` | Filtrar pelo status do local. |
| `ix_match_venue_surface_type` | `surface_type` | Filtrar pelo tipo de superfície. |
| `ix_match_venue_is_neutral` | `is_neutral` | Buscar partidas em campo neutro. |
| `ix_match_venue_is_confirmed` | `is_confirmed` | Buscar locais confirmados. |
| `ix_match_venue_valid_from` | `valid_from` | Consultar início de validade. |
| `ix_match_venue_valid_until` | `valid_until` | Consultar encerramento de validade. |
| `ix_match_venue_match_role` | `match_id, venue_role` | Buscar local por papel dentro da partida. |
| `ix_match_venue_stadium_validity` | `stadium_id, valid_from` | Consultar histórico de uso do estádio. |
| `ix_match_venue_city_validity` | `city_id, valid_from` | Consultar partidas por cidade e período. |
| `ix_match_venue_match_status` | `match_id, venue_status` | Buscar locais da partida por status. |
| `ix_match_venue_match_confirmed` | `match_id, is_confirmed` | Localizar o local confirmado da partida. |

Índices simples sobre campos booleanos poderão possuir baixa seletividade.

Índices parciais poderão ser mais eficientes.

Exemplo para locais principais confirmados:

    INDEX ON match_venue (
        match_id,
        stadium_id
    )
    WHERE venue_role = 'PRIMARY'
      AND is_confirmed = true
      AND valid_until IS NULL

Exemplo para partidas em campo neutro:

    INDEX ON match_venue (
        stadium_id,
        match_id
    )
    WHERE is_neutral = true

Exemplo para locais ainda pendentes:

    INDEX ON match_venue (
        match_id,
        venue_status
    )
    WHERE venue_status IN (
        'PLANNED',
        'PROVISIONAL',
        'PENDING_CONFIRMATION'
    )

#### Restrições recomendadas

As restrições numéricas iniciais deverão incluir:

    CHECK capacity >= 0

    CHECK operational_capacity >= 0

    CHECK attendance_limit >= 0

    CHECK attendance >= 0

    CHECK humidity_percent >= 0
    CHECK humidity_percent <= 100

    CHECK wind_speed_kmh >= 0

As restrições deverão aceitar valores nulos.

Também deverá existir:

    CHECK valid_until IS NULL
       OR valid_from IS NULL
       OR valid_until >= valid_from

Uma possível restrição contextual será:

    CHECK is_closed_doors = false
       OR attendance IS NULL
       OR attendance = 0

Essa regra deverá ser avaliada conforme os dados dos providers.

#### Dependências futuras

A entidade `MatchVenue` será utilizada por:

- histórico de locais;
- mudanças de estádio;
- calendário;
- campo neutro;
- análise de mando;
- modelos estatísticos;
- previsões;
- odds;
- mercados de apostas;
- clima;
- temperatura;
- vento;
- umidade;
- altitude;
- condição do gramado;
- capacidade;
- público;
- logística;
- distância de viagem;
- desempenho por estádio;
- desempenho por cidade;
- desempenho em gramado artificial;
- desempenho em altitude;
- desempenho em campo neutro;
- auditoria de providers;
- alertas de alteração de local.

Por isso, a entidade deverá preservar o contexto físico da partida, a validade
temporal das informações e as diferenças entre identidade do estádio, local
atual, capacidade, público e condições operacionais.
---

### 8.4 MatchOfficial

A entidade `MatchOfficial` representa a participação contextual de um oficial em
uma partida.

Ela deverá relacionar a partida a uma pessoa ou perfil profissional responsável
por uma função oficial.

A separação será:

    Person
        identidade humana canônica

    Referee
        perfil profissional de arbitragem

    MatchOfficial
        nomeação e atuação contextual na partida

A entidade `MatchOfficial` não deverá duplicar a identidade permanente do
árbitro.

Ela deverá registrar:

- qual oficial foi nomeado;
- qual função exerceu;
- se a nomeação foi confirmada;
- se houve substituição;
- se o oficial efetivamente atuou;
- o período de validade da nomeação;
- a origem da informação;
- o nível de confiança;
- observações e alterações.

Exemplo conceitual:

    Match
    ├── MatchOfficial
    │   ├── árbitro principal
    │   ├── primeiro assistente
    │   ├── segundo assistente
    │   ├── quarto árbitro
    │   ├── VAR
    │   └── AVAR
    ├── MatchParticipant
    ├── MatchVenue
    ├── LineupEntry
    ├── MatchEvent
    └── MatchStatistic

#### Responsabilidades

A entidade `MatchOfficial` será responsável por:

- relacionar um oficial à partida;
- relacionar uma pessoa à nomeação;
- relacionar um perfil de árbitro à nomeação;
- indicar a função oficial exercida;
- indicar a ordem funcional;
- indicar o status da nomeação;
- indicar se a nomeação foi confirmada;
- indicar se o oficial efetivamente atuou;
- indicar se houve substituição;
- relacionar o oficial substituído;
- relacionar o oficial substituto;
- registrar o momento da substituição;
- registrar o minuto da substituição;
- registrar o período da partida;
- representar oficiais ainda não identificados;
- preservar nomeações provisórias;
- preservar nomeações canceladas;
- preservar histórico de alterações;
- registrar autoridade responsável pela nomeação;
- preservar proveniência;
- armazenar nível de confiança;
- apoiar estatísticas de arbitragem;
- apoiar análise disciplinar;
- apoiar modelos de previsão;
- apoiar auditoria de providers.

#### Campos principais

    id
    match_id
    person_id
    referee_id
    official_role
    official_order
    appointment_status
    participation_status
    appointed_by
    appointment_reference
    appointed_at
    confirmed_at
    started_at
    ended_at
    replaced_official_id
    replacement_official_id
    replacement_minute
    replacement_added_time
    replacement_period
    is_primary
    is_confirmed
    did_participate
    is_replacement
    is_replaced
    is_tbd
    placeholder_name
    notes
    valid_from
    valid_until
    source_provider
    confidence_score
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno e canônico da nomeação. |
| `match_id` | UUID | Sim | Partida relacionada ao oficial. |
| `person_id` | UUID | Não | Pessoa canônica relacionada à nomeação. |
| `referee_id` | UUID | Não | Perfil profissional de árbitro relacionado. |
| `official_role` | enum | Sim | Função exercida ou prevista na partida. |
| `official_order` | integer | Sim | Ordem funcional do oficial dentro da mesma função ou equipe. |
| `appointment_status` | enum | Sim | Situação da nomeação. |
| `participation_status` | enum | Não | Situação efetiva da atuação do oficial. |
| `appointed_by` | string | Não | Federação, competição ou autoridade responsável pela nomeação. |
| `appointment_reference` | string | Não | Código, documento ou referência oficial da nomeação. |
| `appointed_at` | datetime UTC | Não | Momento em que a nomeação foi publicada ou registrada. |
| `confirmed_at` | datetime UTC | Não | Momento em que a nomeação foi confirmada. |
| `started_at` | datetime UTC | Não | Momento em que a atuação efetiva começou. |
| `ended_at` | datetime UTC | Não | Momento em que a atuação efetiva terminou. |
| `replaced_official_id` | UUID | Não | Nomeação substituída por este oficial. |
| `replacement_official_id` | UUID | Não | Nomeação que substituiu este oficial. |
| `replacement_minute` | integer | Não | Minuto da partida em que ocorreu a substituição. |
| `replacement_added_time` | integer | Não | Acréscimo relacionado ao momento da substituição. |
| `replacement_period` | enum | Não | Período da partida em que ocorreu a substituição. |
| `is_primary` | boolean | Sim | Indica se o oficial é a referência principal de sua função. |
| `is_confirmed` | boolean | Sim | Indica se a nomeação foi oficialmente confirmada. |
| `did_participate` | boolean | Sim | Indica se o oficial efetivamente atuou. |
| `is_replacement` | boolean | Sim | Indica se entrou como substituto. |
| `is_replaced` | boolean | Sim | Indica se foi substituído. |
| `is_tbd` | boolean | Sim | Indica que o oficial ainda não foi identificado. |
| `placeholder_name` | string | Não | Nome ou descrição provisória do oficial ainda não resolvido. |
| `notes` | text | Não | Observações contextuais sobre a nomeação. |
| `valid_from` | datetime UTC | Não | Início da validade da nomeação. |
| `valid_until` | datetime UTC | Não | Encerramento da validade da nomeação. |
| `source_provider` | string | Não | Provider principal que originou o registro. |
| `confidence_score` | decimal | Não | Nível de confiança da nomeação canônica. |
| `created_at` | datetime UTC | Sim | Data de criação do registro. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Funções oficiais previstas

    MAIN_REFEREE
    ASSISTANT_REFEREE_1
    ASSISTANT_REFEREE_2
    ADDITIONAL_ASSISTANT_REFEREE_1
    ADDITIONAL_ASSISTANT_REFEREE_2
    FOURTH_OFFICIAL
    RESERVE_ASSISTANT_REFEREE
    RESERVE_REFEREE
    VAR
    AVAR_1
    AVAR_2
    AVAR_3
    VIDEO_OPERATOR
    REFEREE_OBSERVER
    REFEREE_INSPECTOR
    MATCH_DELEGATE
    MATCH_COMMISSIONER
    TIMEKEEPER
    TECHNICAL_OFFICIAL
    OTHER
    UNKNOWN

`MAIN_REFEREE` deverá representar o árbitro principal da partida.

`ASSISTANT_REFEREE_1` e `ASSISTANT_REFEREE_2` deverão representar os dois
assistentes principais.

`ADDITIONAL_ASSISTANT_REFEREE_1` e
`ADDITIONAL_ASSISTANT_REFEREE_2` poderão representar árbitros adicionais,
quando a competição utilizar esse formato.

`FOURTH_OFFICIAL` deverá representar o quarto árbitro.

`RESERVE_ASSISTANT_REFEREE` deverá representar o assistente reserva.

`RESERVE_REFEREE` deverá representar um árbitro reserva fora das funções
tradicionais.

`VAR` deverá representar o árbitro de vídeo principal.

`AVAR_1`, `AVAR_2` e `AVAR_3` deverão representar assistentes do árbitro de
vídeo.

`VIDEO_OPERATOR` poderá representar o operador técnico do sistema de vídeo,
quando essa informação for disponibilizada.

`REFEREE_OBSERVER` deverá representar o observador de arbitragem.

`REFEREE_INSPECTOR` deverá representar o inspetor responsável por avaliar ou
acompanhar a equipe de arbitragem.

`MATCH_DELEGATE` deverá representar o delegado oficial da partida.

`MATCH_COMMISSIONER` deverá representar o comissário da competição.

`TIMEKEEPER` poderá ser utilizado em formatos especiais que possuam função
oficial de controle de tempo.

`TECHNICAL_OFFICIAL` poderá representar outros oficiais técnicos reconhecidos.

`OTHER` deverá representar uma função conhecida ainda não prevista.

`UNKNOWN` deverá representar ausência real de informação.

#### Status de nomeação previstos

    PROPOSED
    APPOINTED
    PENDING_CONFIRMATION
    CONFIRMED
    CHANGED
    REPLACED
    WITHDRAWN
    CANCELLED
    COMPLETED
    REJECTED
    UNKNOWN

`PROPOSED` deverá indicar nomeação ainda preliminar.

`APPOINTED` deverá indicar que o oficial foi formalmente indicado.

`PENDING_CONFIRMATION` deverá indicar que a nomeação ainda depende de confirmação.

`CONFIRMED` deverá indicar nomeação oficial confirmada.

`CHANGED` deverá indicar que a nomeação deixou de ser atual devido a uma
alteração.

`REPLACED` deverá indicar que outro oficial assumiu a função.

`WITHDRAWN` deverá indicar retirada da nomeação.

`CANCELLED` deverá indicar cancelamento da nomeação ou da própria partida.

`COMPLETED` deverá indicar atuação encerrada normalmente.

`REJECTED` deverá indicar uma nomeação proposta que não foi aceita.

#### Status de participação previstos

    EXPECTED
    AVAILABLE
    ACTIVE
    TEMPORARILY_INACTIVE
    REPLACED
    DID_NOT_PARTICIPATE
    COMPLETED
    UNKNOWN

`EXPECTED` deverá indicar que o oficial está previsto para atuar.

`AVAILABLE` deverá indicar que está presente e disponível.

`ACTIVE` deverá indicar atuação efetiva.

`TEMPORARILY_INACTIVE` poderá representar uma interrupção temporária da atuação.

`REPLACED` deverá indicar que a atuação foi encerrada por substituição.

`DID_NOT_PARTICIPATE` deverá indicar que o oficial foi nomeado, mas não atuou.

`COMPLETED` deverá indicar que a atuação foi concluída normalmente.

#### Períodos de substituição previstos

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

O período deverá indicar o momento contextual da substituição.

Quando a substituição ocorrer antes do início:

    replacement_period = PRE_MATCH
    replacement_minute = null

Quando ocorrer durante a partida:

    replacement_period deverá ser preenchido
    replacement_minute deverá ser preenchido quando conhecido

#### Relacionamentos principais

    Match   1 ─── N MatchOfficial
    Person  0..1 ─── N MatchOfficial
    Referee 0..1 ─── N MatchOfficial

    MatchOfficial 0..1 ─── 0..1 MatchOfficial substituído
    MatchOfficial 0..1 ─── 0..1 MatchOfficial substituto

    MatchOfficial 1 ─── N MatchEvent
    MatchOfficial 1 ─── N RefereeDecision
    MatchOfficial 1 ─── N DisciplinaryEvent
    MatchOfficial 1 ─── N VARReview

Uma partida poderá possuir múltiplos oficiais.

A quantidade dependerá de:

- competição;
- categoria;
- fase;
- disponibilidade tecnológica;
- regulamento;
- nível profissional;
- provider;
- período histórico.

#### Compatibilidade com Referee

Quando `referee_id` estiver preenchido:

    match_official.person_id =
        referee.person_id

A referência a `person_id` poderá permanecer armazenada para:

- consultas rápidas;
- integridade;
- compatibilidade com providers;
- identificação de funções não estritamente arbitrais;
- suporte a oficiais que ainda não possuam perfil `Referee`.

Entretanto, quando ambos existirem, deverão apontar para a mesma pessoa.

#### Oficial sem perfil Referee

Nem toda função oficial exigirá obrigatoriamente um perfil `Referee`.

Exemplos:

    MATCH_DELEGATE
    MATCH_COMMISSIONER
    VIDEO_OPERATOR
    TECHNICAL_OFFICIAL

Nesses casos, poderá existir:

    person_id preenchido
    referee_id = null

Para funções estritamente arbitrais, como:

    MAIN_REFEREE
    ASSISTANT_REFEREE_1
    ASSISTANT_REFEREE_2
    FOURTH_OFFICIAL
    VAR
    AVAR_1

a existência de `referee_id` deverá ser preferida.

A ausência temporária poderá ser aceita durante a resolução de identidade.

#### Compatibilidade com Person

Quando `person_id` estiver preenchido, deverá referenciar uma pessoa canônica.

A nomeação não deverá armazenar a identidade humana apenas como texto.

O campo `placeholder_name` deverá ser utilizado somente quando:

- a pessoa ainda não foi identificada;
- o provider não informou identificador;
- o nome está incompleto;
- a resolução ainda está pendente;
- a função está definida, mas o oficial não.

#### Oficial ainda não definido

Uma partida futura poderá possuir funções oficiais ainda não preenchidas.

Exemplo:

    official_role = MAIN_REFEREE
    person_id = null
    referee_id = null
    is_tbd = true
    appointment_status = PENDING_CONFIRMATION

O sistema não deverá criar uma pessoa artificial com nomes como:

    Árbitro a definir
    TBD Referee
    Unknown Official

Esses valores deverão permanecer como placeholders.

#### Placeholder de oficial

Quando necessário:

    placeholder_name = "Árbitro a definir"

O texto deverá ser preservado como observação do provider.

Quando a identidade for resolvida:

    person_id deverá ser preenchido
    referee_id poderá ser preenchido
    is_tbd deverá ser alterado para false
    appointment_status deverá ser atualizado

O placeholder poderá permanecer no histórico de proveniência.

#### Ordem funcional

`official_order` deverá ser estável dentro da partida e da função.

Exemplos:

    MAIN_REFEREE = 1

    ASSISTANT_REFEREE_1 = 1
    ASSISTANT_REFEREE_2 = 2

    AVAR_1 = 1
    AVAR_2 = 2
    AVAR_3 = 3

A ordem não deverá depender da posição do item no payload.

Ela deverá ser determinada após normalização.

#### Funções exclusivas

Dentro de uma mesma partida deverá existir no máximo um oficial vigente em
funções exclusivas como:

    MAIN_REFEREE
    FOURTH_OFFICIAL
    VAR
    MATCH_DELEGATE
    MATCH_COMMISSIONER

Algumas competições poderão possuir exceções.

Por isso, as regras deverão ser configuráveis conforme o regulamento.

#### Funções múltiplas

Funções como assistentes poderão possuir múltiplos registros.

Exemplo:

    ASSISTANT_REFEREE_1
    ASSISTANT_REFEREE_2

A modelagem poderá utilizar:

- funções enumeradas separadas;
- uma função genérica com `official_order`;
- combinação das duas estratégias.

A estratégia inicial adotada será preservar funções explícitas quando o provider
as disponibilizar.

#### Oficial principal

O campo `is_primary` deverá indicar o oficial de referência dentro de uma
categoria funcional.

Exemplo:

    VAR principal:
        official_role = VAR
        is_primary = true

    AVAR:
        official_role = AVAR_1
        is_primary = false

Para árbitro principal:

    official_role = MAIN_REFEREE
    is_primary = true

A aplicação deverá evitar múltiplos oficiais principais vigentes na mesma função.

#### Nomeação confirmada

Quando:

    is_confirmed = true

o status deverá ser compatível com:

    CONFIRMED
    ACTIVE
    COMPLETED

Uma nomeação apenas proposta ou pendente não deverá possuir
`is_confirmed = true`.

#### Participação efetiva

`did_participate` deverá indicar se o oficial efetivamente atuou.

Uma pessoa poderá ter sido nomeada e não participar.

Exemplo:

    appointment_status = REPLACED
    did_participate = false

Outro exemplo:

    oficial inicia a partida e é substituído
    did_participate = true
    is_replaced = true

A nomeação e a participação deverão permanecer como conceitos separados.

#### Substituição antes da partida

Uma substituição poderá ocorrer antes do início.

Exemplo:

    árbitro principal originalmente nomeado
    apresenta indisponibilidade
    quarto árbitro assume a função

O registro original deverá permanecer:

    appointment_status = REPLACED
    did_participate = false
    is_replaced = true
    valid_until preenchido

O novo registro deverá indicar:

    appointment_status = CONFIRMED
    is_replacement = true
    did_participate conforme a realização

#### Substituição durante a partida

Uma substituição poderá ocorrer durante a partida por:

- lesão;
- indisposição;
- falha técnica;
- decisão da organização;
- problema operacional;
- incapacidade de continuidade.

O registro substituído deverá preservar:

    started_at
    ended_at
    replacement_minute
    replacement_added_time
    replacement_period
    is_replaced = true

O substituto deverá preservar:

    is_replacement = true
    started_at
    replaced_official_id

#### Relação entre substituído e substituto

A relação deverá permitir navegação nos dois sentidos.

No oficial original:

    replacement_official_id =
        oficial que assumiu

No substituto:

    replaced_official_id =
        oficial substituído

Os dois campos deverão permanecer consistentes.

Uma nomeação não poderá substituir a si mesma.

#### Cadeia de substituições

Em situações excepcionais poderão existir múltiplas substituições.

Exemplo:

    Oficial A
        substituído por Oficial B

    Oficial B
        substituído por Oficial C

A estrutura deverá permitir uma cadeia histórica.

Ela não deverá sobrescrever a substituição anterior.

#### Mudança de função

Um oficial poderá permanecer na partida, mas mudar de função.

Exemplo:

    quarto árbitro assume como árbitro principal

Nesse caso, a estratégia recomendada será:

    encerrar o MatchOfficial da função anterior

    criar novo MatchOfficial para a nova função

Isso preservará:

- função original;
- função assumida;
- período de cada atuação;
- ordem temporal;
- histórico.

O mesmo registro não deverá ter seu `official_role` alterado sem histórico.

#### Nomeação provisória

Uma nomeação provisória poderá possuir:

    appointment_status = PROPOSED

ou:

    appointment_status = PENDING_CONFIRMATION

e:

    is_confirmed = false

Quando confirmada, poderá ser atualizada mantendo o mesmo registro se a pessoa e
a função permanecerem iguais.

Caso outro oficial seja nomeado, o registro anterior deverá ser encerrado.

#### Nomeação cancelada

Uma nomeação cancelada deverá possuir:

    appointment_status = CANCELLED
    is_confirmed = false

O registro não deverá ser excluído.

A causa poderá estar relacionada a:

- cancelamento da partida;
- mudança de escala;
- indisponibilidade;
- punição;
- erro de provider;
- alteração administrativa.

#### Partida cancelada

Quando a partida for cancelada, as nomeações poderão permanecer registradas.

Isso será importante para:

- auditoria;
- histórico profissional;
- análise operacional;
- verificação de alterações;
- dados de providers.

A participação deverá normalmente ser:

    did_participate = false

O status poderá ser:

    appointment_status = CANCELLED

#### Partida adiada

Em uma partida adiada, a equipe de arbitragem poderá:

- permanecer nomeada;
- ser removida;
- ser substituída;
- ser novamente confirmada;
- ficar pendente.

O adiamento não deverá apagar as nomeações anteriores.

A validade deverá ser controlada por:

    valid_from
    valid_until
    appointment_status

#### Partida suspensa ou retomada

Uma partida suspensa poderá manter os mesmos oficiais na retomada.

Também poderá existir substituição.

A aplicação deverá preservar:

- oficial que iniciou;
- oficial que retomou;
- minuto da suspensão;
- minuto da substituição;
- períodos de atuação;
- fonte da decisão.

#### Árbitro principal

Deverá existir no máximo um `MAIN_REFEREE` vigente e confirmado por partida.

Uma possível regra será:

    official_role = MAIN_REFEREE
    is_confirmed = true
    valid_until = null

A ausência de árbitro principal poderá ser permitida em partidas futuras ou
dados históricos incompletos.

#### Árbitros assistentes

Uma partida profissional normalmente possuirá dois assistentes.

Entretanto, a quantidade poderá variar em:

- categorias de base;
- partidas históricas;
- amistosos;
- torneios amadores;
- formatos reduzidos;
- dados incompletos.

A aplicação não deverá impor universalmente a existência de dois assistentes.

A validação deverá considerar o contexto da competição.

#### VAR e AVAR

A presença de VAR deverá depender da competição, temporada, fase e partida.

Uma partida poderá possuir:

    VAR
    AVAR_1
    AVAR_2
    AVAR_3

A ausência de VAR não deverá ser tratada automaticamente como dado incompleto.

O sistema deverá distinguir:

    competição sem VAR

de:

    provider não informou VAR

Essa distinção dependerá de regras da competição e proveniência.

#### Localização da equipe de vídeo

Árbitros de vídeo poderão atuar fora do estádio.

Futuramente, poderá existir:

    OfficialOperationLocation
    ├── match_official_id
    ├── location_type
    ├── stadium_id
    ├── city_id
    ├── facility_name
    └── source_provider

Tipos possíveis:

    STADIUM
    REMOTE_VIDEO_CENTER
    FEDERATION_CENTER
    OTHER
    UNKNOWN

Essa estrutura não deverá ser incluída diretamente em `MatchVenue`.

#### Relação com MatchEvent

Eventos poderão referenciar o oficial responsável por uma decisão.

Exemplo:

    MatchEvent
    ├── match_id
    ├── match_official_id
    ├── event_type
    ├── minute
    └── decision_status

Isso poderá ser utilizado em:

- cartões;
- marcação de pênalti;
- revisão de VAR;
- expulsões;
- paralisações;
- decisões administrativas;
- reinício da partida.

A ausência da referência ao oficial não deverá impedir o armazenamento do evento.

#### Relação com cartões

Cartões e advertências deverão ser associados principalmente a jogadores ou
membros das equipes.

O oficial poderá ser relacionado como responsável pela decisão.

Exemplo:

    DisciplinaryEvent
    ├── match_id
    ├── match_official_id
    ├── affected_person_id
    ├── affected_team_id
    ├── card_type
    ├── minute
    └── reason

Essa relação será importante para análise do perfil disciplinar do árbitro.

#### Relação com VARReview

Revisões de vídeo deverão poder referenciar:

    árbitro principal
    VAR
    AVAR
    evento revisado
    decisão inicial
    decisão final

Exemplo conceitual:

    VARReview
    ├── id
    ├── match_id
    ├── event_id
    ├── main_referee_official_id
    ├── var_official_id
    ├── review_type
    ├── original_decision
    ├── final_decision
    ├── started_at
    ├── ended_at
    └── source_provider

#### Relação com estatísticas de arbitragem

A entidade permitirá calcular estatísticas como:

- cartões por partida;
- faltas marcadas;
- pênaltis assinalados;
- expulsões;
- revisões de VAR;
- decisões alteradas;
- acréscimos médios;
- desempenho por competição;
- desempenho por equipe;
- distribuição mandante e visitante;
- frequência de resultados;
- taxa de cartões;
- taxa de pênaltis.

Essas análises deverão considerar o papel do oficial.

Estatísticas do árbitro principal não deverão ser misturadas com estatísticas do
VAR ou assistentes.

#### Uso analítico responsável

Dados de arbitragem poderão ser utilizados em modelos estatísticos.

Entretanto, deverão ser evitadas inferências não sustentadas, como:

- afirmar favorecimento deliberado;
- atribuir intenção;
- classificar corrupção;
- inferir comportamento ilegal;
- concluir parcialidade sem evidência.

A análise deverá permanecer baseada em métricas observáveis.

#### Regras de integridade

- `match_id` deverá referenciar uma partida existente;
- `person_id`, quando informado, deverá referenciar uma pessoa existente;
- `referee_id`, quando informado, deverá referenciar um perfil existente;
- `official_role` deverá possuir valor válido;
- `official_order` deverá ser maior que zero;
- `appointment_status` deverá possuir valor válido;
- `participation_status`, quando informado, deverá possuir valor válido;
- `replacement_minute`, quando informado, deverá ser maior ou igual a zero;
- `replacement_added_time`, quando informado, deverá ser maior ou igual a zero;
- `valid_until`, quando informado, deverá ser posterior ou igual a `valid_from`;
- `ended_at`, quando informado, deverá ser posterior ou igual a `started_at`;
- `confirmed_at`, quando informado, não deverá normalmente ser anterior a
  `appointed_at`;
- `referee_id` e `person_id`, quando informados, deverão representar a mesma
  pessoa;
- `is_tbd = false` deverá normalmente exigir `person_id` ou `referee_id`;
- `is_tbd = true` deverá permitir `placeholder_name`;
- `is_confirmed = true` deverá ser compatível com o status da nomeação;
- `is_replacement = true` deverá possuir referência ao oficial substituído
  quando conhecida;
- `is_replaced = true` deverá possuir referência ao substituto quando conhecida;
- uma nomeação não poderá substituir a si mesma;
- funções exclusivas não deverão possuir múltiplos oficiais vigentes;
- o mesmo oficial não deverá ocupar duas funções incompatíveis simultaneamente;
- nomeações históricas não deverão ser removidas fisicamente;
- mudanças de função deverão preservar registros anteriores;
- conflitos entre providers deverão ser auditáveis.

#### Compatibilidade entre Person e Referee

Quando ambos estiverem preenchidos:

    match_official.person_id =
        referee.person_id

Essa validação poderá ser realizada na aplicação.

A chave estrangeira isolada não será suficiente para garantir essa
compatibilidade.

#### Funções incompatíveis

Algumas funções não deverão ser exercidas simultaneamente pela mesma pessoa.

Exemplo:

    MAIN_REFEREE
    VAR

na mesma partida.

Entretanto, uma pessoa poderá mudar de função durante o evento em situação
excepcional.

Nesse caso, os períodos de validade não deverão se sobrepor.

A validação deverá considerar:

    official_role
    started_at
    ended_at
    valid_from
    valid_until

#### Regra de unicidade inicial

Uma combinação candidata será:

    match_id
    official_role
    official_order
    valid_from

Não deverá existir inicialmente uma restrição única simples apenas sobre:

    match_id
    referee_id

A mesma pessoa poderá possuir mais de uma função ao longo da mesma partida.

Exemplo:

    FOURTH_OFFICIAL
        antes da substituição

    MAIN_REFEREE
        após a substituição

Esses registros deverão ser distintos.

#### Oficial vigente por função

Uma possível restrição parcial futura será:

    UNIQUE (
        match_id,
        official_role,
        official_order
    )
    WHERE valid_until IS NULL
      AND appointment_status IN (
          'APPOINTED',
          'PENDING_CONFIRMATION',
          'CONFIRMED'
      )

Essa restrição deverá ser avaliada com dados reais.

#### Árbitro principal vigente

Uma possível restrição parcial será:

    UNIQUE (
        match_id
    )
    WHERE official_role = 'MAIN_REFEREE'
      AND is_confirmed = true
      AND valid_until IS NULL

Essa regra deverá permitir ausência temporária em registros incompletos.

#### Resolução de identidade

A resolução deverá ocorrer antes da criação definitiva da nomeação.

Fluxo esperado:

    provider official
        ↓
    external person identifier
        ↓
    name normalization
        ↓
    Person resolution
        ↓
    Referee resolution
        ↓
    Match resolution
        ↓
    MatchOfficial resolution

A aplicação não deverá criar um novo `Person` apenas por diferença de grafia.

#### Critérios de resolução

A resolução deverá considerar:

- identificador externo;
- nome completo;
- nome normalizado;
- aliases;
- data de nascimento;
- nacionalidade;
- federação;
- categoria;
- função;
- histórico de partidas;
- competição;
- período de atividade;
- provider;
- confiança.

Nomes idênticos não deverão ser considerados prova suficiente de identidade.

#### Oficial não resolvido

Quando a identidade ainda não puder ser resolvida:

    person_id = null
    referee_id = null
    is_tbd = true

A observação original deverá ser preservada.

O registro poderá permanecer provisório quando existirem:

    match_id
    official_role
    placeholder_name
    source_provider

A publicação como oficial confirmado deverá depender das regras de qualidade.

#### Resolução de duplicidade

A resolução de duplicidade deverá considerar:

- partida;
- pessoa;
- perfil de árbitro;
- função;
- ordem;
- status;
- período de validade;
- identificador externo;
- provider;
- momento da observação.

Dois providers poderão informar o mesmo árbitro com nomes ligeiramente
diferentes.

Esses registros deverão ser fundidos somente após a resolução de `Person` e
`Referee`.

#### Divergência de função

Providers poderão divergir sobre a função.

Exemplo:

    Provider A:
        pessoa X = FOURTH_OFFICIAL

    Provider B:
        pessoa X = ASSISTANT_REFEREE_2

A divergência deverá gerar conflito.

Ela não deverá ser resolvida apenas pela ordem do payload.

Deverão ser considerados:

- fonte oficial;
- competição;
- documento de nomeação;
- horário da observação;
- demais oficiais;
- substituições;
- eventos da partida.

#### Divergência de identidade

Providers poderão informar nomes diferentes para a mesma função.

Exemplo:

    Provider A:
        árbitro principal = Pessoa A

    Provider B:
        árbitro principal = Pessoa B

O sistema deverá verificar:

- se houve substituição;
- se uma fonte está desatualizada;
- se a nomeação era provisória;
- se uma pessoa atuou e outra foi apenas nomeada;
- se existe correção posterior;
- qual fonte possui maior autoridade.

A informação anterior não deverá ser apagada.

#### Histórico de nomeações

As nomeações deverão preservar períodos de validade.

Exemplo:

    nomeação original:
        appointment_status = REPLACED
        valid_until preenchido

    nova nomeação:
        appointment_status = CONFIRMED
        valid_from preenchido
        valid_until = null

O histórico deverá permitir reconstruir:

- quem foi inicialmente nomeado;
- quem foi confirmado;
- quem efetivamente atuou;
- quando ocorreu a substituição;
- qual função foi alterada;
- qual provider informou cada estado.

#### Proveniência

O campo `source_provider` poderá representar temporariamente a origem principal.

A arquitetura definitiva deverá utilizar:

    ExternalEntityMapping
    EntitySource
    ProviderObservation
    CanonicalFieldValue
    ConflictRecord

Campos críticos que deverão preservar observações incluem:

- pessoa;
- perfil de árbitro;
- função;
- ordem;
- status da nomeação;
- status da participação;
- confirmação;
- substituição;
- minuto da substituição;
- autoridade nomeadora;
- documento de nomeação;
- participação efetiva.

#### Confiança

O campo `confidence_score` deverá representar a confiança na identidade e no
contexto da nomeação.

Exemplo:

    1.0
        nomeação confirmada por fonte oficial

    0.8
        múltiplos providers confiáveis concordam

    0.5
        pessoa identificada, mas função divergente

    0.2
        nome textual incompleto ou nomeação provisória

Esse valor não deverá representar qualidade técnica do árbitro.

#### Índices recomendados para MatchOfficial

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_official_match_id` | `match_id` | Buscar oficiais de uma partida. |
| `ix_match_official_person_id` | `person_id` | Buscar nomeações de uma pessoa. |
| `ix_match_official_referee_id` | `referee_id` | Buscar partidas de um árbitro. |
| `ix_match_official_role` | `official_role` | Filtrar por função oficial. |
| `ix_match_official_order` | `match_id, official_role, official_order` | Buscar oficial pela função e ordem. |
| `ix_match_official_appointment_status` | `appointment_status` | Filtrar pelo status da nomeação. |
| `ix_match_official_participation_status` | `participation_status` | Filtrar pela situação da atuação. |
| `ix_match_official_confirmed` | `match_id, is_confirmed` | Buscar nomeações confirmadas. |
| `ix_match_official_referee_match` | `referee_id, match_id` | Consultar participação de árbitro em partida. |
| `ix_match_official_person_role` | `person_id, official_role` | Consultar histórico funcional da pessoa. |
| `ix_match_official_valid_from` | `valid_from` | Consultar início de validade. |
| `ix_match_official_valid_until` | `valid_until` | Consultar encerramento de validade. |
| `ix_match_official_replaced` | `replacement_official_id` | Localizar substituições. |
| `ix_match_official_tbd` | `is_tbd, appointment_status` | Localizar funções ainda sem oficial definido. |

Índices simples em campos booleanos poderão possuir baixa seletividade.

Índices parciais poderão ser mais eficientes.

Exemplo para árbitros principais confirmados:

    INDEX ON match_official (
        match_id,
        referee_id
    )
    WHERE official_role = 'MAIN_REFEREE'
      AND is_confirmed = true
      AND valid_until IS NULL

Exemplo para oficiais ainda não definidos:

    INDEX ON match_official (
        match_id,
        official_role
    )
    WHERE is_tbd = true

Exemplo para substituições:

    INDEX ON match_official (
        match_id,
        replacement_minute
    )
    WHERE is_replacement = true
       OR is_replaced = true

#### Restrições recomendadas

As restrições numéricas iniciais deverão incluir:

    CHECK official_order > 0

    CHECK replacement_minute >= 0

    CHECK replacement_added_time >= 0

As restrições deverão aceitar valores nulos.

Também deverá existir:

    CHECK valid_until IS NULL
       OR valid_from IS NULL
       OR valid_until >= valid_from

    CHECK ended_at IS NULL
       OR started_at IS NULL
       OR ended_at >= started_at

Uma nomeação não poderá substituir a si mesma:

    CHECK replaced_official_id IS NULL
       OR replaced_official_id <> id

    CHECK replacement_official_id IS NULL
       OR replacement_official_id <> id

A compatibilidade entre `person_id` e `referee_id` deverá ser validada pela
aplicação ou por trigger.

#### Dependências futuras

A entidade `MatchOfficial` será utilizada por:

- eventos disciplinares;
- cartões;
- expulsões;
- faltas;
- pênaltis;
- acréscimos;
- revisões de VAR;
- decisões alteradas;
- interrupções;
- súmulas;
- relatórios oficiais;
- estatísticas de arbitragem;
- análise disciplinar;
- histórico profissional;
- desempenho por competição;
- desempenho por equipe;
- modelos estatísticos;
- modelos de previsão;
- mercados relacionados a cartões;
- mercados relacionados a pênaltis;
- auditoria de providers;
- correções pós-partida;
- substituições de árbitros;
- nomeações oficiais.

Por isso, a entidade deverá preservar a função, a identidade, a validade
temporal e a participação efetiva de cada oficial sem misturar a identidade
permanente do árbitro com sua atuação contextual em uma partida.
---

### 8.5 MatchPeriod

A entidade `MatchPeriod` representa cada período esportivo, técnico ou
operacional de uma partida.

Ela deverá separar a estrutura temporal real do evento dos campos resumidos
armazenados em `Match`.

A separação será:

    Match
        estado e horários resumidos da partida

    MatchPeriod
        períodos efetivamente planejados, iniciados, interrompidos e concluídos

Essa entidade permitirá representar:

- pré-jogo;
- primeiro tempo;
- intervalo;
- segundo tempo;
- prorrogação;
- intervalos da prorrogação;
- disputa por pênaltis;
- períodos adicionais;
- partidas com formato reduzido;
- períodos suspensos;
- períodos retomados;
- acréscimos;
- duração planejada;
- duração efetiva;
- início e encerramento reais.

#### Responsabilidades

A entidade `MatchPeriod` será responsável por:

- relacionar um período à partida;
- indicar o tipo do período;
- indicar sua ordem;
- indicar seu status;
- armazenar duração planejada;
- armazenar duração regulamentar;
- armazenar acréscimos;
- armazenar duração efetiva;
- registrar início e encerramento;
- registrar minuto inicial e final;
- registrar placares no início e no final;
- indicar período interrompido;
- indicar período retomado;
- indicar período concluído;
- preservar períodos cancelados;
- preservar períodos adicionais;
- apoiar eventos;
- apoiar estatísticas;
- apoiar interrupções;
- apoiar cálculo de tempo corrido;
- apoiar normalização entre providers.

#### Campos principais

    id
    match_id
    period_type
    period_order
    period_status
    planned_duration_minutes
    regulation_duration_minutes
    announced_added_time_minutes
    actual_added_time_minutes
    elapsed_duration_seconds
    started_at
    ended_at
    start_match_minute
    end_match_minute
    home_score_at_start
    away_score_at_start
    home_score_at_end
    away_score_at_end
    is_extra_time
    is_penalty_shootout
    is_interrupted
    is_resumed
    is_completed
    source_provider
    confidence_score
    created_at
    updated_at

#### Descrição dos campos

| Campo | Tipo sugerido | Obrigatório | Descrição |
|-------|---------------|:-----------:|-----------|
| `id` | UUID | Sim | Identificador interno do período. |
| `match_id` | UUID | Sim | Partida relacionada ao período. |
| `period_type` | enum | Sim | Tipo esportivo ou operacional do período. |
| `period_order` | integer | Sim | Ordem cronológica do período na partida. |
| `period_status` | enum | Sim | Estado atual ou final do período. |
| `planned_duration_minutes` | integer | Não | Duração planejada do período. |
| `regulation_duration_minutes` | integer | Não | Duração regulamentar prevista. |
| `announced_added_time_minutes` | integer | Não | Acréscimo anunciado oficialmente. |
| `actual_added_time_minutes` | integer | Não | Acréscimo efetivamente transcorrido. |
| `elapsed_duration_seconds` | integer | Não | Duração efetiva observada em segundos. |
| `started_at` | datetime UTC | Não | Início efetivo do período. |
| `ended_at` | datetime UTC | Não | Encerramento efetivo do período. |
| `start_match_minute` | integer | Não | Minuto acumulado da partida no início do período. |
| `end_match_minute` | integer | Não | Minuto acumulado da partida no encerramento. |
| `home_score_at_start` | integer | Não | Placar do mandante no início do período. |
| `away_score_at_start` | integer | Não | Placar do visitante no início do período. |
| `home_score_at_end` | integer | Não | Placar do mandante no final do período. |
| `away_score_at_end` | integer | Não | Placar do visitante no final do período. |
| `is_extra_time` | boolean | Sim | Indica período de prorrogação. |
| `is_penalty_shootout` | boolean | Sim | Indica disputa por pênaltis. |
| `is_interrupted` | boolean | Sim | Indica que o período sofreu interrupção. |
| `is_resumed` | boolean | Sim | Indica que o período foi retomado. |
| `is_completed` | boolean | Sim | Indica encerramento normal do período. |
| `source_provider` | string | Não | Provider principal da observação. |
| `confidence_score` | decimal | Não | Confiança do período canônico. |
| `created_at` | datetime UTC | Sim | Data de criação. |
| `updated_at` | datetime UTC | Sim | Data da última atualização. |

#### Tipos de período previstos

    PRE_MATCH
    FIRST_HALF
    HALFTIME
    SECOND_HALF
    REGULATION_END
    EXTRA_TIME_FIRST_HALF
    EXTRA_TIME_HALFTIME
    EXTRA_TIME_SECOND_HALF
    EXTRA_TIME_END
    PENALTY_SHOOTOUT
    POST_MATCH
    SUSPENSION
    RESUMPTION
    ADDITIONAL_PERIOD
    UNKNOWN

`PRE_MATCH` deverá representar o período anterior ao início efetivo.

`FIRST_HALF` deverá representar o primeiro tempo regulamentar.

`HALFTIME` deverá representar o intervalo regulamentar.

`SECOND_HALF` deverá representar o segundo tempo regulamentar.

`REGULATION_END` poderá representar um marco lógico após o encerramento do tempo
regulamentar.

`EXTRA_TIME_FIRST_HALF` e `EXTRA_TIME_SECOND_HALF` deverão representar os dois
períodos da prorrogação.

`EXTRA_TIME_HALFTIME` deverá representar o intervalo da prorrogação.

`EXTRA_TIME_END` poderá representar o encerramento lógico da prorrogação.

`PENALTY_SHOOTOUT` deverá representar a disputa por pênaltis.

`POST_MATCH` deverá representar o período posterior ao encerramento esportivo.

`SUSPENSION` e `RESUMPTION` poderão ser utilizados quando o provider representar
esses momentos como períodos.

`ADDITIONAL_PERIOD` deverá apoiar formatos excepcionais.

#### Status de período previstos

    PLANNED
    PENDING
    ACTIVE
    PAUSED
    INTERRUPTED
    SUSPENDED
    RESUMED
    COMPLETED
    CANCELLED
    NOT_PLAYED
    UNKNOWN

Uma partida futura poderá possuir períodos `PLANNED`.

O período atualmente em andamento deverá possuir status `ACTIVE`.

Uma interrupção temporária poderá utilizar `INTERRUPTED` ou `PAUSED`.

Uma interrupção que impeça a continuidade imediata deverá utilizar `SUSPENDED`.

Um período encerrado normalmente deverá utilizar `COMPLETED`.

Um período que deixou de existir devido ao encerramento antecipado deverá
utilizar `NOT_PLAYED` ou `CANCELLED`, conforme o contexto.

#### Relacionamentos principais

    Match 1 ─── N MatchPeriod

    MatchPeriod 1 ─── N MatchEvent
    MatchPeriod 1 ─── N MatchStatistic
    MatchPeriod 1 ─── N MatchInterruption

Cada evento poderá referenciar o período em que ocorreu.

Cada estatística poderá ser total da partida ou específica de um período.

Cada interrupção deverá poder referenciar o período afetado.

#### Ordem dos períodos

`period_order` deverá representar a ordem cronológica, independentemente do nome
enviado pelo provider.

Exemplo tradicional:

    PRE_MATCH = 1
    FIRST_HALF = 2
    HALFTIME = 3
    SECOND_HALF = 4
    POST_MATCH = 5

Com prorrogação:

    EXTRA_TIME_FIRST_HALF = 5
    EXTRA_TIME_HALFTIME = 6
    EXTRA_TIME_SECOND_HALF = 7
    PENALTY_SHOOTOUT = 8
    POST_MATCH = 9

A ordem definitiva deverá ser normalizada conforme o formato da partida.

#### Duração regulamentar

A duração regulamentar tradicional será:

    FIRST_HALF = 45 minutos
    SECOND_HALF = 45 minutos

Entretanto, a duração não deverá ser fixada universalmente.

Competições poderão utilizar:

- dois tempos de 40 minutos;
- dois tempos de 35 minutos;
- períodos reduzidos;
- formatos de base;
- amistosos especiais;
- partidas interrompidas;
- regras históricas.

Por isso, `regulation_duration_minutes` deverá ser contextual.

#### Acréscimos

`announced_added_time_minutes` deverá representar o acréscimo mínimo anunciado.

`actual_added_time_minutes` deverá representar o tempo efetivamente jogado além
do tempo regulamentar, quando conhecido.

Exemplo:

    announced_added_time_minutes = 5
    actual_added_time_minutes = 7

Os dois valores não deverão ser tratados como equivalentes.

#### Minuto acumulado

Os campos:

    start_match_minute
    end_match_minute

deverão representar o minuto acumulado da partida.

No segundo tempo, a convenção recomendada será continuar a contagem:

    início do segundo tempo = 46

e não reiniciar em zero.

Para prorrogação:

    início do primeiro tempo da prorrogação = 91

A convenção deverá ser centralizada para todos os providers.

#### Tempo corrido

O tempo corrido poderá ser calculado usando:

    started_at
    ended_at
    elapsed_duration_seconds

Quando o relógio esportivo não coincidir com o tempo real, os dois conceitos
deverão permanecer separados.

Uma interrupção poderá aumentar o tempo real sem aumentar proporcionalmente o
minuto esportivo.

#### Compatibilidade com Match

Os períodos deverão ser compatíveis com:

    Match.actual_start_at
    Match.actual_end_at
    Match.current_period
    Match.current_minute
    Match.status

Quando o primeiro período ativo iniciar:

    Match.actual_start_at deverá ser preenchido

Quando o último período esportivo for encerrado:

    Match.actual_end_at poderá ser preenchido

Divergências deverão gerar revisão.

#### Placar por período

Os placares no início e no final deverão permitir reconstruir a evolução da
partida.

Exemplo:

    FIRST_HALF:
        home_score_at_start = 0
        away_score_at_start = 0
        home_score_at_end = 1
        away_score_at_end = 0

    SECOND_HALF:
        home_score_at_start = 1
        away_score_at_start = 0
        home_score_at_end = 2
        away_score_at_end = 1

Esses valores deverão ser compatíveis com os eventos de gol conhecidos.

#### Regras de integridade

- `match_id` deverá referenciar uma partida existente;
- `period_order` deverá ser maior que zero;
- durações deverão ser maiores ou iguais a zero;
- acréscimos deverão ser maiores ou iguais a zero;
- placares deverão ser maiores ou iguais a zero;
- `ended_at` deverá ser posterior ou igual a `started_at`;
- `end_match_minute` deverá ser posterior ou igual a `start_match_minute`;
- uma partida não deverá possuir dois períodos ativos simultaneamente, salvo
  modelagem operacional explicitamente permitida;
- `is_completed = true` deverá ser compatível com `period_status = COMPLETED`;
- `is_penalty_shootout = true` deverá ser compatível com
  `period_type = PENALTY_SHOOTOUT`;
- `is_extra_time = true` deverá ser compatível com período de prorrogação;
- períodos históricos não deverão ser removidos;
- alterações deverão preservar proveniência.

#### Índices recomendados para MatchPeriod

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_period_match_id` | `match_id` | Buscar períodos da partida. |
| `ix_match_period_type` | `period_type` | Filtrar por tipo. |
| `ix_match_period_status` | `period_status` | Filtrar por status. |
| `ix_match_period_order` | `match_id, period_order` | Ordenar períodos da partida. |
| `ix_match_period_started_at` | `started_at` | Consultar períodos iniciados. |
| `ix_match_period_active` | `match_id, period_status` | Localizar período ativo. |

Deverá existir uma restrição única sobre:

    match_id
    period_order

Uma restrição parcial poderá garantir apenas um período ativo por partida.

---

### 8.6 MatchSquad

A entidade `MatchSquad` representa o grupo de jogadores e membros técnicos
relacionados por uma equipe para uma partida.

Ela deverá permanecer separada da escalação inicial.

A separação será:

    SquadRegistration
        registro do atleta em uma competição ou temporada

    MatchSquad
        grupo relacionado para uma partida específica

    Lineup
        organização tática e escalação da equipe na partida

    LineupEntry
        pessoa ou atleta individual dentro da escalação

Um atleta poderá estar registrado na competição, ser relacionado para a partida
e ainda assim não iniciar nem entrar em campo.

#### Responsabilidades

A entidade `MatchSquad` será responsável por:

- relacionar uma equipe à partida;
- relacionar a equipe ao respectivo `MatchParticipant`;
- representar a lista de relacionados;
- indicar status da convocação;
- registrar horário de publicação;
- registrar confirmação;
- indicar lista oficial;
- indicar lista provisória;
- indicar quantidade máxima permitida;
- indicar quantidade efetivamente relacionada;
- preservar alterações;
- apoiar escalações;
- apoiar banco de reservas;
- apoiar ausências;
- apoiar validação de jogadores elegíveis.

#### Campos principais

    id
    match_id
    match_participant_id
    team_id
    squad_status
    squad_type
    published_at
    confirmed_at
    maximum_players
    listed_players
    is_official
    is_confirmed
    notes
    source_provider
    confidence_score
    created_at
    updated_at

#### Tipos de elenco da partida

    PROVISIONAL
    OFFICIAL
    MATCHDAY
    STARTERS_AND_BENCH
    TRAVELING_SQUAD
    EXTENDED
    UNKNOWN

#### Status previstos

    DRAFT
    PUBLISHED
    CONFIRMED
    UPDATED
    SUPERSEDED
    CANCELLED
    COMPLETED
    UNKNOWN

#### Relacionamentos principais

    Match 1 ─── N MatchSquad
    MatchParticipant 1 ─── 0..N MatchSquad
    Team 1 ─── N MatchSquad

    MatchSquad 1 ─── N LineupEntry
    MatchSquad 1 ─── N MatchSquadMember

A primeira implementação poderá utilizar `LineupEntry` como membro individual.

Caso seja necessário representar relacionados ainda sem escalação, poderá ser
criada futuramente:

    MatchSquadMember
    ├── id
    ├── match_squad_id
    ├── player_id
    ├── person_id
    ├── squad_role
    ├── eligibility_status
    ├── is_available
    ├── is_withdrawn
    └── source_provider

#### Compatibilidade com MatchParticipant

Deverá existir compatibilidade:

    match_squad.match_id =
        match_participant.match_id

e:

    match_squad.team_id =
        match_participant.team_id

Uma equipe não participante não poderá possuir elenco na partida.

#### Lista provisória e lista oficial

Uma lista provisória não deverá sobrescrever uma lista oficial anterior sem
histórico.

Quando uma nova versão for publicada:

    lista anterior:
        squad_status = SUPERSEDED

    nova lista:
        squad_status = PUBLISHED ou CONFIRMED

O momento de publicação deverá ser preservado.

#### Elegibilidade

A presença no `MatchSquad` não deverá provar automaticamente elegibilidade.

A elegibilidade poderá depender de:

- registro na competição;
- suspensão;
- limite de estrangeiros;
- idade;
- inscrição na fase;
- transferência;
- documentação;
- punição;
- regulamento.

Futuramente, a elegibilidade deverá ser representada por entidade ou serviço de
domínio específico.

#### Regras de integridade

- `match_id` deverá referenciar uma partida;
- `match_participant_id` deverá pertencer à mesma partida;
- `team_id` deverá corresponder ao participante;
- quantidades deverão ser maiores ou iguais a zero;
- `listed_players` não deverá normalmente superar `maximum_players`;
- apenas uma lista oficial vigente deverá existir por participante;
- listas antigas deverão ser preservadas;
- conflitos de providers deverão ser auditáveis.

#### Índices recomendados para MatchSquad

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_squad_match_id` | `match_id` | Buscar elencos da partida. |
| `ix_match_squad_participant_id` | `match_participant_id` | Buscar elenco do participante. |
| `ix_match_squad_team_id` | `team_id` | Buscar elencos por equipe. |
| `ix_match_squad_status` | `squad_status` | Filtrar por status. |
| `ix_match_squad_match_team` | `match_id, team_id` | Localizar elenco da equipe na partida. |

---

### 8.7 Lineup

A entidade `Lineup` representa a escalação contextual de uma equipe em uma
partida.

Ela deverá armazenar a configuração geral da equipe, enquanto `LineupEntry`
representará os integrantes individualmente.

A separação será:

    Lineup
        cabeçalho, formação, status e contexto da escalação

    LineupEntry
        jogadores, reservas, capitães e membros técnicos

Uma equipe poderá possuir mais de uma versão da escalação devido a:

- escalação provável;
- escalação publicada;
- correção;
- alteração antes do início;
- mudança de formação;
- divergência de provider;
- histórico de atualização.

#### Responsabilidades

A entidade `Lineup` será responsável por:

- relacionar a escalação à partida;
- relacionar a escalação à equipe;
- relacionar a escalação ao participante;
- relacionar a escalação ao elenco da partida;
- indicar tipo e status;
- armazenar formação tática;
- indicar treinador responsável;
- registrar publicação e confirmação;
- indicar escalação inicial;
- indicar escalação provável;
- indicar escalação oficial;
- preservar versões;
- apoiar visualização tática;
- apoiar análise estatística;
- apoiar modelos preditivos.

#### Campos principais

    id
    match_id
    match_participant_id
    match_squad_id
    team_id
    coach_person_id
    lineup_type
    lineup_status
    formation
    formation_normalized
    version_number
    published_at
    confirmed_at
    valid_from
    valid_until
    is_probable
    is_official
    is_starting_lineup
    is_current
    source_provider
    confidence_score
    created_at
    updated_at

#### Tipos de escalação previstos

    PROBABLE
    PROJECTED
    PRELIMINARY
    OFFICIAL
    STARTING
    IN_PLAY
    FINAL
    UNKNOWN

#### Status previstos

    DRAFT
    PUBLISHED
    CONFIRMED
    UPDATED
    SUPERSEDED
    CANCELLED
    COMPLETED
    UNKNOWN

#### Formação tática

O campo `formation` deverá preservar o valor original do provider.

Exemplos:

    4-3-3
    4-2-3-1
    3-5-2
    4-4-2 diamond
    3-4-2-1

O campo `formation_normalized` deverá conter uma representação normalizada.

A normalização não deverá eliminar informação relevante.

Exemplo:

    valor original:
        4-4-1-1

    valor normalizado:
        4-4-1-1

Não deverá ser convertido automaticamente para `4-4-2` sem regra explícita.

#### Alterações de formação

Uma equipe poderá mudar de formação durante a partida.

A escalação inicial deverá permanecer preservada.

Mudanças táticas poderão ser representadas futuramente por:

    TacticalShapeChange
    ├── match_id
    ├── match_participant_id
    ├── previous_formation
    ├── new_formation
    ├── match_period_id
    ├── minute
    └── source_provider

`Lineup` não deverá ser sobrescrita continuamente para representar cada alteração
em campo.

#### Compatibilidade com MatchParticipant

Deverá existir compatibilidade:

    lineup.match_id =
        match_participant.match_id

    lineup.team_id =
        match_participant.team_id

#### Compatibilidade com MatchSquad

Quando `match_squad_id` estiver preenchido:

    lineup.match_id =
        match_squad.match_id

    lineup.team_id =
        match_squad.team_id

#### Versões

`version_number` deverá ser crescente dentro da mesma partida e equipe.

Uma nova escalação deverá ser criada quando houver alteração estrutural
relevante.

A versão anterior deverá receber:

    lineup_status = SUPERSEDED
    is_current = false
    valid_until preenchido

A nova versão deverá possuir:

    is_current = true
    valid_from preenchido

#### Regras de integridade

- uma escalação deverá pertencer a uma equipe participante;
- `version_number` deverá ser maior que zero;
- apenas uma versão atual deverá existir por equipe e tipo;
- uma escalação oficial deverá ser compatível com status confirmado;
- períodos de validade não deverão se sobrepor indevidamente;
- escalações antigas não deverão ser excluídas;
- formação vazia não deverá ser substituída por valor inventado.

#### Índices recomendados para Lineup

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_lineup_match_id` | `match_id` | Buscar escalações da partida. |
| `ix_lineup_participant_id` | `match_participant_id` | Buscar escalação do participante. |
| `ix_lineup_team_id` | `team_id` | Buscar escalações da equipe. |
| `ix_lineup_status` | `lineup_status` | Filtrar por status. |
| `ix_lineup_match_team_version` | `match_id, team_id, version_number` | Consultar versões. |
| `ix_lineup_current` | `match_id, team_id, is_current` | Localizar escalação atual. |

---

### 8.8 LineupEntry

A entidade `LineupEntry` representa uma pessoa relacionada à escalação ou ao
elenco contextual de uma equipe na partida.

Ela poderá representar:

- titular;
- reserva;
- jogador não utilizado;
- goleiro;
- capitão;
- treinador;
- auxiliar;
- membro técnico;
- atleta retirado antes do início;
- atleta ainda não identificado.

#### Responsabilidades

A entidade `LineupEntry` será responsável por:

- relacionar jogador ou pessoa à escalação;
- relacionar o integrante ao participante;
- indicar papel na escalação;
- indicar posição;
- indicar número da camisa;
- indicar status;
- indicar titularidade;
- indicar presença no banco;
- indicar participação;
- indicar capitão;
- indicar goleiro;
- registrar entrada e saída;
- relacionar eventos de substituição;
- preservar posição contextual;
- preservar número contextual;
- apoiar estatísticas por jogador;
- apoiar validação de eventos.

#### Campos principais

    id
    lineup_id
    match_id
    match_participant_id
    match_squad_id
    team_id
    person_id
    player_id
    lineup_role
    lineup_status
    position
    position_normalized
    shirt_number
    tactical_slot
    display_order
    started_match
    was_substitute
    entered_match
    left_match
    remained_unused
    is_captain
    is_goalkeeper
    is_tbd
    entry_period_id
    exit_period_id
    entry_minute
    entry_added_time
    exit_minute
    exit_added_time
    source_provider
    confidence_score
    created_at
    updated_at

#### Papéis previstos

    STARTER
    SUBSTITUTE
    UNUSED_SUBSTITUTE
    RESERVE_GOALKEEPER
    COACH
    ASSISTANT_COACH
    FITNESS_COACH
    GOALKEEPER_COACH
    MEDICAL_STAFF
    TECHNICAL_STAFF
    WITHDRAWN
    INELIGIBLE
    UNKNOWN

#### Status previstos

    EXPECTED
    CONFIRMED
    ACTIVE
    SUBSTITUTED_IN
    SUBSTITUTED_OUT
    UNUSED
    WITHDRAWN
    DISQUALIFIED
    COMPLETED
    UNKNOWN

#### Posição contextual

A posição armazenada em `LineupEntry` deverá representar a função do jogador
naquela partida.

Ela não deverá substituir a posição preferencial armazenada no perfil do
jogador.

Exemplo:

    Player.position = MIDFIELDER

    LineupEntry.position = RIGHT_BACK

Isso poderá ocorrer devido a uma adaptação tática.

#### Número da camisa

`shirt_number` deverá ser contextual à partida.

Ele poderá divergir do número normalmente utilizado pelo atleta.

A ausência de número não deverá receber zero automaticamente.

#### Titular e reserva

Para titular:

    started_match = true
    was_substitute = false
    lineup_role = STARTER

Para reserva:

    started_match = false
    was_substitute = true

Um reserva que entrar deverá possuir:

    entered_match = true
    remained_unused = false

Um reserva não utilizado deverá possuir:

    entered_match = false
    remained_unused = true

#### Substituições

A entrada e saída poderão ser resumidas em `LineupEntry`, mas o evento oficial
deverá permanecer em `MatchEvent`.

Exemplo:

    entry_minute = 65
    entry_added_time = 0

Esses campos deverão ser compatíveis com o evento de substituição.

#### Compatibilidade com Player e Person

Quando `player_id` estiver preenchido:

    lineup_entry.person_id =
        player.person_id

Membros técnicos poderão possuir:

    person_id preenchido
    player_id = null

#### Compatibilidade com a equipe

Deverá existir compatibilidade entre:

    lineup_entry.team_id
    lineup.team_id
    match_participant.team_id

Uma pessoa não deverá ser associada à equipe adversária por erro de provider.

#### Regras de integridade

- `lineup_id` deverá referenciar uma escalação existente;
- `match_id`, `team_id` e `match_participant_id` deverão ser compatíveis;
- `player_id` e `person_id`, quando presentes, deverão representar a mesma
  pessoa;
- `shirt_number`, quando informado, deverá ser maior ou igual a zero;
- minutos deverão ser maiores ou iguais a zero;
- `started_match` e `was_substitute` não deverão ser verdadeiros simultaneamente;
- `remained_unused = true` deverá implicar `entered_match = false`;
- `is_tbd = false` deverá normalmente exigir pessoa ou jogador;
- o mesmo jogador não deverá aparecer duas vezes na mesma versão da escalação;
- o mesmo número poderá exigir validação conforme o regulamento;
- registros históricos não deverão ser removidos.

#### Índices recomendados para LineupEntry

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_lineup_entry_lineup_id` | `lineup_id` | Buscar integrantes da escalação. |
| `ix_lineup_entry_match_id` | `match_id` | Buscar integrantes da partida. |
| `ix_lineup_entry_player_id` | `player_id` | Buscar partidas do jogador. |
| `ix_lineup_entry_person_id` | `person_id` | Buscar participações da pessoa. |
| `ix_lineup_entry_team_id` | `team_id` | Buscar integrantes por equipe. |
| `ix_lineup_entry_match_player` | `match_id, player_id` | Localizar jogador na partida. |
| `ix_lineup_entry_role` | `lineup_role` | Filtrar titulares e reservas. |

---

### 8.9 MatchEvent

A entidade `MatchEvent` representa um acontecimento esportivo, disciplinar,
tático, técnico ou administrativo ocorrido no contexto de uma partida.

Ela será uma das entidades centrais do domínio.

Eventos deverão ser armazenados de maneira estruturada, ordenável, auditável e
compatível com múltiplos providers.

#### Responsabilidades

A entidade `MatchEvent` será responsável por:

- relacionar um evento à partida;
- relacionar o evento a um período;
- indicar o tipo do evento;
- indicar sua ordem cronológica;
- armazenar minuto e acréscimo;
- armazenar momento real;
- relacionar equipe;
- relacionar participante;
- relacionar jogador;
- relacionar pessoa;
- relacionar oficial;
- relacionar evento principal e evento relacionado;
- armazenar resultado do evento;
- armazenar placar após o evento;
- indicar confirmação;
- indicar anulação;
- indicar revisão;
- preservar correções;
- preservar proveniência;
- apoiar estatísticas;
- apoiar mercados ao vivo;
- apoiar modelos analíticos.

#### Campos principais

    id
    match_id
    match_period_id
    match_participant_id
    team_id
    person_id
    player_id
    related_person_id
    related_player_id
    match_official_id
    parent_event_id
    related_event_id
    event_type
    event_subtype
    event_status
    event_order
    minute
    added_time
    second_in_minute
    occurred_at
    home_score_after
    away_score_after
    outcome
    location_x
    location_y
    body_part
    play_situation
    description
    is_confirmed
    is_cancelled
    is_overturned
    is_var_reviewed
    source_provider
    confidence_score
    created_at
    updated_at

#### Tipos de evento previstos

    MATCH_START
    PERIOD_START
    PERIOD_END
    MATCH_END
    GOAL
    OWN_GOAL
    PENALTY_GOAL
    PENALTY_MISSED
    PENALTY_SAVED
    SHOT
    SHOT_ON_TARGET
    SHOT_OFF_TARGET
    SHOT_BLOCKED
    SUBSTITUTION
    YELLOW_CARD
    SECOND_YELLOW_CARD
    RED_CARD
    FOUL
    OFFSIDE
    CORNER
    FREE_KICK
    PENALTY_AWARDED
    PENALTY_CANCELLED
    VAR_REVIEW
    VAR_DECISION
    INJURY
    MEDICAL_ATTENDANCE
    INTERRUPTION
    RESUMPTION
    WEATHER_DELAY
    CROWD_INCIDENT
    TECHNICAL_FAILURE
    BALL_IN_PLAY
    BALL_OUT_OF_PLAY
    FORMATION_CHANGE
    CAPTAIN_CHANGE
    GOALKEEPER_CHANGE
    ADMINISTRATIVE_DECISION
    OTHER
    UNKNOWN

#### Status previstos

    PROVISIONAL
    CONFIRMED
    CORRECTED
    CANCELLED
    OVERTURNED
    SUPERSEDED
    DISPUTED
    UNKNOWN

#### Ordem cronológica

`event_order` deverá fornecer uma ordem estável dentro da partida.

Ela será necessária porque múltiplos eventos poderão possuir o mesmo minuto.

Exemplo:

    90+3 gol
    90+3 cartão
    90+3 revisão de VAR

O minuto isolado não será suficiente para ordenar os acontecimentos.

#### Minuto e acréscimo

A convenção deverá separar:

    minute = 45
    added_time = 2

para representar:

    45+2

O campo `second_in_minute` poderá aumentar a precisão quando disponível.

O valor textual `45+2` não deverá ser o único valor armazenado.

#### Momento real

`occurred_at` deverá representar o horário real do evento quando disponível.

Ele poderá ser utilizado para:

- sincronização ao vivo;
- latência de provider;
- auditoria;
- reprodução temporal;
- comparação entre fontes.

O horário real não deverá substituir o minuto esportivo.

#### Gols

Eventos de gol deverão indicar:

- equipe beneficiada;
- jogador autor;
- assistência, quando conhecida;
- tipo do gol;
- placar após o evento;
- período;
- minuto;
- situação da jogada;
- confirmação;
- eventual anulação.

Um gol contra deverá utilizar:

    event_type = OWN_GOAL

A equipe relacionada deverá ser a equipe que recebeu o gol no placar.

O jogador relacionado poderá pertencer à equipe adversária.

#### Assistências

Uma assistência poderá utilizar:

    related_player_id

ou uma entidade futura de participantes do evento.

Para eventos com múltiplos envolvidos, deverá ser criada futuramente:

    MatchEventParticipant
    ├── match_event_id
    ├── person_id
    ├── player_id
    ├── team_id
    ├── participant_role
    └── sequence

Papéis possíveis:

    PRIMARY_ACTOR
    ASSISTANT
    VICTIM
    FOUL_COMMITTED_BY
    FOUL_SUFFERED_BY
    GOALKEEPER
    REVIEWING_OFFICIAL
    OTHER

#### Substituições

Um evento de substituição deverá relacionar:

    player_id
        jogador que saiu

    related_player_id
        jogador que entrou

A convenção deverá ser única em toda a aplicação.

O evento deverá ser compatível com os respectivos `LineupEntry`.

#### Cartões

Cartões deverão indicar:

    YELLOW_CARD
    SECOND_YELLOW_CARD
    RED_CARD

Um segundo amarelo que resulte em expulsão não deverá ser armazenado apenas como
`RED_CARD`.

A sequência disciplinar deverá permanecer explícita.

#### Revisão de VAR

Uma revisão poderá ser representada por eventos relacionados:

    VAR_REVIEW
    VAR_DECISION

O evento revisado deverá ser referenciado por:

    related_event_id

A decisão final poderá:

- confirmar;
- cancelar;
- alterar;
- substituir;
- manter com correção.

#### Eventos anulados

Um evento anulado não deverá ser removido.

Exemplo:

    gol marcado
    revisão de VAR
    gol anulado

O evento original deverá permanecer:

    is_cancelled = true
    is_overturned = true
    event_status = OVERTURNED

O placar canônico deverá desconsiderá-lo.

#### Localização do evento

Os campos:

    location_x
    location_y

deverão utilizar sistema normalizado.

Uma convenção recomendada será:

    x entre 0 e 100
    y entre 0 e 100

A orientação deverá ser documentada.

Dados originais do provider deverão permanecer na camada de observação.

#### Situações de jogada

`play_situation` poderá utilizar valores como:

    OPEN_PLAY
    COUNTER_ATTACK
    CORNER
    FREE_KICK
    DIRECT_FREE_KICK
    INDIRECT_FREE_KICK
    PENALTY
    THROW_IN
    SET_PIECE
    UNKNOWN

#### Parte do corpo

`body_part` poderá utilizar:

    RIGHT_FOOT
    LEFT_FOOT
    HEAD
    CHEST
    HAND
    OTHER
    UNKNOWN

#### Compatibilidade com placar

Após um gol confirmado:

    home_score_after
    away_score_after

deverão ser compatíveis com a sequência anterior de eventos.

Um evento anulado não deverá incrementar o placar canônico.

#### Regras de integridade

- `match_id` deverá referenciar uma partida;
- o período deverá pertencer à mesma partida;
- equipe e participante deverão ser compatíveis;
- jogador e pessoa deverão ser compatíveis;
- minutos e acréscimos deverão ser maiores ou iguais a zero;
- `event_order` deverá ser maior que zero;
- coordenadas normalizadas deverão permanecer no intervalo definido;
- um evento não poderá ser pai de si mesmo;
- um evento não poderá relacionar a si mesmo;
- eventos cancelados deverão permanecer armazenados;
- alterações deverão preservar histórico;
- placares após eventos deverão ser maiores ou iguais a zero;
- conflitos entre providers deverão ser auditáveis.

#### Unicidade e deduplicação

Não deverá existir uma unicidade simples baseada apenas em:

    match_id
    event_type
    minute
    player_id

Dois eventos reais poderão compartilhar esses valores.

A deduplicação deverá considerar:

- identificador externo;
- sequência;
- segundo;
- período;
- equipe;
- jogador;
- placar;
- subtipo;
- descrição;
- eventos relacionados;
- provider;
- horário de observação.

#### Índices recomendados para MatchEvent

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_event_match_id` | `match_id` | Buscar eventos da partida. |
| `ix_match_event_period_id` | `match_period_id` | Buscar eventos do período. |
| `ix_match_event_team_id` | `team_id` | Buscar eventos da equipe. |
| `ix_match_event_player_id` | `player_id` | Buscar eventos do jogador. |
| `ix_match_event_type` | `event_type` | Filtrar por tipo. |
| `ix_match_event_order` | `match_id, event_order` | Ordenar eventos. |
| `ix_match_event_minute` | `match_id, minute, added_time` | Consultar linha do tempo. |
| `ix_match_event_related` | `related_event_id` | Buscar eventos relacionados. |
| `ix_match_event_confirmed` | `match_id, is_confirmed` | Buscar eventos confirmados. |

---

### 8.10 MatchStatistic

A entidade `MatchStatistic` representa uma métrica estatística observada ou
calculada no contexto de uma partida.

Ela deverá suportar estatísticas:

- da partida;
- de uma equipe;
- de um participante;
- de um jogador;
- de um período;
- de uma janela temporal;
- observadas por provider;
- calculadas internamente.

#### Responsabilidades

A entidade `MatchStatistic` será responsável por:

- relacionar estatística à partida;
- relacionar estatística ao período;
- relacionar estatística à equipe;
- relacionar estatística ao participante;
- relacionar estatística ao jogador;
- indicar tipo da estatística;
- indicar unidade;
- armazenar valor numérico;
- armazenar valor textual original;
- indicar escopo;
- indicar método de cálculo;
- indicar se o valor é oficial;
- indicar se é calculado;
- indicar se é estimado;
- preservar proveniência;
- preservar confiança;
- apoiar agregações;
- apoiar modelos de IA;
- apoiar comparação entre providers.

#### Campos principais

    id
    match_id
    match_period_id
    match_participant_id
    team_id
    person_id
    player_id
    statistic_type
    statistic_scope
    statistic_unit
    numeric_value
    text_value
    numerator
    denominator
    percentage_value
    calculation_method
    observed_at
    is_official
    is_calculated
    is_estimated
    source_provider
    confidence_score
    created_at
    updated_at

#### Escopos previstos

    MATCH
    TEAM
    PARTICIPANT
    PLAYER
    PERIOD
    GOALKEEPER
    OFFICIAL
    UNKNOWN

#### Unidades previstas

    COUNT
    PERCENT
    SECONDS
    MINUTES
    METERS
    KILOMETERS
    KILOMETERS_PER_HOUR
    EXPECTED_GOALS
    RATIO
    SCORE
    TEXT
    OTHER
    UNKNOWN

#### Tipos iniciais de estatística

    POSSESSION_PERCENT
    SHOTS
    SHOTS_ON_TARGET
    SHOTS_OFF_TARGET
    SHOTS_BLOCKED
    SHOTS_INSIDE_BOX
    SHOTS_OUTSIDE_BOX
    GOALS
    EXPECTED_GOALS
    EXPECTED_GOALS_ON_TARGET
    BIG_CHANCES
    BIG_CHANCES_MISSED
    CORNERS
    OFFSIDES
    FOULS
    YELLOW_CARDS
    RED_CARDS
    PASSES
    PASSES_COMPLETED
    PASS_ACCURACY_PERCENT
    CROSSES
    CROSSES_COMPLETED
    TACKLES
    INTERCEPTIONS
    CLEARANCES
    BLOCKS
    SAVES
    DUELS
    DUELS_WON
    AERIAL_DUELS
    AERIAL_DUELS_WON
    BALL_RECOVERIES
    BALL_LOSSES
    DANGEROUS_ATTACKS
    ATTACKS
    DISTANCE_COVERED
    SPRINTS
    TOUCHES
    TOUCHES_IN_BOX
    PENALTIES
    PENALTIES_SCORED
    PENALTIES_MISSED
    FREE_KICKS
    THROW_INS
    GOAL_KICKS
    OTHER
    UNKNOWN

A enumeração deverá crescer de forma controlada.

Tipos específicos de providers não deverão ser adicionados diretamente sem
normalização.

#### Valor numérico e percentual

Contagens deverão utilizar:

    numeric_value

Percentuais poderão utilizar:

    percentage_value

Quando o provider fornecer numerador e denominador:

    numerator
    denominator

deverão ser preservados.

Exemplo:

    passes completed = 420
    passes attempted = 500
    percentage = 84

A porcentagem poderá ser recalculada, mas o valor original deverá permanecer
auditável.

#### Estatísticas calculadas

Quando:

    is_calculated = true

`calculation_method` deverá indicar a versão ou método utilizado.

Exemplo:

    internal:xg:model_v3

Valores calculados internamente não deverão ser apresentados como estatísticas
oficiais do provider.

#### Estatísticas estimadas

Quando:

    is_estimated = true

o sistema deverá indicar que o valor não foi diretamente observado.

Exemplos:

- posse estimada;
- distância estimada;
- xG calculado;
- pressão estimada;
- intensidade ofensiva inferida.

#### Compatibilidade com participante

Quando a estatística for de equipe:

    team_id
    match_participant_id

deverão ser compatíveis.

Uma estatística do jogador deverá possuir jogador pertencente ao participante
ou equipe no contexto do evento.

#### Estatísticas por período

Quando `match_period_id` estiver preenchido, o período deverá pertencer à mesma
partida.

Estatísticas do primeiro e segundo tempo não deverão ser misturadas com o total
sem indicação explícita.

#### Correções

Providers poderão corrigir estatísticas após a partida.

O valor anterior não deverá ser perdido na camada de observações.

O valor canônico poderá ser atualizado conforme a prioridade e a confiança das
fontes.

#### Regras de integridade

- a estatística deverá pertencer a uma partida;
- entidades relacionadas deverão ser compatíveis com a partida;
- percentuais deverão normalmente permanecer entre zero e cem;
- denominadores deverão ser maiores ou iguais a zero;
- contagens não deverão ser negativas, salvo tipo explicitamente permitido;
- valores calculados deverão indicar método quando necessário;
- valores estimados deverão ser identificados;
- tipo e unidade deverão ser compatíveis;
- conflitos deverão ser preservados.

#### Unicidade contextual

Uma chave candidata poderá considerar:

    match_id
    match_period_id
    match_participant_id
    player_id
    statistic_type
    statistic_scope
    source_provider

A chave definitiva dependerá da estratégia de proveniência.

#### Índices recomendados para MatchStatistic

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_statistic_match_id` | `match_id` | Buscar estatísticas da partida. |
| `ix_match_statistic_period_id` | `match_period_id` | Buscar estatísticas do período. |
| `ix_match_statistic_team_id` | `team_id` | Buscar estatísticas da equipe. |
| `ix_match_statistic_player_id` | `player_id` | Buscar estatísticas do jogador. |
| `ix_match_statistic_type` | `statistic_type` | Filtrar por tipo. |
| `ix_match_statistic_match_type` | `match_id, statistic_type` | Buscar métrica na partida. |
| `ix_match_statistic_team_type` | `team_id, statistic_type` | Agregar métricas por equipe. |

---

### 8.11 MatchInterruption

A entidade `MatchInterruption` representa uma paralisação temporária, suspensão
ou interrupção operacional da partida.

Ela deverá permanecer separada de `MatchEvent` porque interrupções podem possuir
duração, causa, responsabilidade, impacto e resolução próprios.

#### Responsabilidades

A entidade `MatchInterruption` será responsável por:

- relacionar interrupção à partida;
- relacionar interrupção ao período;
- indicar tipo;
- indicar status;
- registrar início e fim;
- registrar minuto esportivo;
- registrar duração;
- registrar motivo;
- indicar retomada;
- indicar impacto no calendário;
- indicar impacto no resultado;
- relacionar evento de início;
- relacionar evento de retomada;
- preservar decisões;
- apoiar cálculo de tempo real;
- apoiar alertas;
- apoiar auditoria.

#### Campos principais

    id
    match_id
    match_period_id
    start_event_id
    end_event_id
    interruption_type
    interruption_status
    started_at
    ended_at
    start_minute
    start_added_time
    end_minute
    end_added_time
    duration_seconds
    reason
    resolution
    is_match_suspended
    is_match_resumed
    affected_schedule
    affected_result
    source_provider
    confidence_score
    created_at
    updated_at

#### Tipos de interrupção previstos

    INJURY
    MEDICAL_EMERGENCY
    WEATHER
    LIGHTNING
    HEAVY_RAIN
    SNOW
    FOG
    PITCH_CONDITION
    CROWD_INCIDENT
    SECURITY_INCIDENT
    OBJECTS_ON_FIELD
    PITCH_INVASION
    RACISM_PROTOCOL
    TECHNICAL_FAILURE
    LIGHTING_FAILURE
    VAR_FAILURE
    GOAL_STRUCTURE_FAILURE
    EQUIPMENT_FAILURE
    REFEREE_INJURY
    PLAYER_PROTEST
    TEAM_WITHDRAWAL
    BALL_UNAVAILABLE
    EXTERNAL_INTERFERENCE
    ADMINISTRATIVE
    UNKNOWN

#### Status previstos

    ACTIVE
    RESOLVED
    RESUMED
    ESCALATED
    SUSPENDED
    ABANDONED
    CANCELLED
    UNKNOWN

#### Suspensão e abandono

Uma interrupção temporária não deverá alterar automaticamente o status da
partida para `ABANDONED`.

Quando houver suspensão:

    is_match_suspended = true

Quando houver retomada:

    is_match_resumed = true
    ended_at preenchido

Quando não houver retomada, uma decisão posterior poderá definir:

- continuação em outra data;
- encerramento antecipado;
- abandono;
- resultado administrativo;
- repetição.

#### Duração

`duration_seconds` poderá ser calculado a partir de:

    started_at
    ended_at

O valor observado pelo provider poderá ser preservado quando divergir.

#### Relação com MatchEvent

A interrupção poderá possuir:

    start_event_id
    end_event_id

Isso permitirá navegação entre a linha do tempo e a estrutura operacional.

#### Regras de integridade

- a interrupção deverá pertencer a uma partida;
- o período deverá pertencer à mesma partida;
- eventos relacionados deverão pertencer à mesma partida;
- tempos e durações deverão ser maiores ou iguais a zero;
- `ended_at` deverá ser posterior ou igual a `started_at`;
- interrupção resolvida deverá possuir encerramento quando conhecido;
- interrupções não deverão ser removidas;
- múltiplas interrupções simultâneas poderão existir quando representarem causas
  distintas;
- causas e decisões deverão ser auditáveis.

#### Índices recomendados para MatchInterruption

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_interruption_match_id` | `match_id` | Buscar interrupções da partida. |
| `ix_match_interruption_period_id` | `match_period_id` | Buscar interrupções do período. |
| `ix_match_interruption_type` | `interruption_type` | Filtrar por causa. |
| `ix_match_interruption_status` | `interruption_status` | Filtrar interrupções ativas. |
| `ix_match_interruption_started_at` | `started_at` | Consultar início das interrupções. |

---

### 8.12 MatchScheduleChange

A entidade `MatchScheduleChange` representa qualquer alteração relevante no
calendário, horário ou local de uma partida.

Ela deverá preservar o valor anterior e o novo valor.

A entidade não deverá substituir diretamente o estado atual de `Match`.

Ela funcionará como histórico auditável das alterações.

#### Responsabilidades

A entidade `MatchScheduleChange` será responsável por:

- relacionar alteração à partida;
- indicar tipo da alteração;
- preservar data anterior;
- preservar nova data;
- preservar horário anterior;
- preservar novo horário;
- preservar estádio anterior;
- preservar novo estádio;
- preservar cidade anterior;
- preservar nova cidade;
- preservar fuso anterior;
- preservar novo fuso;
- indicar motivo;
- indicar autoridade;
- registrar anúncio;
- registrar vigência;
- indicar confirmação;
- indicar cancelamento;
- relacionar alteração anterior;
- preservar proveniência;
- apoiar notificações;
- apoiar auditoria;
- apoiar reconstrução histórica.

#### Campos principais

    id
    match_id
    previous_change_id
    change_type
    change_status
    previous_scheduled_start_at
    new_scheduled_start_at
    previous_sporting_date
    new_sporting_date
    previous_timezone
    new_timezone
    previous_stadium_id
    new_stadium_id
    previous_city_id
    new_city_id
    reason
    announced_by
    announced_at
    effective_at
    is_official
    is_confirmed
    source_provider
    confidence_score
    created_at
    updated_at

#### Tipos de alteração previstos

    DATE_CHANGE
    TIME_CHANGE
    DATE_AND_TIME_CHANGE
    TIMEZONE_CORRECTION
    SPORTING_DATE_CHANGE
    VENUE_CHANGE
    CITY_CHANGE
    POSTPONEMENT
    RESCHEDULING
    ANTICIPATION
    DELAY
    EMERGENCY_RELOCATION
    CANCELLATION
    REINSTATEMENT
    CORRECTION
    OTHER
    UNKNOWN

#### Status previstos

    PROPOSED
    ANNOUNCED
    CONFIRMED
    APPLIED
    SUPERSEDED
    CANCELLED
    REJECTED
    UNKNOWN

#### Data esportiva e horário UTC

Uma alteração de horário poderá não alterar a data esportiva.

Exemplo:

    início anterior:
        2026-08-10 23:30 UTC

    novo início:
        2026-08-11 00:30 UTC

Dependendo do fuso local, a data esportiva poderá permanecer a mesma.

Por isso, deverão permanecer separados:

    scheduled_start_at
    sporting_date
    timezone

#### Adiamento

Um adiamento deverá indicar que a partida não ocorrerá no horário anteriormente
previsto.

A nova data poderá ainda ser desconhecida.

Nesse caso:

    previous_scheduled_start_at preenchido
    new_scheduled_start_at = null
    change_type = POSTPONEMENT

Quando a nova data for definida, poderá ser criado novo registro:

    change_type = RESCHEDULING

#### Atraso

Um atraso no início poderá ser representado por:

    change_type = DELAY

Pequenas diferenças entre horário previsto e início real não deverão gerar
automaticamente uma alteração formal.

A entidade deverá representar mudanças oficialmente relevantes.

#### Mudança de local

Quando houver mudança de estádio, o histórico deverá ser compatível com
`MatchVenue`.

O novo `MatchVenue` deverá ser criado ou confirmado.

O local anterior deverá ser encerrado ou marcado como alterado.

#### Compatibilidade com Match

Após uma alteração aplicada:

    Match.scheduled_start_at =
        MatchScheduleChange.new_scheduled_start_at

quando o novo valor estiver disponível.

O histórico não deverá depender apenas do valor atual armazenado em `Match`.

#### Cadeia de alterações

Uma partida poderá sofrer várias mudanças.

Exemplo:

    horário alterado
    partida adiada
    novo horário anunciado
    estádio alterado

`previous_change_id` poderá formar uma sequência lógica.

A ordem real também poderá ser reconstruída por `announced_at` e `effective_at`.

#### Regras de integridade

- a alteração deverá referenciar uma partida;
- referências anteriores e novas deverão ser diferentes quando o tipo exigir;
- `previous_change_id` não poderá referenciar o próprio registro;
- horários deverão utilizar UTC;
- cidades e estádios deverão existir quando informados;
- alteração confirmada deverá possuir origem confiável;
- registros aplicados não deverão ser apagados;
- uma alteração cancelada deverá permanecer no histórico;
- mudanças deverão ser compatíveis com o estado atual de `Match`.

#### Índices recomendados para MatchScheduleChange

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_schedule_change_match_id` | `match_id` | Buscar alterações da partida. |
| `ix_match_schedule_change_type` | `change_type` | Filtrar por tipo. |
| `ix_match_schedule_change_status` | `change_status` | Filtrar por status. |
| `ix_match_schedule_change_announced_at` | `announced_at` | Ordenar anúncios. |
| `ix_match_schedule_change_effective_at` | `effective_at` | Consultar vigência. |
| `ix_match_schedule_change_match_announced` | `match_id, announced_at` | Reconstruir histórico. |

---

### 8.13 MatchDecision

A entidade `MatchDecision` representa uma decisão oficial, administrativa,
disciplinar ou regulamentar que afeta a partida, seus participantes ou seu
resultado.

Ela deverá permanecer separada do placar observado em campo.

#### Responsabilidades

A entidade `MatchDecision` será responsável por:

- relacionar decisão à partida;
- indicar tipo;
- indicar status;
- relacionar participante afetado;
- relacionar equipe beneficiada;
- relacionar equipe penalizada;
- relacionar oficial ou autoridade;
- armazenar placar concedido;
- armazenar resultado concedido;
- indicar impacto no resultado;
- indicar impacto na classificação;
- indicar impacto na continuidade;
- registrar fundamento;
- registrar autoridade;
- registrar anúncio;
- registrar vigência;
- preservar recursos;
- preservar revisões;
- apoiar walkover;
- apoiar abandono;
- apoiar desclassificação;
- apoiar repetição;
- apoiar anulação;
- preservar proveniência.

#### Campos principais

    id
    match_id
    match_participant_id
    benefited_team_id
    penalized_team_id
    related_official_id
    decision_type
    decision_status
    awarded_home_score
    awarded_away_score
    awarded_winner_team_id
    reason
    legal_basis
    authority_name
    reference_number
    decided_at
    effective_at
    appealed_at
    resolved_at
    affects_result
    affects_qualification
    affects_schedule
    requires_replay
    is_final
    source_provider
    confidence_score
    created_at
    updated_at

#### Tipos de decisão previstos

    WALKOVER
    AWARDED_RESULT
    MATCH_FORFEIT
    ABANDONMENT_RULING
    MATCH_VOIDED
    MATCH_REPLAY
    RESULT_OVERTURNED
    SCORE_CORRECTION
    TEAM_DISQUALIFICATION
    TEAM_REINSTATEMENT
    MATCH_CANCELLATION
    MATCH_CONTINUATION
    MATCH_TERMINATION
    POINTS_DEDUCTION
    ADMINISTRATIVE_WIN
    ADMINISTRATIVE_DRAW
    DISCIPLINARY_SANCTION
    APPEAL_DECISION
    OTHER
    UNKNOWN

#### Status previstos

    PROVISIONAL
    ANNOUNCED
    UNDER_APPEAL
    SUSPENDED
    CONFIRMED
    OVERTURNED
    SUPERSEDED
    FINAL
    CANCELLED
    UNKNOWN

#### Resultado observado e resultado concedido

A arquitetura deverá distinguir:

    resultado observado em campo

    resultado canônico vigente

    resultado concedido administrativamente

Exemplo:

    resultado observado:
        1 x 1

    decisão administrativa:
        3 x 0

O placar observado deverá permanecer preservado.

O placar vigente poderá ser atualizado conforme a decisão final.

#### Walkover

Uma decisão por walkover deverá indicar:

    decision_type = WALKOVER
    awarded_winner_team_id preenchido
    awarded_home_score e awarded_away_score quando definidos
    affects_result = true

Os participantes deverão ser atualizados de forma coerente.

#### Repetição de partida

Quando:

    decision_type = MATCH_REPLAY
    requires_replay = true

a partida original não deverá ser apagada.

Uma nova partida poderá ser criada e relacionada futuramente por:

    MatchRelation
    ├── source_match_id
    ├── target_match_id
    ├── relation_type
    └── decision_id

Tipos possíveis:

    REPLAY_OF
    CONTINUATION_OF
    REPLACEMENT_FOR
    CORRECTION_OF

#### Recursos

Uma decisão poderá sofrer recurso.

Nesse caso:

    decision_status = UNDER_APPEAL

A decisão original deverá permanecer.

Uma nova decisão poderá substituir a anterior utilizando relação futura ou
campo de revisão.

#### Compatibilidade com Match

Quando a decisão for final e afetar o resultado:

    Match.result_source poderá indicar decisão administrativa

    Match.winner_team_id deverá refletir o resultado vigente

    Match.home_score e Match.away_score deverão seguir a estratégia definida
    para placar canônico

Os dados observados em campo deverão permanecer acessíveis em estruturas de
histórico ou observação.

#### Regras de integridade

- a decisão deverá pertencer a uma partida;
- equipes relacionadas deverão participar ou possuir relação administrativa
  válida;
- placares concedidos deverão ser maiores ou iguais a zero;
- vencedor concedido deverá ser compatível com o placar, salvo regra específica;
- decisão não poderá ser final e provisória simultaneamente;
- decisão anulada não deverá continuar aplicada;
- recursos deverão preservar decisões anteriores;
- referências oficiais deverão ser preservadas;
- decisões não deverão ser removidas fisicamente.

#### Índices recomendados para MatchDecision

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_decision_match_id` | `match_id` | Buscar decisões da partida. |
| `ix_match_decision_type` | `decision_type` | Filtrar por tipo. |
| `ix_match_decision_status` | `decision_status` | Filtrar por status. |
| `ix_match_decision_benefited_team` | `benefited_team_id` | Buscar decisões favoráveis. |
| `ix_match_decision_penalized_team` | `penalized_team_id` | Buscar penalizações. |
| `ix_match_decision_decided_at` | `decided_at` | Ordenar decisões. |

---

### 8.14 MatchRevision

A entidade `MatchRevision` representa uma revisão, correção, reconciliação ou
nova versão do estado canônico da partida.

Ela deverá permitir rastrear alterações importantes realizadas após a primeira
ingestão ou após o encerramento.

#### Responsabilidades

A entidade `MatchRevision` será responsável por:

- relacionar revisão à partida;
- indicar tipo;
- indicar origem;
- indicar motivo;
- registrar versão anterior;
- registrar nova versão;
- indicar campos afetados;
- registrar resumo da alteração;
- relacionar provider;
- relacionar decisão;
- relacionar alteração de calendário;
- indicar revisão automática ou manual;
- indicar aprovação;
- indicar aplicação;
- preservar auditoria;
- apoiar rollback lógico;
- apoiar reconciliação entre providers.

#### Campos principais

    id
    match_id
    previous_revision_id
    match_decision_id
    schedule_change_id
    revision_type
    revision_status
    previous_version_number
    new_version_number
    changed_fields
    change_summary
    reason
    reviewed_by
    reviewed_at
    applied_at
    is_automatic
    is_manual
    is_approved
    is_applied
    source_provider
    confidence_score
    created_at
    updated_at

#### Tipos de revisão previstos

    PROVIDER_CORRECTION
    CANONICAL_RECONCILIATION
    SCORE_CORRECTION
    STATUS_CORRECTION
    PARTICIPANT_CORRECTION
    VENUE_CORRECTION
    SCHEDULE_CORRECTION
    OFFICIAL_CORRECTION
    LINEUP_CORRECTION
    EVENT_CORRECTION
    STATISTIC_CORRECTION
    ADMINISTRATIVE_DECISION
    DUPLICATE_MERGE
    DUPLICATE_SPLIT
    MANUAL_REVIEW
    OTHER
    UNKNOWN

#### Status previstos

    PENDING
    UNDER_REVIEW
    APPROVED
    REJECTED
    APPLIED
    REVERTED
    SUPERSEDED
    UNKNOWN

#### Campos alterados

`changed_fields` poderá ser armazenado como:

- array de strings;
- JSON estruturado;
- relação normalizada.

Uma representação futura poderá utilizar:

    MatchRevisionField
    ├── match_revision_id
    ├── field_name
    ├── previous_value
    ├── new_value
    ├── source_provider
    └── confidence_score

Campos sensíveis deverão possuir histórico legível.

#### Versão da partida

Cada aplicação de revisão relevante poderá incrementar uma versão lógica.

Exemplo:

    previous_version_number = 4
    new_version_number = 5

O número de versão não deverá substituir os timestamps e a proveniência.

#### Revisão automática

Uma revisão poderá ser automática quando:

- provider de maior prioridade corrigir valor;
- múltiplas fontes convergirem;
- regra determinística resolver conflito;
- evento anulado exigir correção de placar;
- horário oficial substituir horário provisório.

#### Revisão manual

Uma revisão manual deverá registrar:

    reviewed_by
    reviewed_at
    reason

A identidade do revisor deverá ser tratada conforme a arquitetura de usuários e
auditoria.

#### Correção pós-partida

Estatísticas, eventos, cartões e placares poderão ser corrigidos após o
encerramento.

A revisão deverá permitir entender:

- qual valor existia;
- qual valor foi aplicado;
- qual fonte motivou a alteração;
- quando a mudança ocorreu;
- se houve aprovação manual;
- quais entidades dependentes foram recalculadas.

#### Reprocessamento

Uma revisão poderá exigir reprocessamento de:

- estatísticas agregadas;
- probabilidades;
- modelos;
- mercados;
- recomendações;
- classificação;
- histórico de equipes;
- métricas de jogadores.

O sistema deverá registrar a necessidade de reprocessamento em mecanismo
operacional futuro.

#### Regras de integridade

- a revisão deverá pertencer a uma partida;
- números de versão deverão ser maiores que zero;
- nova versão deverá ser superior à anterior;
- revisão aplicada deverá possuir `applied_at`;
- revisão manual deverá possuir responsável quando aplicável;
- uma revisão não poderá referenciar a si mesma;
- revisões rejeitadas não deverão alterar o estado canônico;
- revisões aplicadas não deverão ser removidas;
- alterações deverão ser auditáveis.

#### Índices recomendados para MatchRevision

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_match_revision_match_id` | `match_id` | Buscar revisões da partida. |
| `ix_match_revision_type` | `revision_type` | Filtrar por tipo. |
| `ix_match_revision_status` | `revision_status` | Filtrar revisões pendentes. |
| `ix_match_revision_reviewed_at` | `reviewed_at` | Ordenar revisões. |
| `ix_match_revision_match_version` | `match_id, new_version_number` | Consultar versões. |

---

### 8.15 Tie

A entidade `Tie` representa um confronto competitivo composto por uma ou mais
partidas entre participantes.

Ela será especialmente importante para:

- fases eliminatórias;
- confrontos de ida e volta;
- séries;
- playoffs;
- repescagens;
- replays;
- confrontos com placar agregado.

A separação será:

    Match
        uma partida individual

    Tie
        confronto esportivo que poderá conter uma ou mais partidas

#### Responsabilidades

A entidade `Tie` será responsável por:

- relacionar confronto à competição;
- relacionar confronto à temporada;
- relacionar confronto à fase;
- relacionar confronto à rodada;
- identificar participantes;
- indicar formato;
- indicar quantidade de partidas;
- indicar status;
- armazenar placar agregado;
- armazenar vencedor;
- armazenar critério de desempate;
- indicar classificação;
- relacionar partidas;
- representar participantes ainda indefinidos;
- apoiar chaves eliminatórias;
- apoiar avanço de fase;
- apoiar mercados de classificação;
- preservar decisões administrativas.

#### Campos principais

    id
    competition_id
    season_id
    stage_id
    round_id
    tie_type
    tie_status
    participant_1_team_id
    participant_2_team_id
    participant_1_placeholder
    participant_2_placeholder
    participant_1_aggregate_score
    participant_2_aggregate_score
    participant_1_penalty_score
    participant_2_penalty_score
    winner_team_id
    advancing_team_id
    leg_count
    completed_leg_count
    tiebreak_method
    scheduled_start_at
    completed_at
    is_neutral
    is_decided
    is_administrative
    source_provider
    confidence_score
    created_at
    updated_at

#### Tipos de confronto previstos

    SINGLE_MATCH
    TWO_LEG
    MULTI_LEG
    BEST_OF_SERIES
    PLAYOFF
    REPLAY
    QUALIFIER
    ROUND_ROBIN_PAIRING
    OTHER
    UNKNOWN

#### Status previstos

    PLANNED
    PARTICIPANTS_PENDING
    SCHEDULED
    IN_PROGRESS
    SUSPENDED
    COMPLETED
    DECIDED
    CANCELLED
    VOIDED
    UNKNOWN

#### Métodos de desempate previstos

    REGULATION_SCORE
    EXTRA_TIME
    PENALTY_SHOOTOUT
    AGGREGATE_SCORE
    AWAY_GOALS
    HIGHER_SEED
    GROUP_RANKING
    REPLAY
    DRAW
    ADMINISTRATIVE_DECISION
    OTHER
    UNKNOWN

O método `AWAY_GOALS` deverá ser contextual à competição e temporada.

Ele não deverá ser aplicado apenas porque o confronto possui duas partidas.

#### Relacionamento com partidas

A relação deverá ser representada por entidade associativa:

    TieMatch
    ├── id
    ├── tie_id
    ├── match_id
    ├── leg_number
    ├── match_role
    ├── counts_for_aggregate
    ├── is_deciding_match
    ├── created_at
    └── updated_at

Papéis possíveis:

    FIRST_LEG
    SECOND_LEG
    THIRD_LEG
    DECIDING_MATCH
    REPLAY
    CONTINUATION
    OTHER

#### Participantes indefinidos

Um confronto poderá ser criado antes da definição das equipes.

Exemplo:

    participant_1_placeholder =
        vencedor do confronto A

    participant_2_placeholder =
        segundo colocado do grupo B

Equipes artificiais não deverão ser criadas.

Quando os participantes forem definidos, os campos de equipe deverão ser
preenchidos.

#### Placar agregado

O placar agregado deverá refletir apenas partidas válidas que contem para o
confronto.

Uma partida anulada, repetida ou desconsiderada não deverá permanecer no cálculo.

`counts_for_aggregate` deverá permitir controlar essa condição.

#### Disputa por pênaltis

O placar da disputa por pênaltis deverá permanecer separado do placar agregado.

Exemplo:

    agregado = 2 x 2
    pênaltis = 5 x 4

O vencedor deverá ser compatível com a disputa.

#### Vencedor e classificado

`winner_team_id` deverá representar o vencedor do confronto.

`advancing_team_id` deverá representar a equipe que avançou.

Normalmente serão iguais.

Entretanto, decisões administrativas poderão criar exceções.

#### Confronto de jogo único

Em `SINGLE_MATCH`, o confronto poderá possuir uma única partida.

A entidade ainda será útil para:

- relacionar chaves;
- indicar avanço;
- representar participantes ainda indefinidos;
- mercados de classificação;
- histórico da fase.

#### Replays

Um replay não deverá substituir a partida original.

O confronto poderá relacionar ambas:

    partida original
    replay

A partida original poderá não contar para o placar agregado, conforme o
regulamento.

#### Regras de integridade

- competição, temporada e fase deverão ser compatíveis;
- participantes não deverão ser iguais;
- placares deverão ser maiores ou iguais a zero;
- `leg_count` deverá ser maior que zero;
- `completed_leg_count` deverá ser maior ou igual a zero;
- partidas relacionadas deverão pertencer ao mesmo contexto competitivo;
- vencedor deverá ser um participante ou possuir justificativa administrativa;
- apenas partidas válidas deverão contar para o agregado;
- confrontos históricos não deverão ser removidos;
- alterações administrativas deverão ser auditáveis.

#### Índices recomendados para Tie

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_tie_competition_id` | `competition_id` | Buscar confrontos da competição. |
| `ix_tie_season_id` | `season_id` | Buscar confrontos da temporada. |
| `ix_tie_stage_id` | `stage_id` | Buscar confrontos da fase. |
| `ix_tie_status` | `tie_status` | Filtrar por status. |
| `ix_tie_participant_1` | `participant_1_team_id` | Buscar confrontos da equipe. |
| `ix_tie_participant_2` | `participant_2_team_id` | Buscar confrontos da equipe. |
| `ix_tie_winner` | `winner_team_id` | Buscar vencedores. |
| `ix_tie_stage_status` | `stage_id, tie_status` | Buscar confrontos da fase. |

#### Índices recomendados para TieMatch

| Índice sugerido | Colunas | Finalidade |
|-----------------|---------|------------|
| `ix_tie_match_tie_id` | `tie_id` | Buscar partidas do confronto. |
| `ix_tie_match_match_id` | `match_id` | Buscar confronto da partida. |
| `ix_tie_match_leg` | `tie_id, leg_number` | Ordenar partidas. |

Deverá existir unicidade sobre:

    tie_id
    leg_number

Também deverá existir unicidade sobre:

    tie_id
    match_id

---

### 8.16 Consolidação de partidas e calendário esportivo

A modelagem de partidas deverá ser implementada como um agregado canônico
composto por entidades com responsabilidades distintas.

A entidade `Match` será a raiz principal do agregado.

Estrutura consolidada:

    Match
    ├── MatchParticipant
    ├── MatchVenue
    ├── MatchOfficial
    ├── MatchPeriod
    ├── MatchSquad
    ├── Lineup
    │   └── LineupEntry
    ├── MatchEvent
    ├── MatchStatistic
    ├── MatchInterruption
    ├── MatchScheduleChange
    ├── MatchDecision
    ├── MatchRevision
    └── TieMatch
        └── Tie

#### Responsabilidade de cada entidade

`Match` deverá representar:

- identidade da partida;
- competição;
- temporada;
- fase;
- rodada;
- participantes principais;
- data e horário atuais;
- status;
- placar resumido;
- vencedor;
- estado canônico atual.

`MatchParticipant` deverá representar:

- equipe contextual;
- papel;
- ordem;
- placar por participante;
- resultado;
- classificação;
- eliminação;
- avanço;
- walkover;
- participante indefinido.

`MatchVenue` deverá representar:

- contexto físico;
- estádio;
- cidade;
- campo neutro;
- capacidade;
- público;
- gramado;
- clima;
- histórico de local.

`MatchOfficial` deverá representar:

- nomeação;
- função;
- participação efetiva;
- substituições;
- equipe de arbitragem;
- oficiais técnicos.

`MatchPeriod` deverá representar:

- estrutura temporal;
- primeiro e segundo tempos;
- prorrogação;
- pênaltis;
- acréscimos;
- início e fim reais.

`MatchSquad` deverá representar:

- lista de relacionados;
- lista provisória;
- lista oficial;
- grupo disponível para a partida.

`Lineup` deverá representar:

- escalação;
- formação;
- versão;
- estado oficial ou provável.

`LineupEntry` deverá representar:

- titular;
- reserva;
- posição;
- número;
- capitão;
- entrada;
- saída;
- participação individual.

`MatchEvent` deverá representar:

- gols;
- cartões;
- substituições;
- faltas;
- revisões;
- acontecimentos da linha do tempo.

`MatchStatistic` deverá representar:

- métricas por partida;
- métricas por equipe;
- métricas por jogador;
- métricas por período;
- valores observados e calculados.

`MatchInterruption` deverá representar:

- paralisações;
- suspensões;
- causas;
- retomadas;
- duração da interrupção.

`MatchScheduleChange` deverá representar:

- mudanças de data;
- mudanças de horário;
- adiamentos;
- alterações de local;
- histórico de calendário.

`MatchDecision` deverá representar:

- decisões administrativas;
- walkovers;
- resultados concedidos;
- anulações;
- replays;
- desclassificações.

`MatchRevision` deverá representar:

- correções;
- reconciliações;
- versões;
- alterações pós-partida;
- auditoria do estado canônico.

`Tie` deverá representar:

- confrontos;
- ida e volta;
- placar agregado;
- critérios de desempate;
- classificação para outra fase.

#### Fonte de verdade

A fonte de verdade deverá ser dividida por responsabilidade.

`Match` será a fonte do estado resumido atual.

As entidades contextuais serão as fontes detalhadas.

Exemplos:

    participante atual:
        MatchParticipant

    estádio atual:
        MatchVenue vigente e confirmado

    equipe de arbitragem:
        MatchOfficial vigente

    linha do tempo:
        MatchEvent

    alteração de calendário:
        MatchScheduleChange

    decisão administrativa:
        MatchDecision

    histórico de correção:
        MatchRevision

Campos resumidos em `Match` deverão ser sincronizados por serviços de domínio.

#### Redundância controlada

A arquitetura aceitará redundância controlada em campos de leitura frequente.

Exemplos:

    Match.home_team_id
    Match.away_team_id
    Match.stadium_id
    Match.home_score
    Match.away_score
    Match.winner_team_id

Esses campos deverão ser consistentes com entidades detalhadas.

A redundância não poderá resultar em múltiplas fontes independentes de escrita.

#### Fluxo de ingestão

O fluxo esperado será:

    payload do provider
        ↓
    armazenamento bruto
        ↓
    collector
        ↓
    normalização
        ↓
    resolução de identidade
        ↓
    resolução da partida
        ↓
    resolução das entidades contextuais
        ↓
    fusão
        ↓
    validação do agregado
        ↓
    persistência canônica
        ↓
    revisão e auditoria
        ↓
    publicação para estatísticas e IA

Nenhum payload de provider deverá ser gravado diretamente nas tabelas
canônicas.

#### Ordem de resolução

A ordem recomendada será:

    Country
        ↓
    Region
        ↓
    City
        ↓
    Stadium
        ↓
    Competition
        ↓
    Season
        ↓
    Stage
        ↓
    Round
        ↓
    Team
        ↓
    Person
        ↓
    Player
        ↓
    Referee
        ↓
    Match
        ↓
    MatchParticipant
        ↓
    MatchVenue
        ↓
    MatchOfficial
        ↓
    MatchPeriod
        ↓
    MatchSquad
        ↓
    Lineup
        ↓
    LineupEntry
        ↓
    MatchEvent
        ↓
    MatchStatistic
        ↓
    entidades administrativas e de revisão

A ordem poderá variar parcialmente, mas dependências obrigatórias deverão ser
respeitadas.

#### Estado atual e histórico

Entidades com alterações temporais deverão preservar histórico.

Incluem:

- `MatchVenue`;
- `MatchOfficial`;
- `Lineup`;
- `MatchScheduleChange`;
- `MatchDecision`;
- `MatchRevision`.

O estado atual não deverá apagar o estado anterior.

Campos como:

    valid_from
    valid_until
    status
    version_number

deverão apoiar reconstrução histórica.

#### Participantes indefinidos

Participantes, oficiais, estádios e pessoas ainda não resolvidos não deverão
gerar entidades artificiais.

Deverão ser utilizados:

    campos nulos
    placeholders
    status pendentes
    observações de provider
    resolução posterior

Exemplos proibidos como entidades canônicas:

    Team = TBD
    Team = Winner Match 10
    Person = Unknown Referee
    Stadium = To Be Confirmed

#### Valores desconhecidos

Valor desconhecido não deverá ser confundido com zero, falso ou vazio.

Exemplos:

    attendance = null
        público desconhecido

    attendance = 0
        público oficialmente igual a zero

    score = null
        placar desconhecido

    score = 0
        placar conhecido igual a zero

    is_neutral = false
        confirmado que não é campo neutro

    is_neutral = null
        informação ainda desconhecida, caso a implementação permita tri-state

A estratégia de booleanos deverá considerar quando `null` for necessário.

#### Proveniência

Todas as entidades críticas deverão integrar futuramente:

    ExternalEntityMapping
    EntitySource
    ProviderObservation
    CanonicalFieldValue
    ConflictRecord

A proveniência deverá permitir responder:

- qual provider informou;
- qual valor foi recebido;
- quando foi recebido;
- qual normalizador foi utilizado;
- qual entidade externa originou o dado;
- qual valor canônico foi escolhido;
- qual regra escolheu o valor;
- quais fontes divergiram;
- qual confiança foi atribuída;
- quando houve revisão.

#### Confiança

`confidence_score` deverá representar confiança na identidade ou no valor
canônico.

Ele não deverá representar:

- probabilidade de vitória;
- qualidade do time;
- desempenho do jogador;
- certeza de aposta;
- força estatística do modelo.

As escalas deverão ser documentadas de forma uniforme.

#### Conflitos

Conflitos não deverão ser resolvidos silenciosamente.

Exemplos críticos:

- equipes invertidas;
- horários divergentes;
- estádios divergentes;
- placares divergentes;
- eventos duplicados;
- árbitros diferentes;
- cartões corrigidos;
- gols anulados;
- resultados administrativos;
- partidas duplicadas;
- partidas distintas fundidas incorretamente.

Cada conflito deverá possuir:

- entidades envolvidas;
- campos divergentes;
- fontes;
- valores;
- confiança;
- prioridade;
- status de resolução;
- decisão aplicada.

#### Exclusão

Partidas e entidades contextuais não deverão ser removidas fisicamente em
situações normais.

Estados recomendados incluem:

    CANCELLED
    VOIDED
    SUPERSEDED
    REPLACED
    REJECTED
    DISPUTED
    ARCHIVED

Exclusão física deverá ser reservada para:

- dados de teste;
- registros inválidos sem dependências;
- exigências legais;
- manutenção controlada;
- duplicidades ainda não publicadas.

#### Transações

Atualizações críticas deverão ocorrer dentro de transações.

Exemplo de atualização de placar:

    criar ou atualizar evento
        ↓
    validar sequência
        ↓
    atualizar MatchParticipant
        ↓
    atualizar Match
        ↓
    atualizar estatísticas derivadas
        ↓
    criar MatchRevision
        ↓
    confirmar transação

Em caso de falha, nenhuma parte deverá permanecer parcialmente atualizada.

#### Serviços de domínio recomendados

A implementação deverá considerar serviços como:

    MatchIdentityResolver
    MatchParticipantResolver
    MatchVenueResolver
    MatchOfficialResolver
    MatchPeriodService
    LineupService
    MatchEventService
    MatchScoreService
    MatchStatisticService
    MatchScheduleService
    MatchDecisionService
    MatchRevisionService
    TieService
    MatchAggregateValidator

Esses serviços não deverão depender diretamente de formatos específicos dos
providers.

#### Eventos de domínio recomendados

Eventos internos poderão incluir:

    MatchCreated
    MatchScheduled
    MatchRescheduled
    MatchPostponed
    MatchCancelled
    MatchStarted
    MatchPeriodStarted
    MatchEventRecorded
    MatchScoreChanged
    MatchInterrupted
    MatchResumed
    MatchCompleted
    MatchResultCorrected
    MatchDecisionApplied
    MatchVenueChanged
    MatchOfficialChanged
    LineupConfirmed
    TieDecided

Esses eventos poderão alimentar:

- cache;
- notificações;
- recalculo estatístico;
- modelos;
- odds;
- alertas;
- auditoria;
- integrações.

#### Ordem inicial de implementação

A ordem recomendada para migrations será:

    1. Match
    2. MatchParticipant
    3. MatchVenue
    4. MatchOfficial
    5. MatchPeriod
    6. MatchSquad
    7. Lineup
    8. LineupEntry
    9. MatchEvent
    10. MatchStatistic
    11. MatchInterruption
    12. MatchScheduleChange
    13. MatchDecision
    14. MatchRevision
    15. Tie
    16. TieMatch

A ordem poderá ser ajustada conforme dependências reais.

#### Escopo inicial de implementação

A primeira versão não precisará implementar toda a profundidade documentada.

O núcleo mínimo recomendado será:

    Match
    MatchParticipant
    MatchVenue
    MatchOfficial
    MatchPeriod
    Lineup
    LineupEntry
    MatchEvent
    MatchStatistic

A segunda camada poderá incluir:

    MatchSquad
    MatchInterruption
    MatchScheduleChange
    MatchDecision
    MatchRevision
    Tie
    TieMatch

A documentação completa deverá permanecer como referência de evolução.

#### Critérios de conclusão da modelagem

A modelagem de partidas poderá ser considerada pronta para implementação quando:

- as responsabilidades estiverem separadas;
- os relacionamentos estiverem definidos;
- a identidade canônica estiver clara;
- o fluxo de resolução estiver documentado;
- os estados estiverem definidos;
- placeholders não criarem entidades falsas;
- eventos anulados forem preservados;
- alterações de calendário forem auditáveis;
- decisões administrativas forem separadas do resultado observado;
- confrontos agregados forem separados de partidas individuais;
- a proveniência estiver prevista;
- os índices iniciais estiverem definidos;
- as constraints não impedirem dados reais legítimos;
- o agregado possuir estratégia de validação;
- a ordem de migrations estiver estabelecida.

Com essa estrutura, o domínio de partidas estará preparado para receber dados de
múltiplos providers, preservar histórico, resolver divergências e sustentar
estatísticas, probabilidades, mercados e modelos de inteligência esportiva sem
acoplamento direto aos formatos externos.

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