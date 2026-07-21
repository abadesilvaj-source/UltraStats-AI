# Tipos Canônicos do UltraStats AI

O presente documento define a biblioteca oficial de tipos canônicos utilizada pelo
UltraStats AI.

Os tipos descritos neste catálogo representam conceitos fundamentais do domínio
e constituem a base sobre a qual entidades, agregados, serviços de domínio e
demais componentes da aplicação são construídos.

Este documento possui caráter arquitetural e normativo.

Seu objetivo não é descrever detalhes de implementação, mas estabelecer a
estrutura conceitual da biblioteca de tipos compartilhados, suas
responsabilidades, suas relações e as regras que deverão ser preservadas durante
a evolução do projeto.

---

# 1. Objetivo

A biblioteca de tipos canônicos tem como finalidade eliminar o uso indiscriminado
de tipos primitivos (`str`, `int`, `float`, `UUID`, entre outros) na camada de
domínio.

Cada conceito relevante do negócio deve possuir um tipo que expresse
explicitamente seu significado.

Essa abordagem reduz ambiguidades, melhora a legibilidade do código, centraliza
validações e aumenta a segurança das operações realizadas pelo domínio.

Como consequência, assinaturas de métodos tornam-se mais expressivas e erros de
utilização de valores incompatíveis passam a ser identificados durante o
desenvolvimento, em vez de somente em tempo de execução.

---

# 2. Filosofia da Biblioteca

A biblioteca de tipos canônicos segue os princípios do Domain-Driven Design
(DDD), utilizando predominantemente Value Objects para representar conceitos que
não possuem identidade própria.

Todo tipo canônico deverá representar um conceito específico do domínio e nunca
apenas um formato de armazenamento.

O foco da biblioteca não está na tecnologia utilizada, mas no significado do
valor representado.

Por esse motivo, dois objetos que contenham exatamente o mesmo valor textual
podem representar conceitos completamente diferentes.

Exemplo:

```python
CountryName("Brasil")
CompetitionName("Brasil")
```

Embora ambos armazenem o mesmo texto, representam conceitos distintos do domínio
e, portanto, não devem ser considerados equivalentes.

Da mesma forma:

```python
CountryCode("BRA")
CompetitionCode("BRA")
```

Mesmo compartilhando o mesmo valor, representam códigos semanticamente
diferentes.

O domínio diferencia conceitos, e não apenas valores.

---

# 3. Princípios Gerais

Toda a biblioteca de tipos canônicos deverá respeitar os seguintes princípios.

## 3.1 Independência do domínio

Os tipos compartilhados não poderão depender de:

- frameworks;
- banco de dados;
- ORM;
- APIs externas;
- protocolos de comunicação;
- interfaces gráficas;
- bibliotecas específicas de infraestrutura.

O domínio deve permanecer completamente independente da camada de infraestrutura.

---

## 3.2 Imutabilidade

Os tipos canônicos deverão ser imutáveis.

Após sua criação, um objeto nunca poderá alterar seu estado interno.

Caso seja necessário representar outro valor, uma nova instância deverá ser
criada.

Essa característica simplifica comparações, evita efeitos colaterais e facilita
o compartilhamento seguro entre diferentes partes da aplicação.

---

## 3.3 Igualdade semântica

A igualdade considera simultaneamente:

- o tipo concreto;
- o valor armazenado.

Consequentemente:

```python
CountryName("Brasil") != CompetitionName("Brasil")
```

Da mesma forma:

```python
CountryCode("BRA") != CompetitionCode("BRA")
```

Mesmo quando os valores internos forem iguais, os conceitos continuam sendo
diferentes.

---

## 3.4 Validação centralizada

Cada tipo é responsável por validar seus próprios dados.

O restante da aplicação não deverá repetir regras de validação já implementadas
pela biblioteca.

Essa centralização evita inconsistências e garante comportamento uniforme em
todo o sistema.

---

## 3.5 Especialização progressiva

Tipos especializados deverão reutilizar regras das classes-base sempre que
possível.

Uma nova especialização somente deverá ser criada quando existir diferença
semântica ou comportamental relevante.

Diferenças meramente organizacionais não justificam novos tipos.

---

## 3.6 API pública estável

Consumidores externos deverão utilizar preferencialmente a API pública do pacote
compartilhado.

Exemplo:

```python
from ultrastats_ai.domain.shared import CountryName
```

A organização física dos arquivos poderá evoluir ao longo do projeto sem exigir
alterações no código dos consumidores.

---

# 4. Organização da Biblioteca

Atualmente a biblioteca de tipos compartilhados encontra-se organizada em quatro
grandes grupos.

```text
Tipos Canônicos

├── Identificadores
├── Tipos Textuais
├── Biblioteca de Nomes
└── Biblioteca de Códigos
```

Cada grupo possui responsabilidades próprias.

## Identificadores

Representam identidades canônicas utilizadas pelo domínio.

Exemplos:

- CountryId;
- CompetitionId;
- TeamId;
- MatchId.

---

## Tipos Textuais

Fornecem infraestrutura compartilhada para valores baseados em texto.

Exemplos:

- TextValue;
- Name;
- ProperName;
- DisplayName;
- ShortName.

---

## Biblioteca de Nomes

Contém especializações semânticas utilizadas para representar nomes de conceitos
do domínio.

Exemplos:

- CountryName;
- VenueName;
- CompetitionName;
- PersonName;
- OrganizationName.

---

## Biblioteca de Códigos

Representa códigos internos utilizados pelo domínio.

Exemplos:

- CodeValue;
- CountryCode;
- CompetitionCode;
- OrganizationCode.

---

# 5. Hierarquia Geral

A relação entre os principais tipos atualmente implementados pode ser
representada da seguinte forma.

```text
ValueObject
│
├── CanonicalId
│   └── EntityId
│       └── IDs especializados
│
└── TextValue
│    │
│    ├── Name
│    │   ├── ProperName
│    │   │
│    │   ├── DisplayName
│    │   └── ShortName
│    │
│    └── CodeValue
│    ├── SlugValue
│    └── AliasValue
│    ├── ProviderNamespace
│    └── ExternalIdentifier
│
└── ExternalIdentity
│    ├── ProviderNamespace
│    └── ExternalIdentifier
├── Temporal
│   ├── DomainDate
│   ├── UtcTimestamp
│   ├── TimeZone
│   └── TemporalInterval
│       ├── start: UtcTimestamp
│       └── end: UtcTimestamp
│
└── Geographic
    ├── Latitude
    ├── Longitude
    └── Coordinates
        ├── latitude: Latitude
        └── longitude: Longitude
```

As especializações de nomes e códigos serão apresentadas nos capítulos
seguintes.

---

# 6. Organização Física

A estrutura interna da biblioteca encontra-se organizada da seguinte maneira.

```text
domain/shared/

├── __init__.py
│
├── identifiers.py
├── text_value.py
│
├── codes/
│   ├── __init__.py
│   └── code_value.py
│
├── names/
│   ├── __init__.py
│   │
│   ├── base/
│   ├── geography/
│   ├── competitions/
│   ├── people/
│   └── organizations/
│
└── external_ids/
    ├── __init__.py
    ├── external_identifier.py
    ├── external_identity.py
    └── provider_namespace.py
```

Essa organização busca separar conceitos semanticamente relacionados sem expor
essa estrutura aos consumidores da API pública.

Mudanças internas de organização deverão preservar, sempre que possível, a
compatibilidade da interface pública do pacote.

---
# 7. Identificadores Canônicos

Os identificadores canônicos representam a identidade única e permanente dos
conceitos do domínio.

Diferentemente dos identificadores fornecidos por sistemas externos, um
identificador canônico pertence exclusivamente ao UltraStats AI e permanece
estável durante todo o ciclo de vida da entidade que representa.

A utilização de identificadores semanticamente tipados elimina ambiguidades,
impede a mistura acidental entre entidades distintas e torna explícito o
significado de cada valor utilizado pelo domínio.

---

## 7.1 Objetivos

A biblioteca de identificadores possui os seguintes objetivos:

- representar identidades canônicas do domínio;
- impedir a utilização de UUIDs sem contexto semântico;
- evitar a mistura acidental entre identificadores de entidades diferentes;
- fornecer igualdade baseada em tipo e identidade;
- permitir reconstrução segura de entidades persistidas;
- manter independência em relação a identificadores externos.

---

## 7.2 Hierarquia

Todos os identificadores seguem a hierarquia abaixo.

```text
ValueObject
│
└── CanonicalId
    │
    └── EntityId
        │
        ├── CountryId
        ├── RegionId
        ├── CityId
        ├── VenueId
        │
        ├── CompetitionId
        ├── SeasonId
        ├── StageId
        ├── RoundId
        │
        ├── PersonId
        ├── PlayerId
        ├── CoachId
        ├── RefereeId
        │
        ├── TeamId
        ├── TeamMembershipId
        ├── SquadRegistrationId
        │
        ├── MatchId
        ├── TieId
        ├── MatchEventId
        ├── MatchRevisionId
        │
        ├── BookmakerId
        ├── BettingMarketId
        ├── BettingSelectionId
        ├── OddId
        ├── BetId
        │
        ├── PredictionId
        ├── RecommendationId
        ├── StatisticalModelId
        ├── FeatureSetId
        │
        ├── PortfolioId
        ├── BankrollAccountId
        └── BankrollTransactionId
```

Essa estrutura garante que cada entidade do domínio possua um identificador
próprio e semanticamente distinto.

---

## 7.3 CanonicalId

`CanonicalId` representa a base comum para todos os identificadores
pertencentes ao domínio canônico.

Sua responsabilidade é definir o comportamento compartilhado entre todos os
tipos de identidade utilizados pelo sistema.

Todo identificador canônico deverá:

- ser imutável;
- representar exatamente uma identidade;
- utilizar UUID como representação interna;
- possuir igualdade baseada em tipo e valor;
- possuir representação textual;
- ser utilizável como chave de coleções baseadas em hash.

`CanonicalId` não deve ser utilizado diretamente pela aplicação.

Seu papel é servir como infraestrutura para identificadores especializados.

---

## 7.4 EntityId

`EntityId` representa a base para todos os identificadores de entidades do
domínio.

Enquanto `CanonicalId` define o comportamento geral, `EntityId` estabelece a
base comum utilizada pelos Aggregate Roots e pelas entidades persistentes.

Todas as especializações apresentadas neste documento derivam de `EntityId`.

---

## 7.5 Criação de Identificadores

Novas entidades deverão receber um identificador criado pelo próprio domínio.

Exemplo:

```python
team_id = TeamId.new()
```

Esse mecanismo garante que novas identidades sejam sempre válidas e produzidas
de forma uniforme.

---

## 7.6 Reconstrução

Durante operações de persistência ou carregamento de dados já existentes,
identificadores poderão ser reconstruídos a partir de sua representação
textual.

