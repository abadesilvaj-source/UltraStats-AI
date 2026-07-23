# Competition Context

O contexto **Competition** representa a estrutura organizacional das competições esportivas do UltraStats AI.

## Estrutura

```text
Competition
└── Season
    ├── Stage
    │   └── Round
    └── Round

Tie
└── TieMatchReference
```

## Responsabilidades

O contexto é responsável por:

- representar competições esportivas;
- representar temporadas de uma competição;
- representar fases de uma temporada;
- representar rodadas;
- representar confrontos compostos por uma ou mais partidas;
- preservar a hierarquia entre Competition, Season, Stage e Round;
- controlar vigência temporal;
- controlar ordenação lógica das fases e rodadas;
- preservar histórico de alterações.

## Hierarquia

```text
Competition
    │
    ├── Season
    │      │
    │      ├── Stage
    │      │      │
    │      │      └── Round
    │      │
    │      └── Round
    │
    └── Tie
           │
           └── TieMatchReference
```

## Invariantes

O domínio garante as seguintes regras:

- uma `Season` pertence exatamente a uma `Competition`;
- uma `Stage` pertence exatamente a uma `Season`;
- uma `Round` pertence exatamente a uma `Season`;
- uma `Round` pode existir sem uma `Stage`;
- quando existir uma `Stage`, ela deve pertencer à mesma `Season` da `Round`;
- um `Tie` pertence a uma `Competition`;
- um `Tie` pertence a uma `Season` da mesma competição;
- quando existir uma `Stage` em um `Tie`, ela deve pertencer à mesma temporada;
- uma partida não pode aparecer duas vezes no mesmo confronto;
- duas partidas não podem possuir a mesma sequência dentro do mesmo confronto;
- nomes principais não podem aparecer novamente como aliases;
- datas de início devem ser menores ou iguais às datas de término;
- números de sequência devem ser positivos;
- entidades do domínio são imutáveis;
- igualdade entre entidades é baseada na identidade canônica.

## Estados de Season

Os estados válidos são:

```text
PLANNED
    │
    ├── ACTIVE
    │      │
    │      ├── SUSPENDED
    │      │       │
    │      │       ├── ACTIVE
    │      │       ├── COMPLETED
    │      │       └── CANCELLED
    │      │
    │      ├── COMPLETED
    │      └── CANCELLED
    │
    └── CANCELLED
```

Não existem transições a partir de:

- COMPLETED
- CANCELLED

## Imutabilidade

Todas as entidades do contexto seguem os princípios do domínio canônico:

- objetos imutáveis (`@dataclass(frozen=True, slots=True)`);
- igualdade baseada na identidade;
- métodos de alteração retornam uma nova instância;
- nenhuma alteração ocorre na instância original.

## Persistência

O contexto competitivo define apenas contratos (`Protocol`) para persistência.

Nenhuma implementação depende de:

- SQLAlchemy;
- banco de dados;
- framework web.

As implementações concretas serão adicionadas nas próximas etapas da arquitetura de infraestrutura.

## Componentes

```text
Competition
Season
Stage
Round
Tie
TieMatchReference

CompetitionRepository
SeasonRepository
TieRepository
CompetitionHistoryRepository

CompetitionReconstruction
SeasonReconstruction
StageReconstruction
RoundReconstruction
TieReconstruction
```

## Testes

Os testes unitários do contexto validam:

- criação das entidades;
- igualdade por identidade;
- imutabilidade;
- transições de temporada;
- regras de hierarquia;
- ordenação de confrontos;
- reconstrução das entidades;
- API pública;
- contratos de persistência;
- invariantes do domínio.