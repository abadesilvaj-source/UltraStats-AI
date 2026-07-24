# Team Domain

## 1. Objetivo

O contexto `ultrastats_ai.domain.team` representa equipes canônicas, seus
vínculos com pessoas e as inscrições esportivas de atletas. O modelo é
independente dos formatos dos providers.

## 2. Agregado

`Team` é a raiz do agregado e controla:

- identidade e dados canônicos da equipe;
- tipo e estado;
- aliases;
- vínculos temporais;
- inscrições de elenco;
- prevenção de duplicidades e sobreposições inválidas.

Alterações em `TeamMembership` e `SquadRegistration` são coordenadas pela raiz
quando afetam as invariantes do agregado.

## 3. Tipos principais

| Tipo | Responsabilidade |
|---|---|
| `Team` | Aggregate Root da equipe |
| `TeamMembership` | Vínculo temporal entre pessoa e equipe |
| `SquadRegistration` | Inscrição temporal de atleta em elenco |
| `TeamAliases` | Coleção imutável de nomes alternativos |
| `TeamType` | Classificação canônica da equipe |
| `TeamStatus` | Estado operacional da equipe |
| `MembershipRole` | Papel exercido no vínculo |
| `MembershipStatus` | Estado do vínculo |
| `SquadRegistrationStatus` | Estado da inscrição |

## 4. Invariantes

- a equipe possui identidade canônica e nome válido;
- aliases não podem conflitar com o nome principal;
- membros e inscrições possuem vigência temporal válida;
- não existem identidades duplicadas no agregado;
- vínculos e inscrições encerrados não podem sofrer transições inválidas;
- inscrições referenciam pessoas e competições por identidade canônica;
- coleções expostas pelo agregado são imutáveis.

## 5. Relações com outros contextos

`Team` utiliza identificadores canônicos para pessoas, competições e elementos
geográficos. Ele não incorpora entidades pertencentes a outros agregados e não
altera seus estados.

O futuro Match Context referenciará equipes participantes sem assumir ownership
sobre o agregado Team.

## 6. Persistência

Contratos e implementações concretas de persistência serão consolidados nas
etapas G5.11 a G5.13, mantendo o domínio independente de ORM.

## 7. Validação

Os testes estão em `tests/unit/domain/team` e cobrem linhas e branches das
entidades, enums, erros, invariantes e API pública.