Exemplo:

```python
team_id = TeamId.from_string(
    "5b7e2723-c8b4-4b09-b7ac-d1238807d5ee"
)
```

Também poderá ser utilizada uma instância de UUID previamente validada.

A reconstrução não cria uma nova identidade.

Ela apenas restaura uma identidade já existente.

---

## 7.7 Igualdade

A igualdade entre identificadores considera simultaneamente:

- o tipo concreto;
- o UUID armazenado.

Consequentemente:

```python
TeamId(uuid_value) != MatchId(uuid_value)
```

mesmo quando ambos utilizarem exatamente o mesmo UUID.

Da mesma forma:

```python
CountryId(uuid_value) != CompetitionId(uuid_value)
```

Essa diferenciação impede erros de utilização entre conceitos distintos do
domínio.

---

## 7.8 Identidade Canônica

A identidade canônica pertence exclusivamente ao UltraStats AI.

Ela não depende:

- do banco de dados;
- do provider utilizado;
- da API de origem;
- do formato de importação;
- do identificador externo.

Mudanças em sistemas externos nunca deverão alterar a identidade canônica de
uma entidade.

---

## 7.9 Identificadores Externos

Os identificadores utilizados por APIs e provedores de dados não fazem parte da
biblioteca de identificadores canônicos.

Eles representam apenas chaves utilizadas por sistemas externos.

Exemplos:

```text
API-Football
SportMonks
Opta
StatsBomb
Football-Data
```

Esses valores serão representados futuramente por tipos específicos da
biblioteca de identificadores externos.

Essa separação evita o acoplamento do domínio ao formato de qualquer provider.

---

## 7.10 Relação entre Identidades

A relação entre uma identidade externa e uma identidade canônica pode ser
representada da seguinte forma.

```text
Provider
        │
        ▼
External Identifier
        │
        ▼
External Identity Mapping
        │
        ▼
CanonicalId
```

O domínio sempre trabalha utilizando o identificador canônico.

Os identificadores externos existem apenas para permitir integração,
sincronização e resolução de identidade entre diferentes fontes de dados.

---

## 7.11 Especializações

As especializações de `EntityId` representam conceitos próprios do domínio.

Elas não adicionam comportamento complexo.

Sua principal responsabilidade é fornecer diferenciação semântica entre os
diversos tipos de entidades.

Por esse motivo, tipos como:

- `TeamId`;
- `CompetitionId`;
- `MatchId`;
- `PlayerId`;
- `VenueId`;

possuem exatamente a mesma estrutura interna, mas representam conceitos
completamente diferentes.

Essa distinção aumenta significativamente a segurança do domínio e evita erros
causados pela utilização indiscriminada de UUIDs.

---

## 7.12 Evolução da Biblioteca

Novos identificadores deverão ser criados sempre que uma nova entidade
canônica possuir identidade própria.

Todos deverão:

- herdar de `EntityId`;
- permanecer imutáveis;
- representar exatamente um conceito do domínio;
- manter compatibilidade com a API pública da biblioteca.

A criação de identificadores genéricos reutilizados por entidades diferentes
não é permitida.

Cada conceito relevante do domínio deve possuir um tipo de identidade próprio.

# 8. Tipos Textuais

Grande parte das informações manipuladas pelo domínio é representada por valores
textuais.

Embora esses valores sejam armazenados internamente como cadeias de caracteres,
cada um possui significado próprio e regras específicas de validação.

A biblioteca de tipos textuais estabelece uma hierarquia de Value Objects que
permite reutilizar comportamentos comuns sem perder a diferenciação semântica
entre os diversos conceitos do domínio.

Todos os tipos apresentados neste capítulo são imutáveis e seguem os princípios
definidos anteriormente neste documento.

---

## 8.1 Objetivos

A biblioteca de tipos textuais possui os seguintes objetivos:

- eliminar o uso indiscriminado de `str` na camada de domínio;
- centralizar regras de validação;
- padronizar comparações;
- aumentar a expressividade das assinaturas de métodos;
- facilitar a criação de novos tipos especializados;
- manter comportamento consistente entre todos os Value Objects textuais.

---

## 8.2 Hierarquia

Os principais tipos textuais atualmente implementados seguem a estrutura abaixo.

```text
ValueObject
│
└── TextValue
    │
    ├── Name
    │   ├── ProperName
    │   ├── DisplayName
    │   └── ShortName
    │
    └── CodeValue
```

Novas especializações deverão reutilizar essa estrutura sempre que possível.

---

## 8.3 TextValue

`TextValue` representa a base para todos os Value Objects fundamentados em texto.

Sua responsabilidade não é representar um conceito específico do domínio, mas
fornecer uma infraestrutura comum para objetos que armazenam valores textuais.

Todo tipo derivado de `TextValue` herda um conjunto de comportamentos
compartilhados, como:

- armazenamento imutável;
- igualdade baseada em tipo e valor;
- representação textual;
- suporte a hashing;
- integração uniforme com o restante do domínio.

`TextValue` não deve ser utilizado diretamente para representar conceitos do
negócio.

Sempre que existir significado semântico conhecido, deverá ser criada uma
especialização apropriada.

---

## 8.4 Igualdade

A igualdade considera simultaneamente:

- o tipo concreto;
- o valor armazenado.

Exemplo:

```python
CountryName("Brasil") != OrganizationName("Brasil")
```

Mesmo compartilhando exatamente o mesmo texto, os objetos representam conceitos
diferentes.

Da mesma forma:

```python
DisplayName("São Paulo")
!=
ShortName("São Paulo")
```

O domínio diferencia conceitos, e não apenas valores.

---

## 8.5 TextValue como Infraestrutura

`TextValue` não possui conhecimento sobre o domínio esportivo.

Ele desconhece conceitos como:

- países;
- cidades;
- competições;
- pessoas;
- clubes;
- códigos;
- provedores.

Sua única responsabilidade é fornecer comportamento reutilizável para os tipos
especializados construídos sobre ele.

Essa separação permite que novas categorias de Value Objects sejam adicionadas
sem modificar a infraestrutura existente.

---

# 9. Biblioteca Base de Nomes

A biblioteca de nomes reúne todos os tipos responsáveis por representar nomes
oficiais utilizados pelo domínio.

Um nome representa a forma pela qual um conceito é identificado por pessoas.

Ele não representa códigos, identificadores ou descrições livres.

---

## 9.1 Hierarquia

A estrutura da biblioteca de nomes é apresentada abaixo.

```text
TextValue
│
└── Name
    │
    ├── ProperName
    │   ├── GeographicName
    │   │   ├── CountryName
    │   │   ├── RegionName
    │   │   ├── CityName
    │   │   └── VenueName
    │   │
    │   ├── CompetitionName
    │   ├── PersonName
    │   └── OrganizationName
    │
    ├── DisplayName
    └── ShortName
```

Essa hierarquia organiza os diferentes tipos de nomes conforme seu significado
dentro do domínio.

---

## 9.2 Name

`Name` representa a abstração comum para todos os nomes utilizados pelo domínio.

Sua responsabilidade é concentrar o comportamento compartilhado entre todas as
especializações de nomes.

Ele não representa um conceito específico.

Seu papel é fornecer uma base comum para:

- nomes próprios;
- nomes de exibição;
- nomes abreviados;
- futuras categorias de nomes.

---

## 9.3 ProperName

`ProperName` representa nomes oficiais de entidades.

Exemplos:

- países;
- cidades;
- pessoas;
- clubes;
- competições;
- estádios;
- organizações.

A principal característica de um nome próprio é identificar um conceito do
mundo real.

Ele preserva integralmente a grafia utilizada oficialmente.

---

## 9.4 DisplayName

`DisplayName` representa a forma preferencial de apresentação de um texto para o
usuário.

Sua finalidade é exclusivamente visual.

O mesmo conceito pode possuir diferentes formas de apresentação dependendo da
interface utilizada.

Exemplos:

```text
Premier League
```

```text
Premier League (ENG)
```

```text
Premier League 2025/26
```

Essas diferenças não alteram a identidade do conceito.

---

## 9.5 ShortName

`ShortName` representa uma versão reduzida de um nome.

Seu objetivo é facilitar a apresentação em interfaces com restrição de espaço.

Exemplos:

```text
Manchester United
```

↓

```text
Man. United
```

ou

```text
São Paulo Futebol Clube
```

↓

```text
São Paulo
```

A forma abreviada nunca substitui o nome oficial.

Ela representa apenas uma alternativa de apresentação.

---

## 9.6 Relação entre os Tipos de Nome

Embora todos armazenem texto, cada tipo possui responsabilidade diferente.

```text
ProperName
│
├── representa identidade nominal
│
DisplayName
│
├── representa apresentação visual
│
ShortName
│
└── representa apresentação abreviada
```

Esses conceitos não devem ser confundidos.

Um mesmo valor textual poderá existir simultaneamente em diferentes categorias.

---

## 9.7 Especialização Progressiva

Novos tipos de nome deverão ser criados apenas quando houver diferença
semântica claramente definida.

Não deverão ser criadas especializações apenas para organizar arquivos ou
categorizar entidades.

Por exemplo, faz sentido existir:

- CompetitionName;
- OrganizationName;
- PersonName.

Entretanto, não há justificativa para criar classes como:

- LeagueName;
- CupName;
- RefereeName;
- CoachName;
- ClubName.

Essas diferenças pertencem ao domínio das entidades representadas e não ao tipo
do nome.

A biblioteca deve permanecer pequena, consistente e semanticamente orientada.

---

## 9.8 Evolução da Biblioteca

A criação de novos tipos deverá obedecer à seguinte ordem de decisão.

1. O conceito já pode ser representado por um tipo existente?

Se sim, nenhuma nova classe deverá ser criada.

2. Existe diferença semântica relevante?

Se não existir, o tipo atual deverá ser reutilizado.

3. Existe comportamento próprio?

Caso a diferença seja apenas organizacional, também não deverá ser criada uma
nova especialização.

Somente quando houver diferença de significado ou comportamento será justificável
introduzir um novo tipo na biblioteca.

Essa política evita a proliferação de classes redundantes e mantém a biblioteca
coesa ao longo da evolução do projeto.

# 10. Biblioteca de Nomes

A biblioteca de nomes reúne os tipos responsáveis por representar a denominação
oficial dos principais conceitos do domínio.

Todos os tipos apresentados neste capítulo derivam, direta ou indiretamente, de
`ProperName`.

Seu objetivo é fornecer diferenciação semântica entre conceitos que, embora
compartilhem a mesma representação textual, possuem significados distintos.

---

## 10.1 Hierarquia

A organização atual da biblioteca é apresentada abaixo.

```text
ProperName
│
├── GeographicName
│   ├── CountryName
│   ├── RegionName
│   ├── CityName
│   └── VenueName
│
├── CompetitionName
├── PersonName
└── OrganizationName
```

