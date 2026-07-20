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

## 24. Estado atual

```text
G5.3.2.1 — Base TextValue
CONCLUÍDO

G5.3.2.2.1 — Tipos Base de Nomes
CONCLUÍDO

G5.3.2.2.2 — Nomes Geográficos
PRÓXIMA ETAPA
```