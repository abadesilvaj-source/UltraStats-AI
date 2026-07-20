# Tipos Canônicos do UltraStats AI

Este documento registra os Value Objects, identificadores, enums e tipos
compartilhados utilizados pelo domínio canônico.

A implementação deste catálogo ocorre durante:

```text
G5.3 — Biblioteca de Value Objects
G5.4 — Enums Canônicos
```

---

## 1. Objetivo

Os tipos canônicos deverão:

- representar conceitos relevantes do domínio;
- impedir o uso de valores primitivos sem contexto;
- centralizar validações;
- reduzir duplicação;
- tornar assinaturas mais explícitas;
- impedir a mistura acidental de identificadores;
- preservar imutabilidade;
- manter o domínio independente de providers.

---

## 2. Organização da G5.3

```text
G5.3.1 — Identificadores Canônicos
G5.3.2 — Tipos Textuais
G5.3.3 — Tipos Numéricos
G5.3.4 — Tipos Temporais e Geográficos
```

---

## 3. Identificadores canônicos

Arquivo de implementação:

```text
src/ultrastats_ai/domain/shared/identifiers.py
```

Todos os identificadores canônicos utilizam UUID.

A base da hierarquia é:

```text
ValueObject
    ↓
CanonicalId
    ↓
EntityId
    ↓
Identificador específico
```

Exemplo:

```python
team_id = TeamId.new()
match_id = MatchId.new()
```

---

## 4. Regras dos identificadores

Todo identificador canônico deverá:

- ser imutável;
- possuir um UUID válido;
- ser criado internamente pelo UltraStats AI;
- possuir igualdade baseada em tipo e valor;
- possuir representação textual;
- ser utilizável como chave de dicionário;
- ser independente de identificadores externos.

Dois identificadores com o mesmo UUID, mas de tipos diferentes, não são iguais.

Exemplo:

```python
TeamId(value=uuid_value) != MatchId(value=uuid_value)
```

---

## 5. Identificadores de Geography

```text
CountryId
RegionId
CityId
VenueId
```

---

## 6. Identificadores de Competition

```text
CompetitionId
SeasonId
StageId
RoundId
```

---

## 7. Identificadores de People e Team

```text
PersonId
PlayerId
CoachId
RefereeId
TeamId
TeamMembershipId
SquadRegistrationId
```

---

## 8. Identificadores de Match

```text
MatchId
TieId
MatchEventId
MatchRevisionId
```

---

## 9. Identificadores de providers e identidade

```text
ProviderId
ExternalIdentityId
AliasId
```

O identificador canônico de um provider não substitui os identificadores
fornecidos pelo próprio provider.

Os valores externos serão representados posteriormente por tipos específicos.

---

## 10. Identificadores de Betting

```text
BookmakerId
BettingMarketId
BettingSelectionId
OddId
BetId
```

---

## 11. Identificadores analíticos

```text
StatisticalModelId
FeatureSetId
PredictionModelId
PredictionId
RecommendationId
```

---

## 12. Identificadores de risco e banca

```text
PortfolioId
BankrollAccountId
BankrollTransactionId
```

---

## 13. Criação de identificadores

Novos identificadores deverão ser criados por:

```python
team_id = TeamId.new()
```

A reconstrução a partir de persistência poderá utilizar:

```python
team_id = TeamId.from_string(
    "5b7e2723-c8b4-4b09-b7ac-d1238807d5ee"
)
```

Também será possível construir diretamente a partir de UUID:

```python
team_id = TeamId(value=uuid_value)
```

---

## 14. Identificadores externos

Identificadores externos não deverão ser armazenados diretamente dentro de
`TeamId`, `MatchId`, `PlayerId` ou qualquer outro identificador canônico.

Exemplo proibido:

```python
team_id = TeamId.from_string(provider_team_id)
```

quando `provider_team_id` não for o UUID canônico do UltraStats AI.

O relacionamento correto será:

```text
Provider
    +
External ID
    ↓
External Identity Mapping
    ↓
Canonical ID
```

---
## 15. Infraestrutura de tipos textuais

Arquivo principal:

```text
src/ultrastats_ai/domain/shared/text_value.py
```

A infraestrutura textual compartilhada possui como base:

```text
ValueObject
    ↓
TextValue
    ↓
Tipos textuais especializados
```

A classe `TextValue` é responsável por:

- validar que o valor recebido seja uma string;
- aplicar normalização Unicode NFKC;
- remover espaços das extremidades;
- reduzir espaços internos consecutivos;
- validar comprimento mínimo;
- validar comprimento máximo;
- aplicar expressões regulares opcionais;
- permitir validações adicionais em subclasses;
- manter imutabilidade;
- fornecer representação textual;
- permitir utilização como chave de dicionário.

Exemplo:

```python
text = TextValue("  UltraStats    AI  ")

assert text.value == "UltraStats AI"
```

---

## 16. Normalização Unicode

A normalização padrão utilizada é:

```text
NFKC
```

Essa forma converte representações Unicode compatíveis para uma forma
canônica comum.

Exemplo:

```python
TextValue("ＡＢＣ").value == "ABC"
```

A normalização Unicode não deverá ser utilizada para remover acentos nem para
forçar transliteração.

Valores como:

```text
São Paulo
Málaga
Łódź
東京
```

deverão continuar preservando seus caracteres semânticos.

---

## 17. Base para nomes

Arquivo:

```text
src/ultrastats_ai/domain/shared/name.py
```

A classe `Name` representa a base compartilhada para nomes canônicos.

Regras atuais:

- comprimento mínimo de dois caracteres;
- comprimento máximo de cento e cinquenta caracteres;
- normalização de espaços;
- suporte a Unicode;
- presença obrigatória de ao menos um caractere alfanumérico;
- suporte a hífens;
- suporte a apóstrofos;
- suporte a pontos;
- suporte a números.

Exemplos válidos:

```text
São Paulo
Paris Saint-Germain
O'Connor
F.C. Porto
Schalke 04
東京
```

Exemplos inválidos:

```text
--
..
@#
```

---

## 18. Especialização dos tipos textuais

Subclasses poderão alterar regras por meio de atributos de classe:

```python
class ExampleText(TextValue):
    MIN_LENGTH = 2
    MAX_LENGTH = 50
```

Expressões regulares também poderão ser definidas:

```python
class ExampleCode(TextValue):
    PATTERN = compile_text_pattern(r"[A-Z0-9]+")
```

Validações semânticas adicionais deverão sobrescrever:

```python
def validate_specific_rules(self) -> None:
    ...
```

Esse mecanismo evita a duplicação da infraestrutura básica de validação.
---

## 19. Tipos base de nomes

A biblioteca de nomes possui a seguinte hierarquia:

```text
ValueObject
    ↓
TextValue
    ↓
Name
    ├── ProperName
    ├── DisplayName
    └── ShortName
```

Esses tipos representam categorias textuais reutilizáveis. Eles ainda não
representam diretamente entidades específicas do domínio.

---

## 20. ProperName

Arquivo:

```text
src/ultrastats_ai/domain/shared/proper_name.py
```

`ProperName` representa o nome oficial ou principal de um conceito.

Exemplos:

```text
Manchester United Football Club
Confederação Brasileira de Futebol
Associação Portuguesa de Desportos
Premier League
São Paulo
```

Regras:

- mínimo de dois caracteres;
- máximo de cento e cinquenta caracteres;
- presença de ao menos um caractere alfanumérico;
- suporte a Unicode;
- normalização de espaços;
- imutabilidade.

O tipo será utilizado como base para nomes como:

```text
CountryName
CompetitionName
TeamName
PersonName
VenueName
ProviderName
```

---

## 21. DisplayName

Arquivo:

```text
src/ultrastats_ai/domain/shared/display_name.py
```

`DisplayName` representa a forma preferencial de apresentação de um nome em
interfaces, relatórios e respostas de API.

Exemplo:

```text
Nome oficial:
Manchester United Football Club

Nome de exibição:
Manchester United
```

Regras:

- mínimo de um caractere;
- máximo de cem caracteres;
- presença de ao menos um caractere alfanumérico;
- suporte a Unicode;
- normalização de espaços;
- imutabilidade.

---

## 22. ShortName

Arquivo:

```text
src/ultrastats_ai/domain/shared/short_name.py
```