Cada especialização representa uma categoria específica de nomes oficiais do
domínio.

---

# 10.2 GeographicName

`GeographicName` representa a abstração comum para nomes geográficos.

Sua principal responsabilidade é concentrar o comportamento compartilhado entre
os diferentes conceitos geográficos utilizados pelo domínio.

Ele não representa um conceito específico.

Seu papel é servir como base para:

- países;
- estados;
- províncias;
- regiões;
- cidades;
- estádios;
- arenas;
- centros esportivos.

A existência dessa abstração reduz duplicação e facilita a evolução da
biblioteca.

---

## Hierarquia

```text
ProperName
│
└── GeographicName
    │
    ├── CountryName
    ├── RegionName
    ├── CityName
    └── VenueName
```

---

# 10.3 CountryName

`CountryName` representa o nome oficial de um país.

Exemplos:

```python
CountryName("Brasil")
CountryName("Argentina")
CountryName("Germany")
CountryName("United Kingdom")
```

Esse tipo não representa:

- nacionalidade;
- código ISO;
- bandeira;
- continente;
- confederação esportiva.

Esses conceitos pertencem a outros componentes do domínio.

---

# 10.4 RegionName

`RegionName` representa subdivisões administrativas de um país.

Dependendo da legislação local, uma região poderá corresponder a:

- estado;
- província;
- departamento;
- distrito;
- comunidade autônoma;
- prefeitura.

Exemplos:

```python
RegionName("São Paulo")
RegionName("California")
RegionName("Bayern")
```

A biblioteca não diferencia esses formatos administrativos.

Todos são tratados como regiões administrativas.

---

# 10.5 CityName

`CityName` representa o nome oficial de uma cidade.

Exemplos:

```python
CityName("Araraquara")
CityName("Madrid")
CityName("Liverpool")
```

O tipo representa exclusivamente o nome da cidade.

Informações como:

- população;
- coordenadas;
- país;
- estado;

pertencem às entidades geográficas correspondentes.

---

# 10.6 VenueName

`VenueName` representa o nome oficial de um local esportivo.

Exemplos:

```python
VenueName("Allianz Parque")
VenueName("Old Trafford")
VenueName("Santiago Bernabéu")
```

Um local esportivo pode representar:

- estádio;
- arena;
- ginásio;
- centro esportivo;
- complexo esportivo.

A categoria física do local não altera o tipo do nome.

---

# 10.7 CompetitionName

`CompetitionName` representa o nome oficial de uma competição esportiva.

Exemplos:

```python
CompetitionName("Premier League")
CompetitionName("UEFA Champions League")
CompetitionName("Campeonato Brasileiro Série A")
```

Esse tipo representa apenas o nome.

Ele não incorpora informações sobre:

- temporada;
- categoria;
- modalidade;
- divisão;
- formato da competição.

Essas características pertencem às entidades do domínio.

Por esse motivo não existem especializações como:

- LeagueName;
- CupName;
- TournamentName.

A biblioteca diferencia conceitos semânticos, e não formatos de competição.

---

# 10.8 PersonName

`PersonName` representa o nome oficial de uma pessoa.

Exemplos:

```python
PersonName("Lionel Messi")
PersonName("Carlo Ancelotti")
PersonName("Raphael Claus")
```

O tipo não distingue:

- jogadores;
- treinadores;
- árbitros;
- dirigentes;
- médicos;
- analistas.

Todos representam pessoas.

Os diferentes papéis pertencem às entidades e não ao tipo do nome.

Consequentemente, não existem classes como:

- PlayerName;
- CoachName;
- RefereeName.

---

# 10.9 OrganizationName

`OrganizationName` representa o nome oficial de uma organização.

Exemplos:

```python
OrganizationName("FIFA")
OrganizationName("UEFA")
OrganizationName("Confederação Brasileira de Futebol")
```

Uma organização pode representar:

- federação;
- confederação;
- associação;
- empresa;
- entidade privada;
- entidade pública.

Essas categorias não justificam novos tipos.

O domínio diferencia organizações por meio das entidades correspondentes.

---

# 10.10 Igualdade

Todos os tipos de nomes seguem exatamente a mesma política de igualdade.

Dois nomes serão considerados iguais apenas quando:

- pertencerem ao mesmo tipo concreto;
- possuírem exatamente o mesmo valor.

Exemplo:

```python
CountryName("Brasil")
==
CountryName("Brasil")
```

Por outro lado:

```python
CountryName("Brasil")
!=
CompetitionName("Brasil")
```

Mesmo armazenando o mesmo texto, representam conceitos diferentes.

---

# 10.11 API Pública

Todos os tipos de nomes deverão ser importados pela API pública do pacote.

Exemplo:

```python
from ultrastats_ai.domain.shared import CountryName
from ultrastats_ai.domain.shared import CompetitionName
from ultrastats_ai.domain.shared import PersonName
from ultrastats_ai.domain.shared import OrganizationName
from ultrastats_ai.domain.shared import VenueName
```

Consumidores da biblioteca não deverão depender da organização física dos
arquivos internos.

---

# 10.12 Evolução da Biblioteca

A criação de novas especializações deverá seguir alguns princípios.

Uma nova classe somente deverá ser criada quando representar um conceito
semanticamente diferente dos já existentes.

Diferenças de:

- categoria;
- formato;
- função;
- papel;
- classificação;

não justificam novas especializações.

Por exemplo, não deverão existir classes como:

- ClubName;
- LeagueName;
- CupName;
- StadiumName;
- ArenaName;
- CoachName;
- RefereeName;
- PlayerName.

Todos esses conceitos já são representados adequadamente pelos tipos existentes.

Essa política mantém a biblioteca pequena, consistente e alinhada aos princípios
do Domain-Driven Design.

# 11. Biblioteca de Códigos

A biblioteca de códigos reúne os tipos responsáveis por representar códigos
canônicos utilizados pelo domínio.

Enquanto os nomes existem para identificação humana, os códigos existem para
identificação técnica, integração entre sistemas e representação padronizada de
conceitos do domínio.

Embora ambos sejam armazenados como texto, nomes e códigos possuem finalidades
completamente diferentes e nunca devem ser utilizados de forma intercambiável.

---

## 11.1 Objetivos

A biblioteca de códigos possui os seguintes objetivos:

- representar códigos oficiais utilizados pelo domínio;
- eliminar o uso indiscriminado de `str` para representar códigos;
- centralizar validações estruturais;
- padronizar formatos utilizados internamente;
- fornecer diferenciação semântica entre categorias de códigos;
- facilitar futuras integrações com sistemas externos.

---

## 11.2 Hierarquia

A estrutura atual da biblioteca é apresentada abaixo.

```text
TextValue
│
└── CodeValue
    │
    ├── CountryCode
    ├── CompetitionCode
    └── OrganizationCode
```

Novas especializações deverão reutilizar essa estrutura sempre que possível.

---

## 11.3 CodeValue

`CodeValue` representa a infraestrutura comum para todos os códigos utilizados
pelo domínio.

Assim como `TextValue` fornece a base para todos os valores textuais,
`CodeValue` estabelece o comportamento compartilhado entre os diferentes tipos
de códigos.

Sua responsabilidade é definir regras estruturais comuns, preservando a
consistência entre todas as especializações.

`CodeValue` não representa um conceito específico.

Ele existe exclusivamente como classe-base para tipos especializados.

---

## 11.4 Características Gerais

Todo `CodeValue` deverá possuir as seguintes características.

### Imutabilidade

Após criado, um código nunca poderá ser modificado.

---

### Igualdade

A igualdade considera:

- o tipo concreto;
- o valor armazenado.

Exemplo:

```python
CountryCode("BRA")
==
CountryCode("BRA")
```

Por outro lado:

```python
CountryCode("BRA")
!=
CompetitionCode("BRA")
```

Mesmo compartilhando o mesmo texto, representam conceitos distintos.

---

### Representação textual

Todo código possui uma representação textual única.

Essa representação deve permanecer estável durante todo o ciclo de vida do
objeto.

---

### Hash

Todos os códigos devem ser compatíveis com coleções baseadas em hashing,
permitindo utilização segura como:

- chaves de dicionários;
- elementos de conjuntos;
- índices internos.

---

## 11.5 Regras Gerais

Embora cada especialização possa definir validações adicionais, todo código
canônico deverá obedecer aos seguintes princípios.

### Normalização

Os valores deverão ser normalizados durante sua criação.

Essa normalização poderá incluir:

- remoção de espaços externos;
- padronização de caixa;
- validações estruturais.

A política específica de normalização pertence a cada especialização.

---

### Estrutura

Um código representa um identificador técnico.

Consequentemente, não deve conter:

- descrições;
- observações;
- comentários;
- informações de apresentação.

Seu único objetivo é identificar um conceito.

---

### Estabilidade

Depois de definido, um código canônico deverá permanecer estável.

Mudanças de nomenclatura, tradução ou apresentação visual nunca deverão alterar
o código associado ao conceito.

---

## 11.6 Especializações

Cada categoria de código representa um conceito diferente.

Mesmo quando compartilham exatamente o mesmo formato textual, continuam sendo
tipos distintos.

Exemplo:

```python
CountryCode("BRA")
CompetitionCode("BRA")
OrganizationCode("BRA")
```

Embora os três objetos armazenem o mesmo texto, cada um representa um conceito
próprio do domínio.

Essa diferenciação evita erros de utilização e aumenta a segurança das regras
de negócio.

---

## 11.7 Relação entre Nomes e Códigos

Nomes e códigos representam perspectivas diferentes do mesmo conceito.

Exemplo:

```text
País
│
├── CountryName("Brasil")
│
└── CountryCode("BRA")
```

O nome é destinado à comunicação humana.

O código é destinado à representação técnica.

Esses dois tipos não devem ser confundidos nem utilizados de forma
intercambiável.

---

## 11.8 API Pública

Todos os códigos deverão ser importados pela API pública do pacote.

Exemplo:

```python
from ultrastats_ai.domain.shared import CodeValue
from ultrastats_ai.domain.shared import CountryCode
from ultrastats_ai.domain.shared import CompetitionCode
from ultrastats_ai.domain.shared import OrganizationCode
```

A organização física da biblioteca permanece um detalhe interno da
implementação.

---

## 11.9 Evolução da Biblioteca

Novas especializações deverão ser criadas apenas quando representarem uma
categoria semanticamente distinta de código.

Diferenças de:

- fornecedor;
- formato de importação;
- protocolo;
- banco de dados;
- API externa;

não justificam novas especializações.

Essas diferenças pertencem à camada de infraestrutura.

O domínio representa apenas códigos canônicos.

---

## 11.10 Identificadores Externos

A biblioteca de códigos não representa identificadores provenientes de sistemas
externos.

Valores utilizados por provedores como:

