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