`ShortName` representa nomes utilizados em espaços reduzidos.

Exemplos:

```text
PSG
UCL
Man United
São Paulo
Brasileirão
```

Regras:

- mínimo de um caractere;
- máximo de trinta caracteres;
- presença de ao menos um caractere alfanumérico;
- suporte a Unicode;
- normalização de espaços;
- imutabilidade.

`ShortName` não obriga letras maiúsculas.

Abreviações formais e códigos serão modelados separadamente durante a etapa
G5.3.2.3.

---

## 23. Igualdade entre tipos de nomes

A igualdade dos Value Objects considera o tipo concreto e o valor normalizado.

Portanto:

```python
ProperName("São Paulo") != DisplayName("São Paulo")
```

Mesmo quando os textos armazenados forem iguais, os objetos representam
conceitos semânticos diferentes.
---

## 24. Nomes da geografia administrativa

Os nomes da geografia administrativa são especializações semânticas de
`ProperName`.

### Hierarquia de nomes geográficos

Os nomes relacionados a conceitos geográficos possuem uma base semântica
específica:

```text
ProperName
└── GeographicName
    ├── CountryName
    ├── RegionName
    ├── CityName
    └── VenueName
```

`GeographicName` concentra a identidade semântica comum dos nomes geográficos.

Atualmente ele reutiliza integralmente as regras de `ProperName`, mas oferece
um ponto de extensão para futuras regras relacionadas a:

- localidades;
- transliteração;
- aliases geográficos;
- integrações com padrões territoriais;
- normalização internacional.

`VenueName` representa o nome canônico de um local esportivo, incluindo:

- estádios;
- arenas;
- ginásios;
- centros esportivos;
- campos;
- complexos esportivos.

Exemplo:

```python
from ultrastats_ai.domain.shared import VenueName

venue = VenueName("Estádio do Maracanã")
```

`VenueName` é semanticamente diferente de `CityName`, mesmo quando ambos
possuem o mesmo valor textual.
---

### Nomes de competições

`CompetitionName` representa o nome canônico de uma competição esportiva.

Hierarquia:

```text
ProperName
└── CompetitionName
```

Exemplos:

```python
from ultrastats_ai.domain.shared import CompetitionName

premier_league = CompetitionName("Premier League")
copa_do_brasil = CompetitionName("Copa do Brasil")
champions_league = CompetitionName("UEFA Champions League")
```

`CompetitionName` representa somente o nome.

Características como formato, nível territorial, gênero, categoria etária ou
organizador não deverão ser codificadas por subclasses do nome.

Essas características serão representadas futuramente por propriedades
específicas da entidade ou do agregado de competição.

Exemplos:

```text
CompetitionFormat
CompetitionLevel
CompetitionGender
CompetitionAgeCategory
```

Consequentemente, não serão criadas classes como:

```text
LeagueName
CupName
TournamentName
```

a menos que surjam regras textuais realmente diferentes para esses conceitos.

Estrutura física:

```text
domain/shared/names/competitions/
├── __init__.py
└── competition_name.py
```

O caminho público recomendado é:

```python
from ultrastats_ai.domain.shared import CompetitionName
```
---

### Hierarquia atual da biblioteca de nomes

```text
ProperName
├── GeographicName
│   ├── CountryName
│   ├── RegionName
│   ├── CityName
│   └── VenueName
├── CompetitionName
├── PersonName
└── OrganizationName
```

Essa hierarquia organiza os tipos de nomes pelo conceito que representam,
sem misturar o nome com papéis, formatos ou categorias das entidades.
---

### Nomes de pessoas

`PersonName` representa o nome canônico de uma pessoa.

Hierarquia:

```text
ProperName
└── PersonName
```

Exemplos:

```python
from ultrastats_ai.domain.shared import PersonName

coach = PersonName("Carlo Ancelotti")
former_player = PersonName("Xabi Alonso")
single_name = PersonName("Pelé")
```

`PersonName` representa exclusivamente o nome da pessoa.

Papéis como jogador, treinador, árbitro, dirigente ou agente não fazem parte
do nome e não serão representados por subclasses como:

```text
PlayerName
CoachName
RefereeName
```