- API-Football;
- SportMonks;
- Opta;
- StatsBomb;
- Football-Data;

serão representados por tipos específicos de identificadores externos.

Essa separação impede o acoplamento entre o domínio canônico e os formatos
adotados por terceiros.

---

## 11.11 Evolução Arquitetural

A biblioteca foi projetada para permitir o crescimento gradual sem necessidade
de alterações na infraestrutura existente.

Novos tipos poderão ser adicionados futuramente, desde que representem conceitos
semanticamente distintos.

Exemplo:

```text
CodeValue
│
├── CountryCode
├── CompetitionCode
├── OrganizationCode
├── SeasonCode
├── VenueCode
└── ProviderCode
```

Cada nova especialização deverá reutilizar o comportamento compartilhado de
`CodeValue`, adicionando apenas as regras específicas do conceito representado.
---

# 12. Biblioteca de Slugs

## 12.1 Objetivo

A biblioteca de slugs representa identificadores textuais estáveis e apropriados para URLs, APIs REST, rotas, pesquisa e referências públicas legíveis.

Slugs não representam nomes oficiais, códigos canônicos ou identificadores internos. Eles representam uma forma textual normalizada e restrita.

Exemplo:

```text
São Paulo Futebol Clube
↓
sao-paulo-futebol-clube
```

## 12.2 Tipo Base

A biblioteca possui o tipo:

```text
SlugValue
```

`SlugValue` herda de `TextValue` e acrescenta regras específicas para o formato de slug.

## 12.3 Regras de Normalização

Durante sua criação, `SlugValue`:

1. exige uma string;
2. remove espaços externos;
3. converte letras para minúsculas;
4. normaliza o texto Unicode;
5. remove marcas diacríticas;
6. converte sequências de espaços em hífens;
7. valida o formato canônico resultante.

Exemplo:

```python
SlugValue(" São Paulo FC ").value
```

Resultado:

```text
sao-paulo-fc
```

## 12.4 Regras de Validação

Um slug válido aceita apenas:

```text
a-z
0-9
-
```

O hífen:

- não pode aparecer no início;
- não pode aparecer no final;
- não pode aparecer duas vezes consecutivas.

Exemplos válidos:

```text
fifa
premier-league
competition-2026
sao-paulo-fc
```

Exemplos inválidos:

```text
-premier-league
premier-league-
premier--league
premier_league
premier/league
```

## 12.5 Tamanho Máximo

`SlugValue` possui limite máximo de:

```text
128 caracteres
```

A validação de tamanho é executada pela infraestrutura herdada de `TextValue`.

## 12.6 Especializações

Não existem, no estado atual, especializações como:

```text
CompetitionSlug
CountrySlug
OrganizationSlug
VenueSlug
```

Essa decisão evita duplicação, pois todas essas categorias compartilham as mesmas regras estruturais.

Especializações futuras somente deverão ser criadas quando houver comportamentos ou invariantes adicionais reais.

## 12.7 API Pública

Importação pelo pacote específico:

```python
from ultrastats_ai.domain.shared.slugs import SlugValue
```

Importação pela API pública compartilhada:

```python
from ultrastats_ai.domain.shared import SlugValue
```
---

# 13. Biblioteca de Aliases

## 13.1 Objetivo

A biblioteca de aliases representa grafias alternativas associadas a uma entidade do domínio.

Aliases podem ser utilizados para:

- resolução de entidades;
- integração entre providers;
- pesquisa textual;
- reconhecimento de abreviações;
- armazenamento de grafias históricas ou alternativas.

Exemplos:

```text
São Paulo FC
SPFC
Tricolor Paulista
Manchester Utd
Man United
PSG
Paris SG
```

## 13.2 Tipo Base

A biblioteca possui o tipo:

```text
AliasValue
```

`AliasValue` herda de `TextValue` e preserva a grafia humana do texto.

## 13.3 Regras de Normalização

Durante sua criação, `AliasValue`:

1. exige uma string;
2. normaliza Unicode para NFC;
3. remove espaços externos;
4. reduz múltiplos espaços internos para um único espaço;
5. preserva maiúsculas e minúsculas;
6. preserva acentos;
7. preserva pontuação legítima.

Exemplo:

```python
AliasValue("  São   Paulo FC  ").value
```

Resultado:

```text
São Paulo FC
```

## 13.4 Preservação da Grafia

Os seguintes valores permanecem distintos:

```python
AliasValue("PSG")
AliasValue("psg")
```

Também permanecem distintos:

```python
AliasValue("São Paulo")
AliasValue("Sao Paulo")
```

A busca tolerante a maiúsculas, minúsculas ou acentos deverá ser implementada em uma camada de pesquisa ou resolução, sem destruir a grafia original armazenada no domínio.

## 13.5 Caracteres Permitidos

`AliasValue` não utiliza uma expressão regular rígida.

Essa decisão permite aliases legítimos como:

```text
1. FC Köln
Brighton & Hove Albion
Nott'm Forest
Paris Saint-Germain
PSG / Paris SG
```

As validações estruturais básicas são herdadas de `TextValue`.

## 13.6 Tamanho Máximo

`AliasValue` possui limite máximo de:

```text
128 caracteres
```

## 13.7 Especializações

Não existem, no estado atual, especializações como:

```text
CompetitionAlias
OrganizationAlias
PersonAlias
VenueAlias
```

Aliases permanecem genéricos porque suas regras estruturais são compartilhadas.

O vínculo entre um alias e uma entidade deverá ser definido pelo agregado ou modelo que utiliza o Value Object.

## 13.8 API Pública

Importação pelo pacote específico:

```python
from ultrastats_ai.domain.shared.aliases import AliasValue
```

Importação pela API pública compartilhada:

```python
from ultrastats_ai.domain.shared import AliasValue
```

---

# 14. Biblioteca de Identificadores Externos

## 14.1 Objetivo

A biblioteca de identificadores externos representa identidades pertencentes a sistemas, APIs e providers externos.

Esses identificadores não substituem os identificadores canônicos internos do UltraStats AI.

Um identificador externo informa como uma entidade é reconhecida por um provider específico.

Exemplo:

```text
Provider: sportradar
Identificador: sr:team:1234
```

## 14.2 Componentes

A biblioteca possui três tipos principais:

```text
ProviderNamespace
ExternalIdentifier
ExternalIdentity
```

Cada tipo possui uma responsabilidade específica.

## 14.3 ProviderNamespace

`ProviderNamespace` representa o namespace estável de um provider externo.

Exemplos:

```text
opta
sportradar
football_data
transfermarkt
```

Durante sua criação, o valor:

1. deve ser uma string;
2. tem espaços externos removidos;
3. é convertido para letras minúsculas;
4. tem sequências de espaços convertidas para underscore;
5. é validado contra o formato permitido.

São aceitos:

```text
a-z
0-9
.
-
_
```

Separadores não podem aparecer no início, no final ou consecutivamente.

Exemplo:

```python
ProviderNamespace(" Football Data ").value
```

Resultado:

```text
football_data
```

O tamanho máximo é de 64 caracteres.

## 14.4 ExternalIdentifier

`ExternalIdentifier` representa a chave opaca fornecida por um provider.

Exemplos:

```text
sr:team:1234
t12345
10293
pK7Q0mTn
```

A chave é tratada como opaca. Seu conteúdo não deve ser interpretado pelo domínio compartilhado.

Durante sua criação:

1. o valor deve ser uma string;
2. Unicode é normalizado para NFC;
3. espaços externos são removidos;
4. maiúsculas e minúsculas são preservadas;
5. espaços internos são rejeitados;
6. caracteres de controle são rejeitados.

Exemplo:

```python
ExternalIdentifier("  sr:team:1234  ").value
```

Resultado:

```text
sr:team:1234
```

O tamanho máximo é de 128 caracteres.

## 14.5 ExternalIdentity

`ExternalIdentity` representa a identidade externa completa.

Ela é formada pela composição de:

```text
ProviderNamespace
+
ExternalIdentifier
```

Exemplo:

```python
ExternalIdentity(
    provider=ProviderNamespace("sportradar"),
    identifier=ExternalIdentifier("sr:team:1234"),
)
```

A igualdade considera os dois componentes.

Portanto:

```text
(opta, 100)
```

é diferente de:

```text
(sportradar, 100)
```

A propriedade:

```python
identity.key
```

retorna a chave composta em formato de tupla:

```python
("sportradar", "sr:team:1234")
```

## 14.6 Relação com Identificadores Internos

Identificadores externos não substituem tipos como:

```text
TeamId
CompetitionId
PersonId
VenueId
```

Os identificadores internos pertencem ao UltraStats AI.

Os identificadores externos pertencem aos providers.

Uma entidade interna poderá possuir várias identidades externas.

Exemplo conceitual:

```text
TeamId interno
├── (opta, t1234)
├── (sportradar, sr:team:5678)
└── (football_data, 77)
```

## 14.7 Organização Física

```text
external_ids/
├── __init__.py
├── external_identifier.py
├── external_identity.py
└── provider_namespace.py
```

## 14.8 API Pública

Importação pelo pacote específico:

```python
from ultrastats_ai.domain.shared.external_ids import (
    ExternalIdentifier,
    ExternalIdentity,
    ProviderNamespace,
)
```

Importação pela API pública compartilhada:

```python
from ultrastats_ai.domain.shared import (
    ExternalIdentifier,
    ExternalIdentity,
    ProviderNamespace,
)
```
---
# 15. Biblioteca de Tipos Numéricos

## 15.1 Objetivo

A biblioteca de tipos numéricos fornece Value Objects imutáveis para representar valores quantitativos do domínio.

Seu objetivo é evitar o uso de números primitivos sem significado explícito.

Em vez de utilizar diretamente:

```python
percentage = 75.5
probability = 0.75
age = 25
```

o domínio poderá utilizar:

```python
percentage = Percentage("75.5")
probability = Probability("0.75")
age = Age(25)
```

Cada tipo numérico concentra:

- normalização;
- validação;
- imutabilidade;
- igualdade por valor;
- significado semântico;
- regras específicas do domínio.

---

## 15.2 Princípios

Os tipos numéricos seguem os seguintes princípios:

1. valores são validados no momento da criação;
2. objetos inválidos não podem existir;
3. objetos são imutáveis;
4. valores decimais utilizam `Decimal`;
5. valores booleanos não são aceitos como números;
6. valores infinitos e `NaN` são rejeitados;
7. cada tipo representa um único conceito do domínio;
8. regras específicas permanecem dentro do respectivo Value Object.

---

## 15.3 Hierarquia Geral

A biblioteca numérica está organizada em duas classes-base principais:

```text
DecimalValue
├── Percentage
├── Probability
├── Odds
├── Height
└── Weight

IntegerValue
├── Position
├── RoundNumber
├── ShirtNumber
└── Age

Money
├── amount: Decimal
└── currency: str
```

