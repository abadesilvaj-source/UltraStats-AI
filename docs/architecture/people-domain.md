# People Domain

## 1. Objetivo

O contexto `ultrastats_ai.domain.people` mantém a identidade canônica das
pessoas e seus perfis profissionais no futebol. Ele não conhece payloads,
identificadores ou estados particulares de providers.

## 2. Modelo

`Person` é a identidade central do contexto. Uma pessoa pode possuir, de forma
independente, perfis de:

- `Player`;
- `Coach`;
- `Referee`.

Os perfis compartilham a identidade da pessoa, mas preservam ciclo de vida,
estado e regras profissionais próprios.

## 3. Tipos principais

| Tipo | Responsabilidade |
|---|---|
| `Person` | Identidade, nome, nascimento, nacionalidade, aliases e perfis |
| `Player` | Estado e dados profissionais de jogador |
| `Coach` | Estado, função e dados profissionais de treinador |
| `Referee` | Estado, categoria, função e dados profissionais de árbitro |
| `PersonAliases` | Coleção imutável de nomes alternativos |
| `PersonHistoryEntry` | Registro imutável de alterações do contexto |

Os enums públicos representam estados, funções, categorias, tipos de perfil e
ações de histórico. Todos os tipos são exportados explicitamente pela API
pública do pacote.

## 4. Invariantes

- toda entidade possui identidade canônica;
- aliases não podem duplicar o nome principal nem se repetir;
- perfis profissionais pertencem à mesma pessoa;
- transições de estado são explícitas;
- dados históricos são imutáveis;
- reconstruções preservam a identidade persistida;
- valores externos não participam da identidade canônica.

## 5. Dependências

O contexto depende apenas dos tipos compartilhados do domínio. Outros
contextos devem referenciar pessoas por identificadores canônicos ou contratos,
sem alterar diretamente seus perfis.

## 6. Persistência

Os modelos ORM, mapeamentos e repositórios concretos serão implementados nas
etapas G5.11 a G5.13. O domínio atual permanece independente de SQLAlchemy e do
banco de dados.

## 7. Validação

Os testes estão em `tests/unit/domain/people` e cobrem linhas e branches dos
módulos públicos do contexto.