Uma mesma pessoa pode exercer mais de um papel ao longo da carreira ou até
simultaneamente. O nome permanece o mesmo independentemente do papel.

Exemplo conceitual futuro:

```python
person = Person(
    name=PersonName("Xabi Alonso"),
    roles={
        PersonRole.PLAYER,
        PersonRole.COACH,
    },
)
```

A modelagem de papéis será realizada nas fases de entidades, agregados e regras
de domínio.

`PersonName` aceita nomes compostos, nomes de apenas uma palavra, caracteres
Unicode, hífens e apóstrofos, desde que respeitadas as regras gerais herdadas
de `ProperName`.

Estrutura física:

```text
domain/shared/names/people/
├── __init__.py
└── person_name.py
```

O caminho público recomendado é:

```python
from ultrastats_ai.domain.shared import PersonName
```
---
### Nomes de organizações

`OrganizationName` representa o nome canônico de uma organização.

Hierarquia:

```text
ProperName
└── OrganizationName
```

Exemplos:

```python
from ultrastats_ai.domain.shared import OrganizationName

club = OrganizationName("São Paulo Futebol Clube")
federation = OrganizationName("Confederação Brasileira de Futebol")
international_body = OrganizationName("UEFA")
company = OrganizationName("Red Bull GmbH")
```

`OrganizationName` representa exclusivamente o nome da organização.

O tipo da organização não faz parte do nome e será representado futuramente
por um conceito separado.

Exemplo conceitual:

```python
organization = Organization(
    name=OrganizationName("Confederação Brasileira de Futebol"),
    organization_type=OrganizationType.FEDERATION,
)
```

Não serão criadas subclasses como:

```text
ClubName
FederationName
AssociationName
CompanyName
```

Essas classificações representam a natureza da organização, não uma regra
textual diferente para o nome.

Estrutura física:

```text
domain/shared/names/organizations/
├── __init__.py
└── organization_name.py
```

O caminho público recomendado é:

```python
from ultrastats_ai.domain.shared import OrganizationName
```
---
## Códigos canônicos

`CodeValue` representa a base dos códigos internos e estáveis utilizados pelo
domínio do UltraStats AI.

Hierarquia inicial:

```text
TextValue
└── CodeValue
```

Exemplos:

```python
from ultrastats_ai.domain.shared import CodeValue

country = CodeValue("BRA")
competition = CodeValue("BR_SERIE_A")
organization = CodeValue("UEFA")
```

### Normalização

Os códigos são:

- convertidos para letras maiúsculas;
- limpos de espaços no início e no final;
- limitados a 64 caracteres;
- restritos a caracteres ASCII.

Caracteres permitidos:

```text
A-Z
0-9
.
_
-
```

Exemplo:

```python
CodeValue("  br-serie-a  ")
```

Resultado:

```text
BR-SERIE-A
```

Espaços internos e caracteres especiais não permitidos geram erro.

### Código canônico e identificador externo

`CodeValue` não representa identificadores fornecidos por APIs externas.

Código canônico interno:

```text
BR_SERIE_A
```

Identificadores externos:

```text
API_FOOTBALL = 71
SPORTMONKS = 384
OPTA = COMP-1234
```

Os identificadores externos serão modelados separadamente em
`G5.3.2.5 — External Identifiers`.

Estrutura física:

```text
domain/shared/codes/
├── __init__.py
└── code_value.py
```

O caminho público recomendado é:

```python
from ultrastats_ai.domain.shared import CodeValue
```
---
## 25. CountryName

Arquivo:

```text
src/ultrastats_ai/domain/shared/country_name.py
```

`CountryName` representa o nome oficial de um país.

Exemplos:

```text
Brazil
United Kingdom
Côte d'Ivoire
日本
```

O tipo reutiliza as regras de `ProperName`:

- mínimo de dois caracteres;
- máximo de cento e cinquenta caracteres;
- presença de caractere alfanumérico;
- normalização Unicode;
- normalização de espaços;
- imutabilidade.

---

## 26. RegionName

Arquivo:

```text
src/ultrastats_ai/domain/shared/region_name.py
```

`RegionName` representa o nome oficial de uma divisão administrativa.

Exemplos:

```text
São Paulo
California
Andalucía
New South Wales
```