`Money` não herda diretamente de `DecimalValue`, pois representa uma composição formada por:

```text
valor monetário
+
código da moeda
```

---

## 15.4 DecimalValue

`DecimalValue` é a classe-base dos Value Objects numéricos decimais.

Ela aceita entradas nos seguintes formatos:

```text
Decimal
int
float
str
```

Independentemente do tipo recebido, o valor é armazenado internamente como:

```python
Decimal
```

Exemplo:

```python
DecimalValue("10.50")
```

Resultado conceitual:

```text
Decimal("10.50")
```

### 15.4.1 Normalização

As seguintes entradas são válidas:

```python
DecimalValue(10)
DecimalValue(10.5)
DecimalValue("10.50")
DecimalValue(" 10.50 ")
DecimalValue(Decimal("10.50"))
```

Strings têm seus espaços externos removidos antes da conversão.

Valores `float` são convertidos inicialmente para string, reduzindo efeitos indesejados da representação binária do ponto flutuante.

Exemplo:

```python
DecimalValue(0.1)
```

é convertido utilizando:

```python
Decimal(str(0.1))
```

### 15.4.2 Valores rejeitados

São rejeitados:

```text
strings vazias
strings não numéricas
booleanos
NaN
Infinity
-Infinity
tipos não suportados
```

Exemplos inválidos:

```python
DecimalValue("")
DecimalValue("abc")
DecimalValue(True)
DecimalValue("NaN")
DecimalValue("Infinity")
```

### 15.4.3 Extensão

Subclasses especializadas implementam suas próprias regras por meio do método:

```python
_validate()
```

Assim, a classe-base concentra a conversão e as subclasses concentram as regras semânticas.

---

## 15.5 IntegerValue

`IntegerValue` é a classe-base dos Value Objects numéricos inteiros.

Ela aceita:

```text
int
str
```

Exemplos válidos:

```python
IntegerValue(10)
IntegerValue("10")
IntegerValue(" 10 ")
IntegerValue("+10")
IntegerValue("-10")
```

Todos os valores são armazenados internamente como:

```python
int
```

### 15.5.1 Valores rejeitados

São rejeitados:

```text
booleanos
strings vazias
números decimais
notação científica
strings não numéricas
tipos não suportados
```

Exemplos inválidos:

```python
IntegerValue(True)
IntegerValue("")
IntegerValue("10.5")
IntegerValue("1e2")
IntegerValue("abc")
```

### 15.5.2 Extensão

Assim como `DecimalValue`, suas subclasses acrescentam regras específicas por meio de:

```python
_validate()
```

---

## 15.6 Percentage

`Percentage` representa uma porcentagem entre:

```text
0 e 100
```

Os limites são inclusivos.

Exemplos válidos:

```python
Percentage(0)
Percentage("25")
Percentage("75.5")
Percentage(100)
```

Exemplos inválidos:

```python
Percentage("-0.01")
Percentage("100.01")
Percentage(101)
```

A representação interna utiliza:

```python
Decimal
```

Exemplo:

```python
percentage = Percentage("75.5")
```

Valor armazenado:

```python
Decimal("75.5")
```

---

## 15.7 Probability

`Probability` representa uma probabilidade entre:

```text
0 e 1
```

Os limites são inclusivos.

Exemplos válidos:

```python
Probability(0)
Probability("0.25")
Probability("0.755")
Probability(1)
```

Exemplos inválidos:

```python
Probability("-0.01")
Probability("1.01")
Probability(2)
```

A probabilidade é armazenada como fração decimal.

Exemplo:

```text
0.75 = 75%
```

A conversão para porcentagem não é realizada automaticamente, pois `Probability` e `Percentage` representam conceitos distintos.

---

## 15.8 Odds

`Odds` representa uma odd no formato decimal.

Seu valor deve ser:

```text
maior que 1
```

Exemplos válidos:

```python
Odds("1.01")
Odds("1.50")
Odds("2.00")
Odds("10.75")
```

Exemplos inválidos:

```python
Odds(0)
Odds(1)
Odds("1.0")
Odds("-2")
```

### 15.8.1 Probabilidade implícita

A propriedade:

```python
implied_probability
```

calcula a probabilidade implícita da odd por meio da fórmula:

```text
probabilidade implícita = 1 / odd
```

Exemplo:

```python
odds = Odds("2.00")
odds.implied_probability
```

Resultado:

```python
Decimal("0.5")
```

Isso representa uma probabilidade implícita de:

```text
50%
```

A propriedade retorna `Decimal`, não `Probability`, pois cálculos futuros poderão exigir políticas específicas de arredondamento ou margem da casa.

---

## 15.9 Money

`Money` representa um valor monetário associado a uma moeda.

Ele é composto por:

```text
amount
currency
```

Exemplo:

```python
Money(
    amount="150.50",
    currency="BRL",
)
```

### 15.9.1 Amount

O campo `amount` utiliza as mesmas regras de conversão de `DecimalValue`.

São aceitos:

```text
Decimal
int
float
str
```

O valor é armazenado como:

```python
Decimal
```

Valores negativos são permitidos.

Eles podem representar:

```text
prejuízos
ajustes
débitos
lucros negativos
variações negativas
```

Exemplo:

```python
Money("-25.50", "BRL")
```

### 15.9.2 Currency

O campo `currency` deve possuir exatamente três letras.

Exemplos válidos:

```text
BRL
USD
EUR
GBP
```

O valor é normalizado para letras maiúsculas.

Exemplo:

```python
Money("10.00", " brl ")
```

Resultado:

```text
amount = Decimal("10.00")
currency = "BRL"
```

Exemplos inválidos:

```text
BR
REAL
B1L
R$
```

A validação estrutural garante três letras, mas não verifica se o código está oficialmente registrado em uma lista internacional de moedas.

### 15.9.3 Operações monetárias

Valores monetários podem ser somados por meio de:

```python
first.add(second)
```

Exemplo:

```python
first = Money("10.50", "BRL")
second = Money("5.25", "BRL")

result = first.add(second)
```

Resultado:

```python
Money("15.75", "BRL")
```

Também podem ser subtraídos:

```python
result = first.subtract(second)
```

Operações entre moedas diferentes são rejeitadas.

Exemplo inválido:

```python
Money("10", "BRL").add(
    Money("10", "USD")
)
```

A conversão cambial deverá ser realizada por um serviço específico antes da operação monetária.

### 15.9.4 Valor negativo

A propriedade:

```python
is_negative
```

indica se o valor monetário é menor que zero.

Exemplo:

```python
Money("-10", "BRL").is_negative
```

Resultado:

```text
True
```

---

## 15.10 Position

`Position` representa uma posição classificatória.

Seu valor deve ser um inteiro:

```text
maior ou igual a 1
```

Exemplos válidos:

```python
Position(1)
Position("2")
Position(20)
```

Exemplos inválidos:

```python
Position(0)
Position(-1)
Position("1.5")
```

O tipo pode ser utilizado em contextos como:

```text
posição em campeonato
posição em ranking
posição em tabela
posição classificatória
```

---

## 15.11 RoundNumber

`RoundNumber` representa o número de uma rodada.

Seu valor deve ser um inteiro:

```text
maior ou igual a 1
```

Exemplos válidos:

```python
RoundNumber(1)
RoundNumber("10")
RoundNumber(38)
```

Exemplos inválidos:

```python
RoundNumber(0)
RoundNumber(-1)
RoundNumber("1.5")
```

O tipo não estabelece um limite máximo global, pois competições diferentes podem possuir quantidades diferentes de rodadas.

Limites específicos deverão ser aplicados pelo agregado ou pela competição correspondente.

---

## 15.12 ShirtNumber

`ShirtNumber` representa o número utilizado na camisa de um atleta.

O valor deve estar entre:

```text
1 e 99
```

Os limites são inclusivos.

Exemplos válidos:

```python
ShirtNumber(1)
ShirtNumber("10")
ShirtNumber(99)
```

Exemplos inválidos:

```python
ShirtNumber(0)
ShirtNumber(-1)
ShirtNumber(100)
```

A biblioteca utiliza o intervalo geral de `1` a `99`.

Restrições específicas de uma competição poderão ser implementadas em regras de domínio mais especializadas.

---

## 15.13 Height

`Height` representa altura em centímetros.

Seu valor deve estar:

```text
acima de 0
e
até 300 centímetros
```

Exemplos válidos:

```python
Height(170)
Height("182")
Height("182.5")
Height(300)
```

Exemplos inválidos:

```python
Height(0)
Height(-1)
Height("300.01")
```

### 15.13.1 Unidade canônica

A unidade canônica utilizada é:

```text
centímetros
```

Exemplo:

```python
Height("182")
```

representa:

```text
182 centímetros
```

### 15.13.2 Conversão para metros

A propriedade:

```python
meters
```

retorna a altura convertida para metros.

Exemplo:

```python
Height("182").meters
```

Resultado:

```python
Decimal("1.82")
```

A propriedade não modifica a unidade canônica armazenada.

---

## 15.14 Weight

`Weight` representa peso em quilogramas.

Seu valor deve estar:

```text
acima de 0
e
até 500 quilogramas
```

Exemplos válidos:

```python
Weight(70)
Weight("82.5")
Weight(100)
Weight(500)
```

Exemplos inválidos:

```python
Weight(0)
Weight(-1)
Weight("500.01")
```

A unidade canônica utilizada é:

```text
quilogramas
```

Outras unidades deverão ser convertidas antes da criação do Value Object.

---

## 15.15 Age

`Age` representa uma idade inteira em anos.

Seu valor deve estar entre:

```text
0 e 130
```

Os limites são inclusivos.

Exemplos válidos:

```python
Age(0)
Age(18)
Age("25")
Age(130)
```

Exemplos inválidos:

```python
Age(-1)
Age(131)
Age("25.5")
```

O valor zero é permitido para representar pessoas que ainda não completaram um ano de idade.

`Age` representa uma idade já calculada. Quando a data de nascimento estiver disponível, o cálculo deverá ser realizado a partir de um tipo temporal apropriado.

---

## 15.16 Imutabilidade e Igualdade

Todos os tipos numéricos são imutáveis.

Depois da criação, seus valores não podem ser alterados.

Exemplo inválido:

```python
age = Age(25)
age.value = 26
```

Dois Value Objects do mesmo tipo são iguais quando possuem o mesmo valor normalizado.

Exemplo:

```python
Percentage("75.5") == Percentage(75.5)
```

Resultado:

```text
True
```

Tipos semanticamente diferentes não devem ser utilizados como substitutos, mesmo quando seus valores internos forem numericamente iguais.

Exemplo conceitual:

```text
Percentage("1")
Probability("1")
```

representam conceitos diferentes.

---

## 15.17 Organização Física

A biblioteca está organizada no pacote:

```text
domain/shared/numeric/
```

Estrutura:

