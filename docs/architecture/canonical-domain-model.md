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