Uma região poderá representar estados, províncias, departamentos, comunidades
autônomas ou divisões administrativas equivalentes.

---

## 27. CityName

Arquivo:

```text
src/ultrastats_ai/domain/shared/city_name.py
```

`CityName` representa o nome oficial de uma cidade ou localidade urbana.

Exemplos:

```text
Araraquara
Manchester
Buenos Aires
Łódź
東京
```

O tipo preserva caracteres Unicode e não aplica transliteração automática.

---

## 28. Diferenciação semântica

Mesmo quando os valores textuais forem iguais, tipos geográficos diferentes
não serão considerados iguais.

Exemplo:

```python
CountryName("São Paulo") != RegionName("São Paulo")
RegionName("São Paulo") != CityName("São Paulo")
```

Essa diferenciação impede a utilização acidental de um nome de cidade em um
campo destinado a países ou regiões.
---
## 29. Organização física da biblioteca de nomes

A biblioteca de nomes canônicos está organizada em subpacotes semânticos.

Estrutura atual:

```text
domain/shared/
├── names/
│   ├── __init__.py
│   │
│   ├── base/
│   │   ├── __init__.py
│   │   ├── name.py
│   │   ├── proper_name.py
│   │   ├── display_name.py
│   │   └── short_name.py
│   │
│   └── geography/
│       ├── __init__.py
│       ├── country_name.py
│       ├── region_name.py
│       └── city_name.py
│
├── text_value.py
├── identifiers.py
└── ...
```

A infraestrutura textual geral permanece diretamente em `shared`.

`TextValue` não pertence exclusivamente à biblioteca de nomes, pois será
reutilizado por:

- códigos;
- slugs;
- aliases;
- identificadores externos;
- outros tipos textuais.

---

## 30. API pública

O caminho público recomendado é:

```python
from ultrastats_ai.domain.shared import CountryName
```

Também são suportados os imports pelos pacotes especializados:

```python
from ultrastats_ai.domain.shared.names import CountryName
```

```python
from ultrastats_ai.domain.shared.names.geography import CountryName
```

A API pública principal funciona como fachada sobre a estrutura interna.

Consumidores externos não deverão depender desnecessariamente da organização
interna dos arquivos.

---

## 31. Compatibilidade com caminhos históricos

Os módulos históricos permanecem temporariamente disponíveis:

```python
from ultrastats_ai.domain.shared.country_name import CountryName
```

Esses arquivos não possuem implementações duplicadas.

Eles apenas reexportam as classes canônicas localizadas em:

```text
domain/shared/names/
```

Consequentemente:

```python
from ultrastats_ai.domain.shared import CountryName as PublicCountryName
from ultrastats_ai.domain.shared.country_name import (
    CountryName as CompatibilityCountryName,
)
from ultrastats_ai.domain.shared.names import (
    CountryName as CanonicalCountryName,
)

assert PublicCountryName is CompatibilityCountryName
assert PublicCountryName is CanonicalCountryName
```

Essa estratégia preserva compatibilidade sem manter classes duplicadas.

---

## 32. Regras para novos tipos de nomes

Novos tipos de nomes deverão ser criados dentro do subpacote semântico
correspondente.

Exemplos planejados:

```text
names/
├── competitions/
├── people/
├── organizations/
└── analytics/
```

Depois da implementação, os tipos deverão ser reexportados por:

```text
names/<subpacote>/__init__.py
names/__init__.py
shared/__init__.py
```

A API pública recomendada continuará sendo:

```python
from ultrastats_ai.domain.shared import TipoDeNome
```
## 33. Estado atual

```text
G5.3.2.2.2.1 — Geografia Administrativa
CONCLUÍDO

G5.3.2.2.2.2 — Reorganização da Biblioteca de Nomes
CONCLUÍDO

G5.3.2.2.2.3 — GeographicName e VenueName
CONCLUÍDO

G5.3.2.2.3 — CompetitionName
CONCLUÍDO

G5.3.2.2.4 — PersonName
CONCLUÍDO

G5.3.2.2.5 — OrganizationName
CONCLUÍDO

G5.3.2.3.1 — CodeValue
CONCLUÍDO

G5.3.2.3.2 — CountryCode
PRÓXIMA ETAPA
```