```text
numeric/
├── __init__.py
├── age.py
├── decimal_value.py
├── height.py
├── integer_value.py
├── money.py
├── odds.py
├── percentage.py
├── position.py
├── probability.py
├── round_number.py
├── shirt_number.py
└── weight.py
```

Responsabilidades:

```text
decimal_value.py
└── normalização e validação decimal compartilhada

integer_value.py
└── normalização e validação inteira compartilhada

percentage.py
└── porcentagens entre 0 e 100

probability.py
└── probabilidades entre 0 e 1

money.py
└── valores monetários e moedas

odds.py
└── odds decimais e probabilidade implícita

position.py
└── posições classificatórias

round_number.py
└── números de rodada

shirt_number.py
└── números de camisa

height.py
└── altura em centímetros

weight.py
└── peso em quilogramas

age.py
└── idade inteira em anos
```

---

## 15.18 API Pública

Importação pelo pacote numérico:

```python
from ultrastats_ai.domain.shared.numeric import (
    Age,
    DecimalValue,
    Height,
    IntegerValue,
    Money,
    Odds,
    Percentage,
    Position,
    Probability,
    RoundNumber,
    ShirtNumber,
    Weight,
)
```

Importação pela API pública compartilhada:

```python
from ultrastats_ai.domain.shared import (
    Age,
    DecimalValue,
    Height,
    IntegerValue,
    Money,
    Odds,
    Percentage,
    Position,
    Probability,
    RoundNumber,
    ShirtNumber,
    Weight,
)
```

Consumidores externos deverão preferir a API pública compartilhada:

```python
from ultrastats_ai.domain.shared import Percentage
```

em vez de depender diretamente da organização interna dos arquivos:

```python
from ultrastats_ai.domain.shared.numeric.percentage import Percentage
```

---
# 16. Biblioteca de Tipos Temporais e Geográficos

## 16.1 Objetivo

A biblioteca de tipos temporais e geográficos fornece Value Objects imutáveis para representar datas, instantes, intervalos, timezones e posições geográficas.

Seu objetivo é impedir ambiguidades comuns causadas pelo uso direto de strings, objetos `datetime` sem timezone e números primitivos sem unidade ou significado.

A biblioteca disponibiliza:

```text
DomainDate
UtcTimestamp
TemporalInterval
TimeZone
Latitude
Longitude
Coordinates
```

---

## 16.2 Princípios Temporais

Os tipos temporais seguem os seguintes princípios:

1. datas sem horário são representadas separadamente de timestamps;
2. timestamps devem possuir timezone;
3. timestamps são normalizados para UTC;
4. timezones utilizam identificadores IANA;
5. intervalos devem possuir início anterior ao fim;
6. objetos temporais são imutáveis;
7. strings utilizam formatos ISO quando aplicável.

---

## 16.3 DomainDate

`DomainDate` representa uma data do calendário sem horário e sem timezone.

Exemplos válidos:

```python
DomainDate("2026-07-21")
DomainDate(date(2026, 7, 21))
```

O formato textual aceito é:

```text
YYYY-MM-DD
```

Exemplos inválidos:

```python
DomainDate("21/07/2026")
DomainDate("2026-02-30")
DomainDate(datetime(2026, 7, 21, 12, 0))
```

Um objeto `datetime` é rejeitado porque contém informação de horário e deve ser representado por um tipo temporal apropriado.

### 16.3.1 Formato ISO

A propriedade:

```python
isoformat
```

retorna:

```text
YYYY-MM-DD
```

### 16.3.2 Operações

O método:

```python
add_days()
```

retorna uma nova data sem modificar o objeto original.

O método:

```python
days_until()
```

retorna a diferença em dias entre duas datas.

---

## 16.4 TimeZone

`TimeZone` representa um timezone válido da base IANA.

Exemplos válidos:

```text
UTC
America/Sao_Paulo
Europe/London
```

Exemplos inválidos:

```text
Invalid/Zone
Brazil/SaoPaulo
America/Not_A_City
```

A validação utiliza:

```python
zoneinfo.ZoneInfo
```

A propriedade:

```python
zone_info
```

retorna o objeto `ZoneInfo` correspondente.

---

## 16.5 UtcTimestamp

`UtcTimestamp` representa um instante absoluto normalizado para UTC.

Ele aceita:

```text
datetime com timezone
string ISO com timezone
string ISO terminada em Z
```

Exemplos válidos:

```python
UtcTimestamp("2026-07-21T15:30:00Z")
UtcTimestamp("2026-07-21T12:30:00-03:00")
UtcTimestamp(
    datetime(
        2026,
        7,
        21,
        15,
        30,
        tzinfo=timezone.utc,
    )
)
```

Todo valor é convertido para UTC.

Exemplo:

```python
UtcTimestamp("2026-07-21T12:30:00-03:00")
```

Resultado:

```text
2026-07-21T15:30:00Z
```

Objetos `datetime` sem timezone são rejeitados.

A propriedade:

```python
isoformat
```

retorna uma representação ISO terminada em:

```text
Z
```

O método de classe:

```python
UtcTimestamp.now()
```

retorna o instante UTC atual.

---

## 16.6 TemporalInterval

`TemporalInterval` representa um intervalo composto por:

```text
start
end
```

Ambos devem ser:

```text
UtcTimestamp
```

A regra obrigatória é:

```text
start < end
```

O intervalo segue a convenção:

```text
[start, end)
```

Isso significa:

- início incluído;
- fim excluído.

Exemplo:

```python
TemporalInterval(
    start=UtcTimestamp("2026-07-21T10:00:00Z"),
    end=UtcTimestamp("2026-07-21T11:00:00Z"),
)
```

### 16.6.1 Duração

A propriedade:

```python
duration
```

retorna um objeto:

```python
timedelta
```

A propriedade:

```python
duration_seconds
```

retorna a duração total em segundos.

### 16.6.2 Contenção

O método:

```python
contains()
```

verifica se um timestamp pertence ao intervalo.

### 16.6.3 Sobreposição

O método:

```python
overlaps()
```

verifica se dois intervalos possuem interseção.

Intervalos adjacentes não são considerados sobrepostos.

Exemplo:

```text
10:00 até 11:00
11:00 até 12:00
```

---

## 16.7 Princípios Geográficos

Os tipos geográficos seguem os seguintes princípios:

1. latitude e longitude possuem tipos distintos;
2. coordenadas são uma composição dos dois tipos;
3. valores utilizam `Decimal`;
4. limites geográficos são validados na criação;
5. coordenadas são imutáveis;
6. latitude sempre aparece antes da longitude.

---

## 16.8 Latitude

`Latitude` representa uma latitude geográfica em graus decimais.

O valor deve estar entre:

```text
-90 e 90
```

Os limites são inclusivos.

Exemplos válidos:

```python
Latitude("-90")
Latitude("-23.550520")
Latitude("0")
Latitude("90")
```

Exemplos inválidos:

```python
Latitude("-90.000001")
Latitude("90.000001")
```

---

## 16.9 Longitude

`Longitude` representa uma longitude geográfica em graus decimais.

O valor deve estar entre:

```text
-180 e 180
```

Os limites são inclusivos.

Exemplos válidos:

```python
Longitude("-180")
Longitude("-46.633308")
Longitude("0")
Longitude("180")
```

Exemplos inválidos:

```python
Longitude("-180.000001")
Longitude("180.000001")
```

---

## 16.10 Coordinates

`Coordinates` representa uma coordenada geográfica formada por:

```text
Latitude
+
Longitude
```

Exemplo:

```python
Coordinates(
    latitude=Latitude("-23.550520"),
    longitude=Longitude("-46.633308"),
)
```

Strings e números primitivos não são aceitos diretamente nos campos.

Os valores devem ser construídos previamente como:

```text
Latitude
Longitude
```

### 16.10.1 Par decimal

A propriedade:

```python
decimal_pair
```

retorna:

```python
(
    Decimal("-23.550520"),
    Decimal("-46.633308"),
)
```

### 16.10.2 Par textual

A propriedade:

```python
text_pair
```

retorna:

```text
-23.550520,-46.633308
```

A ordem oficial é:

```text
latitude,longitude
```

---

## 16.11 Imutabilidade

Todos os tipos temporais e geográficos são imutáveis.

Depois da criação, seus valores não podem ser alterados.

Exemplo inválido:

```python
coordinates.latitude = Latitude("0")
```

Operações que modificam uma data retornam um novo objeto.

Exemplo:

```python
new_date = original_date.add_days(10)
```

---

## 16.12 Organização Física

Tipos temporais:

```text
temporal/
├── __init__.py
├── domain_date.py
├── temporal_interval.py
├── time_zone.py
└── utc_timestamp.py
```

Tipos geográficos:

```text
geographic/
├── __init__.py
├── coordinates.py
├── latitude.py
└── longitude.py
```

---

## 16.13 API Pública

Importação dos tipos temporais:

```python
from ultrastats_ai.domain.shared.temporal import (
    DomainDate,
    TemporalInterval,
    TimeZone,
    UtcTimestamp,
)
```

Importação dos tipos geográficos:

```python
from ultrastats_ai.domain.shared.geographic import (
    Coordinates,
    Latitude,
    Longitude,
)
```

Importação pela API pública compartilhada:

```python
from ultrastats_ai.domain.shared import (
    Coordinates,
    DomainDate,
    Latitude,
    Longitude,
    TemporalInterval,
    TimeZone,
    UtcTimestamp,
)
```

Consumidores externos deverão preferir:

```python
from ultrastats_ai.domain.shared import UtcTimestamp
```

em vez de depender da organização interna dos arquivos.

---

# 17. Enums do Domínio

## 17.1 Objetivo

A biblioteca de enums do domínio representa conjuntos fechados de valores semânticos.

Enums devem ser utilizados quando um conceito pode assumir apenas um conjunto conhecido e controlado de estados.

Exemplos:

```text
tipo de competição
tipo de fase
estado de temporada
estado de partida
```

A utilização de enums evita strings livres como:

```python
status = "qualquer texto"
```

e permite:

```python
status = MatchStatus.LIVE
```

---

## 17.2 DomainEnum

`DomainEnum` é a classe-base dos enums canônicos do domínio.

Ela herda de:

```python
str
Enum
```

Isso permite que seus membros possuam comportamento de enum e representação textual estável.

Exemplo:

```python
str(MatchStatus.LIVE)
```

Resultado:

```text
live
```

---

## 17.3 Conversão com parse

O método:

```python
parse()
```

converte uma string para o membro correspondente.

Exemplo:

```python
MatchStatus.parse("live")
```

Resultado:

```python
MatchStatus.LIVE
```

A normalização aceita diferenças de:

```text
maiúsculas e minúsculas
espaços externos
espaços internos
hífens
underscores
```

Exemplos equivalentes:

```text
half_time
HALF_TIME
Half Time
half-time
```

Todos são convertidos para:

```python
MatchStatus.HALF_TIME
```

Valores desconhecidos geram `DomainValidationError`.

---

## 17.4 Métodos utilitários

### 17.4.1 values

Retorna os valores canônicos:

```python
MatchStatus.values()
```

Resultado conceitual:

```python
(
    "scheduled",
    "postponed",
    "cancelled",
    "abandoned",
    "live",
    "half_time",
    "extra_time",
    "penalty_shootout",
    "finished",
    "awarded",
)
```

### 17.4.2 names

Retorna os nomes simbólicos:

```python
MatchStatus.names()
```

### 17.4.3 choices

Retorna pares formados por:

```text
valor
nome simbólico
```

Exemplo:

```python
(
    ("live", "LIVE"),
    ("finished", "FINISHED"),
)
```

### 17.4.4 has_value

Verifica se uma entrada pode ser convertida para o enum.

Exemplo:

```python
MatchStatus.has_value("half time")
```

Resultado:

```text
True
```

---

## 17.5 CompetitionType

`CompetitionType` representa o formato estrutural de uma competição.

Valores:

```text
league
cup
tournament
playoff
friendly
```

Significados gerais:

```text
league
competição baseada em classificação recorrente

cup
competição predominantemente eliminatória

tournament
torneio de formato genérico ou misto

playoff
competição ou série classificatória eliminatória

friendly
competição ou evento sem caráter oficial
```

---

## 17.6 PhaseType

`PhaseType` representa uma fase dentro de uma competição.

Valores:

```text
qualifying
league_stage
group_stage
round_of_32
round_of_16
quarter_final
semi_final
third_place
final
```

Esse enum descreve a posição estrutural de uma fase no torneio.

---

## 17.7 RoundType

`RoundType` representa a natureza de uma rodada.

Valores:

```text
regular
preliminary
qualifying
group
knockout
playoff
final
```

`PhaseType` e `RoundType` possuem responsabilidades diferentes.

`PhaseType` descreve uma etapa ampla da competição.

`RoundType` descreve a natureza operacional de uma rodada específica.

---

## 17.8 SeasonStatus

`SeasonStatus` representa o estado de uma temporada.

Valores:

```text
planned
active
suspended
completed
cancelled
```

Uma temporada deve possuir apenas um desses estados por vez.

---

## 17.9 MatchStatus

`MatchStatus` representa o estado operacional de uma partida.

Valores:

```text
scheduled
postponed
cancelled
abandoned
live
half_time
extra_time
penalty_shootout
finished
awarded
```

Significados:

```text
scheduled
partida programada

postponed
partida adiada

cancelled
partida cancelada

abandoned
partida iniciada e definitivamente interrompida

live
partida em andamento

half_time
intervalo regulamentar

extra_time
prorrogação em andamento

penalty_shootout
disputa de pênaltis em andamento

finished
partida concluída normalmente

awarded
resultado atribuído administrativamente
```

---

## 17.10 ParticipantRole

`ParticipantRole` representa o papel de um participante em uma partida.

Valores:

```text
home
away
neutral
```

Significados:

```text
home
participante mandante

away
participante visitante

neutral
participante sem classificação de mandante ou visitante
```

Exemplo:

```python
ParticipantRole.parse("HOME")
```

Resultado:

```python
ParticipantRole.HOME
```

O enum representa a posição do participante no evento.

Ele não representa o tipo da entidade, como jogador, treinador ou organização.

---

## 17.11 OfficialRole

`OfficialRole` representa a função desempenhada por um oficial da partida.

Valores:

```text
referee
assistant_referee
fourth_official
video_assistant_referee
assistant_video_assistant_referee
additional_assistant_referee
reserve_assistant_referee
match_commissioner
```

Significados gerais:

```text
referee
árbitro principal

assistant_referee
árbitro assistente

fourth_official
quarto árbitro

video_assistant_referee
árbitro assistente de vídeo

assistant_video_assistant_referee
assistente do árbitro de vídeo

additional_assistant_referee
árbitro assistente adicional

reserve_assistant_referee
árbitro assistente reserva

match_commissioner
delegado ou comissário da partida
```

Os valores canônicos não armazenam traduções.

Traduções e nomes destinados ao usuário pertencem à camada de apresentação.

---

## 17.12 MovementType

`MovementType` representa a natureza de uma movimentação contratual ou esportiva.

Valores:

```text
transfer
loan
loan_return
free_transfer
release
contract_renewal
promotion
demotion
retirement
```

Significados gerais:

```text
transfer
transferência definitiva

loan
empréstimo temporário

loan_return
retorno após empréstimo

free_transfer
transferência sem taxa

release
liberação ou encerramento do vínculo

contract_renewal
renovação de contrato

promotion
promoção para outro elenco ou categoria

demotion
retorno ou rebaixamento para outro elenco ou categoria

retirement
encerramento da carreira
```

O enum registra somente o tipo da movimentação.

Dados complementares deverão pertencer a uma estrutura específica, como:

```text
data da movimentação
origem
destino
valor
duração
observações
```

---

## 17.13 EventType

`EventType` representa a natureza de um acontecimento registrado durante uma partida.

Valores:

```text
goal
own_goal
penalty_goal
penalty_missed
yellow_card
second_yellow_card
red_card
substitution
injury
offside
foul
corner
free_kick
penalty_awarded
kickoff
half_time
full_time
extra_time_start
extra_time_end
penalty_shootout_start
penalty_shootout_end
```

O enum registra apenas o tipo do evento.

Dados complementares pertencem ao objeto de evento, como:

```text
timestamp
minuto da partida
participante
jogador
equipe
resultado após o evento
localização no campo
```

`EventType.HALF_TIME` representa um acontecimento.

`MatchStatus.HALF_TIME` representa o estado atual da partida.

---

## 17.14 InterruptionType

`InterruptionType` representa o motivo de uma interrupção da partida.

Valores:

```text
injury
weather
crowd_trouble
pitch_invasion
technical_issue
lighting_failure
security_issue
referee_decision
var_check
medical_emergency
equipment_failure
other
```

Uma interrupção pode ser temporária e não implica necessariamente abandono.

O encerramento definitivo da partida deve ser representado pelo estado ou decisão correspondente.

---

## 17.15 DecisionType

`DecisionType` representa a natureza de uma decisão esportiva ou administrativa.

Valores:

```text
confirmed
overturned
awarded
disallowed
cancelled
suspended
postponed
abandoned
rescheduled
administrative_win
administrative_draw
points_deduction
fine
no_action
```

O enum pode ser utilizado em diferentes contextos, como:

```text
decisões de arbitragem
decisões disciplinares
decisões administrativas
alterações de calendário
resultados atribuídos
```

O contexto, a autoridade responsável e a justificativa devem pertencer ao objeto de decisão.

---

## 17.16 ReviewType

`ReviewType` representa o objeto principal de uma revisão.

Valores:

```text
goal
penalty
red_card
mistaken_identity
offside
handball
foul
ball_out_of_play
disciplinary_action
administrative
other
```

O enum pode representar revisões:

```text
de vídeo
disciplinares
administrativas
pós-partida
```

O resultado da revisão deve ser representado separadamente, por exemplo, com `DecisionType`.

---

## 17.17 MarketType

`MarketType` representa uma família canônica de mercados de apostas.

Valores:

```text
match_winner
double_chance
draw_no_bet
both_teams_to_score
over_under_goals
correct_score
half_time
half_time_full_time
asian_handicap
european_handicap
corners
cards
shots
player_props
team_props
other
```

Significados gerais:

```text
match_winner
mercado de vencedor da partida

double_chance
mercado em que duas possibilidades de resultado são cobertas

draw_no_bet
mercado em que o empate normalmente devolve a aposta

both_teams_to_score
mercado sobre ambas as equipes marcarem gols

over_under_goals
mercado de quantidade de gols acima ou abaixo de uma linha

correct_score
mercado de placar exato

half_time
mercados relacionados somente ao primeiro tempo

half_time_full_time
mercado que combina resultado do intervalo e resultado final

asian_handicap
mercado de handicap asiático

european_handicap
mercado de handicap europeu

corners
mercados relacionados a escanteios

cards
mercados relacionados a cartões

shots
mercados relacionados a finalizações

player_props
mercados estatísticos relacionados a jogadores

team_props
mercados estatísticos relacionados a equipes

other
mercado ainda não contemplado pelas categorias canônicas
```

Exemplo:

```python
market_type = MarketType.parse("Both Teams To Score")
```

Resultado:

```python
MarketType.BOTH_TEAMS_TO_SCORE
```

`MarketType` representa somente a família principal do mercado.

Detalhes como:

```text
linha
seleção
participante
período
handicap
valor mínimo
valor máximo
```

devem pertencer a objetos específicos do domínio de mercados.

Exemplo conceitual:

```text
MarketType
    over_under_goals

linha
    2.5

seleção
    over
```

O valor `OTHER` deve ser utilizado apenas quando o mercado não puder ser classificado em nenhuma das famílias existentes.
---
## 17.18 PredictionStatus

`PredictionStatus` representa o estado operacional de uma previsão produzida pelo sistema.

Valores:

```text
pending
processing
completed
cancelled
expired
failed
```

Significados:

```text
pending
previsão registrada e aguardando processamento

processing
previsão atualmente em processamento

completed
previsão processada com sucesso

cancelled
processamento cancelado antes da conclusão

expired
previsão que perdeu sua validade temporal

failed
processamento encerrado com erro
```

Exemplo:

```python
status = PredictionStatus.parse("PROCESSING")
```

Resultado:

```python
PredictionStatus.PROCESSING
```

O enum representa apenas o estado atual da previsão.

Dados como:

```text
probabilidade calculada
modelo utilizado
versão do modelo
horário de criação
horário de processamento
motivo da falha
data de expiração
```

devem pertencer ao objeto de previsão.

Um fluxo conceitual possível é:

```text
pending
    ↓
processing
    ↓
completed
```

Um processamento também pode terminar como:

```text
cancelled
expired
failed
```

A existência dos valores no enum não obriga que todas as transições sejam permitidas.

As regras de transição deverão ser implementadas posteriormente no agregado ou serviço responsável pela previsão.

---
## 17.19 RecommendationStatus

`RecommendationStatus` representa o ciclo de vida de uma recomendação produzida pelo sistema.

Valores:

```text
draft
published
active
expired
cancelled
archived
```

Significados:

```text
draft
recomendação criada, mas ainda não disponibilizada

published
recomendação oficialmente publicada

active
recomendação disponível e válida para utilização

expired
recomendação que ultrapassou seu período de validade

cancelled
recomendação invalidada ou cancelada

archived
recomendação mantida somente para histórico
```

Exemplo:

```python
status = RecommendationStatus.parse("Published")
```

Resultado:

```python
RecommendationStatus.PUBLISHED
```

Uma recomendação pode possuir um ciclo conceitual semelhante a:

```text
draft
    ↓
published
    ↓
active
    ↓
expired
    ↓
archived
```

Também poderá ocorrer:

```text
draft
    ↓
cancelled
```

ou:

```text
active
    ↓
cancelled
```

O enum não implementa automaticamente essas transições.

As regras que determinam quais mudanças são permitidas devem ficar no agregado responsável pelas recomendações.

`PredictionStatus` e `RecommendationStatus` possuem responsabilidades diferentes.

```text
PredictionStatus
estado do processamento de uma previsão

RecommendationStatus
estado de publicação e disponibilidade de uma recomendação
```

Uma previsão concluída não significa necessariamente que uma recomendação tenha sido publicada.

---
## 17.20 BetStatus

`BetStatus` representa o estado operacional ou o resultado de uma aposta.

Valores:

```text
open
won
lost
void
half_won
half_lost
cash_out
cancelled
pending
```

Significados:

```text
open
aposta registrada e ainda não liquidada

won
aposta liquidada como vencedora

lost
aposta liquidada como perdedora

void
aposta anulada, normalmente com devolução integral

half_won
aposta liquidada parcialmente como vencedora

half_lost
aposta liquidada parcialmente como perdedora

cash_out
aposta encerrada antecipadamente por cash out

cancelled
aposta cancelada antes de sua liquidação normal

pending
aposta aguardando confirmação, registro ou processamento
```

Exemplo:

```python
status = BetStatus.parse("Half Won")
```

Resultado:

```python
BetStatus.HALF_WON
```

Os estados:

```text
half_won
half_lost
```

são relevantes principalmente para mercados com liquidação fracionada, como determinados handicaps asiáticos.

`VOID` e `CANCELLED` não devem ser tratados obrigatoriamente como sinônimos.

Uma interpretação recomendada é:

```text
void
aposta aceita, mas posteriormente anulada na liquidação

cancelled
aposta cancelada antes de seguir seu fluxo normal
```

A regra final dependerá da integração utilizada e deverá ser normalizada pela camada anticorrupção do provider.

O enum não armazena informações financeiras.

Dados como:

```text
stake
odd
retorno
lucro
prejuízo
valor do cash out
horário da liquidação
```

devem pertencer ao objeto de aposta ou liquidação.

---
## 17.21 RiskClassification

`RiskClassification` representa uma classificação canônica de risco.

Valores:

```text
very_low
low
medium
high
very_high
```

Significados gerais:

```text
very_low
nível de risco muito baixo

low
nível de risco baixo

medium
nível de risco intermediário

high
nível de risco alto

very_high
nível de risco muito alto
```

Exemplo:

```python
risk = RiskClassification.parse("Very High")
```

Resultado:

```python
RiskClassification.VERY_HIGH
```

A classificação poderá ser utilizada em:

```text
previsões
recomendações
mercados
bilhetes
alertas
painéis analíticos
filtros
relatórios
```

`RiskClassification` não representa diretamente uma probabilidade.

Exemplo:

```text
probabilidade estimada
72%

classificação de risco
medium
```

A classificação poderá depender de vários fatores, como:

```text
probabilidade prevista
odd disponível
divergência entre modelos
qualidade dos dados
incerteza estatística
liquidez do mercado
tempo restante até a partida
volatilidade histórica
```

As regras que convertem esses fatores em uma classificação de risco não pertencem ao enum.

Essas regras deverão ficar no motor analítico ou em uma política de domínio específica.

---

## 17.22 Organização Física

```text
enums/
├── __init__.py
├── bet_status.py
├── competition_type.py
├── decision_type.py
├── domain_enum.py
├── event_type.py
├── interruption_type.py
├── market_type.py
├── match_status.py
├── movement_type.py
├── official_role.py
├── participant_role.py
├── phase_type.py
├── prediction_status.py
├── recommendation_status.py
├── review_type.py
├── risk_classification.py
├── round_type.py
└── season_status.py
```

As próximas famílias de enums serão adicionadas ao mesmo pacote.

---

## 17.23 API Pública

Todos os enums canônicos são exportados pelo pacote específico `enums` e pela API pública de `domain.shared`.

Importação pelo pacote específico:

```python
from ultrastats_ai.domain.shared.enums import (
    BetStatus,
    CompetitionType,
    DecisionType,
    DomainEnum,
    EventType,
    InterruptionType,
    MarketType,
    MatchStatus,
    MovementType,
    OfficialRole,
    ParticipantRole,
    PhaseType,
    PredictionStatus,
    RecommendationStatus,
    ReviewType,
    RiskClassification,
    RoundType,
    SeasonStatus,
)
```

Consumidores externos deverão preferir a API compartilhada:

```python
from ultrastats_ai.domain.shared import (
    BetStatus,
    CompetitionType,
    DecisionType,
    DomainEnum,
    EventType,
    InterruptionType,
    MarketType,
    MatchStatus,
    MovementType,
    OfficialRole,
    ParticipantRole,
    PhaseType,
    PredictionStatus,
    RecommendationStatus,
    ReviewType,
    RiskClassification,
    RoundType,
    SeasonStatus,
)
```

Consumidores externos deverão preferir a API compartilhada.

---

# 18. API Pública

A biblioteca de tipos canônicos disponibiliza uma API pública única para acesso
aos seus componentes.

Consumidores do domínio não deverão depender da organização física dos arquivos
internos, nem realizar importações diretamente de módulos específicos.

A API pública constitui o ponto oficial de acesso aos tipos compartilhados e
deverá permanecer estável ao longo da evolução do projeto.

Exemplo:

```python
from ultrastats_ai.domain.shared import (
    AliasValue,
    CountryName,
    CompetitionName,
    PersonName,
    OrganizationName,
    VenueName,
    CountryCode,
    CompetitionCode,
    OrganizationCode,
    SlugValue,
    ExternalIdentifier,
    ExternalIdentity,
    ProviderNamespace,
)
```

Essa abordagem desacopla os consumidores da estrutura interna da biblioteca e
permite reorganizações futuras sem impacto nas demais camadas da aplicação.

---

# 19. Organização Física

A organização física da biblioteca reflete a separação conceitual entre as
diferentes categorias de tipos compartilhados.

Uma implementação típica encontra-se organizada da seguinte maneira.

```text
domain/shared/
├── aliases/
│   ├── __init__.py
│   └── alias_value.py
├── codes/
├── names/
├── slugs/
│   ├── __init__.py
│   └── slug_value.py
├── __init__.py
└── text_value.py
```

Essa organização possui finalidade exclusivamente interna.

Consumidores da biblioteca não devem assumir que essa estrutura permanecerá
imutável.

A única interface estável é a API pública disponibilizada pelo pacote
`ultrastats_ai.domain.shared`.

---

# 20. Compatibilidade

A evolução da biblioteca deverá preservar, sempre que possível, a
compatibilidade com versões anteriores.

Quando reorganizações internas forem necessárias, deverão ser priorizadas
estratégias que reduzam o impacto sobre o restante da aplicação.

Entre essas estratégias incluem-se:

- manutenção temporária de módulos de compatibilidade;
- reexportação pela API pública;
- migração gradual de importações;
- remoção planejada de componentes obsoletos.

Mudanças incompatíveis deverão ocorrer apenas quando houver justificativa
arquitetural clara.

---

# 21. Convenções para Novos Tipos

Todo novo tipo compartilhado deverá seguir as convenções definidas neste
documento.

Antes da criação de uma nova classe, as seguintes perguntas deverão ser
respondidas.

## 21.1 O conceito já possui representação?

Caso exista um tipo capaz de representar corretamente o conceito desejado,
nenhuma nova especialização deverá ser criada.

A reutilização deve sempre ser priorizada.

---

## 21.2 Existe diferença semântica?

Diferenças apenas organizacionais não justificam novos tipos.

A nova classe deverá representar um conceito diferente, e não apenas um novo
agrupamento de objetos.

---

## 21.3 Existe comportamento próprio?

Caso o novo conceito compartilhe exatamente as mesmas regras do tipo existente,
a criação de uma nova especialização provavelmente não será necessária.

Novos tipos devem surgir para representar novos significados ou novos
comportamentos.

---

## 21.4 O tipo pertence ao domínio?

Tipos específicos de:

- banco de dados;
- APIs externas;
- protocolos;
- formatos de serialização;
- interfaces gráficas;
- bibliotecas de terceiros;

não pertencem à biblioteca canônica.

Esses componentes deverão permanecer nas camadas de infraestrutura.

---

## 21.5 O tipo possui nome adequado?

Os nomes das classes deverão representar conceitos do domínio.

Exemplos recomendados:

- CountryName;
- CompetitionCode;
- VenueName;
- MatchId.

Exemplos não recomendados:

- ApiFootballCountryName;
- SqlCompetitionCode;
- JsonVenueName;
- TemporaryPlayerName.

O nome do tipo deve representar o conceito, e nunca sua origem técnica.

---

## 21.6 A especialização é realmente necessária?

Quanto menor e mais coesa for a biblioteca, maior será sua facilidade de
manutenção.

Novas especializações devem ser criadas apenas quando agregarem significado
arquitetural ao domínio.

---

# 22. Estado Atual da Biblioteca

No momento da elaboração deste documento, a biblioteca encontra-se organizada
conforme a estrutura apresentada a seguir.

```text
ValueObject
│
├── CanonicalId
│   └── EntityId
│       └── IDs especializados
│
└── TextValue
    │
    ├── Name
    │   ├── ProperName
    │   ├── DisplayName
    │   └── ShortName
    │
    ├── CodeValue
    │   ├── CountryCode
    │   ├── CompetitionCode
    │   └── OrganizationCode
    │
    ├── SlugValue
    │
    └── AliasValue
```

Essa estrutura representa a arquitetura oficial da biblioteca de tipos
canônicos do UltraStats AI.

Novas especializações deverão preservar essa organização, reutilizando as
abstrações existentes sempre que possível e mantendo a separação entre
identificadores, nomes, códigos e demais categorias de Value Objects.

---

# 23. Considerações Finais

A biblioteca de tipos canônicos constitui um dos pilares da camada de domínio do
UltraStats AI.

Sua principal finalidade é representar conceitos de negócio de forma explícita,
segura e semanticamente consistente, reduzindo a utilização de tipos primitivos
e centralizando regras comuns em abstrações reutilizáveis.

Ao separar claramente identificadores, nomes, códigos e futuras categorias de
Value Objects, a arquitetura torna-se mais expressiva, facilita a evolução do
domínio e reduz o acoplamento entre suas diferentes partes.

Este documento deverá servir como referência oficial para a criação, evolução e
manutenção dos tipos compartilhados do projeto, garantindo que futuras
expansões permaneçam alinhadas aos princípios estabelecidos pelo
Domain-Driven Design e pela arquitetura adotada pelo UltraStats AI.