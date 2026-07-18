# UltraStats AI — Identificadores e Mapeamentos de Provedores

## 1. Objetivo

Este documento define como entidades canônicas do UltraStats AI serão
relacionadas aos identificadores recebidos de APIs externas.

Nenhum identificador de provedor deverá ser utilizado como chave principal do
domínio canônico.

Os identificadores internos pertencem ao UltraStats AI.

Os identificadores externos pertencem aos provedores.

---

## 2. Estrutura conceitual do mapeamento

Cada mapeamento deverá possuir os seguintes campos:

```text
mapping_id
provider_name
entity_type
external_id
canonical_entity_id
external_name
external_payload_reference
confidence
mapping_status
created_at
updated_at
verified_at
verified_by
```

### Significado dos campos

```text
mapping_id
```

Identificador interno do próprio mapeamento.

```text
provider_name
```

Nome do provedor responsável pelo identificador externo.

Exemplos:

```text
football_data
api_football
sportmonks
the_odds_api
```

```text
entity_type
```

Tipo da entidade mapeada.

```text
external_id
```

Identificador fornecido pelo provedor.

```text
canonical_entity_id
```

Identificador interno da entidade canônica no UltraStats AI.

```text
external_name
```

Nome recebido do provedor.

```text
external_payload_reference
```

Referência para o payload bruto de origem.

```text
confidence
```

Confiança atribuída ao mapeamento.

```text
mapping_status
```

Estado atual do mapeamento.

```text
verified_at
```

Data da verificação manual ou automática.

```text
verified_by
```

Responsável pela verificação.

---

## 3. Tipos de entidade

O campo `entity_type` deverá aceitar inicialmente:

```text
COUNTRY
COMPETITION
SEASON
STAGE
ROUND
TEAM
PLAYER
COACH
REFEREE
STADIUM
MATCH
```

Outros tipos poderão ser adicionados futuramente.

---

## 4. Estados do mapeamento

O campo `mapping_status` deverá aceitar inicialmente:

```text
AUTOMATIC
REVIEW_REQUIRED
VERIFIED
REJECTED
CONFLICT
INACTIVE
```

### AUTOMATIC

O mapeamento foi criado automaticamente pelo sistema.

### REVIEW_REQUIRED

O mapeamento precisa de revisão.

### VERIFIED

O mapeamento foi confirmado.

### REJECTED

O mapeamento foi rejeitado.

### CONFLICT

Existe conflito entre o identificador externo e a entidade canônica.

### INACTIVE

O mapeamento deixou de ser utilizado, mas permanece preservado.

---

## 5. Exemplo de mapeamento de equipe

Entidade canônica:

```text
team_id = 6d77b114-b8df-49f7-bce8-a390b9f1f135
name = Manchester United
```

Mapeamento do Football-Data.org:

```text
provider_name = football_data
entity_type = TEAM
external_id = 66
external_name = Manchester United FC
canonical_entity_id = 6d77b114-b8df-49f7-bce8-a390b9f1f135
mapping_status = VERIFIED
confidence = 1.00
```

Mapeamento de outro provedor:

```text
provider_name = api_football
entity_type = TEAM
external_id = 33
external_name = Manchester United
canonical_entity_id = 6d77b114-b8df-49f7-bce8-a390b9f1f135
mapping_status = VERIFIED
confidence = 1.00
```

Os dois identificadores externos apontam para a mesma equipe canônica.

---

## 6. Regras gerais

A combinação abaixo deverá ser única:

```text
provider_name
entity_type
external_id
```

Um mesmo identificador externo não poderá apontar para duas entidades
canônicas do mesmo tipo.

Mapeamentos automáticos deverão possuir um valor de confiança.

Mapeamentos com baixa confiança deverão passar por revisão.

Mapeamentos rejeitados deverão ser preservados.

Alterações manuais deverão ser auditadas.

O nome externo recebido deverá ser preservado.

O payload de origem deverá poder ser localizado.

Um mapeamento não deverá ser alterado silenciosamente.

---

## 7. Resolução de entidades

A resolução de entidades poderá considerar:

```text
nome normalizado
aliases
país
competição
temporada
data de nascimento
posição
equipe atual
cidade
estádio
data da partida
horário da partida
```

Nenhuma entidade deverá ser vinculada apenas por semelhança textual quando
existirem ambiguidades relevantes.

O sistema deverá utilizar o máximo de contexto disponível.

---

## 8. Normalização de nomes

Antes da comparação, os nomes poderão passar por normalização.

Exemplos de normalização:

```text
converter para minúsculas
remover espaços duplicados
remover pontuação desnecessária
remover acentos quando necessário
padronizar abreviações
remover sufixos conhecidos
```

Exemplo:

```text
Manchester United FC
Manchester United
Man United
```

Esses nomes podem representar a mesma equipe.

A normalização não deve decidir sozinha que as entidades são iguais.

Ela apenas auxilia a comparação.

---

## 9. Níveis iniciais de confiança

Os níveis iniciais poderão seguir esta referência:

```text
1.00
identificação confirmada manualmente ou por chave oficial confiável
```

```text
0.90 a 0.99
correspondência automática muito forte
```

```text
0.75 a 0.89
correspondência provável
```

```text
0.50 a 0.74
revisão recomendada
```

```text
abaixo de 0.50
não mapear automaticamente
```

Esses limites poderão ser ajustados futuramente.

---

## 10. Mapeamento automático

Um mapeamento poderá ser criado automaticamente quando houver evidências fortes.

Exemplo de equipe:

```text
nome muito semelhante
mesmo país
mesma competição
mesma cidade
mesmo histórico recente
```

Exemplo de jogador:

```text
mesmo nome
mesma data de nascimento
mesma nacionalidade
mesma equipe
mesma posição
```

Mesmo em mapeamentos automáticos, a confiança deverá ser registrada.

---

## 11. Revisão manual

Mapeamentos deverão ser enviados para revisão quando:

```text
existirem nomes muito parecidos
houver mais de um candidato possível
a confiança estiver abaixo do limite
os dados principais estiverem incompletos
existirem conflitos entre provedores
```

A revisão manual deverá registrar:

```text
quem revisou
quando revisou
qual decisão foi tomada
qual justificativa foi utilizada
```

---

## 12. Mapeamentos rejeitados

Um mapeamento rejeitado deverá permanecer armazenado.

Isso evita que o sistema tente repetir automaticamente o mesmo erro.

Exemplo:

```text
provider_name = provider_x
external_id = 900
candidato incorreto = Team A
mapping_status = REJECTED
```

O sistema poderá tentar outro candidato, mas não deverá reutilizar
automaticamente o candidato rejeitado.

---

## 13. Conflitos

Um conflito ocorre quando um identificador externo já mapeado passa a
representar outra entidade.

Exemplo:

```text
provider_name = provider_x
entity_type = TEAM
external_id = 50
```

Esse identificador já aponta para:

```text
Team A
```

Posteriormente, o provedor envia dados que parecem representar:

```text
Team B
```

Nesse caso:

- o mapeamento não deve ser alterado automaticamente;
- o conflito deve ser registrado;
- os dados relacionados devem ir para quarentena;
- uma revisão deve ser criada;
- nenhuma entidade canônica deve ser sobrescrita silenciosamente.

---

## 14. Quarentena

Dados relacionados a mapeamentos conflitantes ou incertos poderão ser enviados
para quarentena.

A quarentena deverá preservar:

```text
payload original
provedor
endpoint
horário da coleta
motivo
entidade candidata
confiança
estado da revisão
```

Dados em quarentena não deverão atualizar diretamente o domínio canônico.

---

## 15. Identidade de países

A resolução de países poderá considerar:

```text
nome
nome oficial
código ISO alpha-2
código ISO alpha-3
código FIFA
```

Códigos confiáveis devem ter prioridade sobre comparação apenas por nome.

Exemplo:

```text
Brazil
Brasil
BRA
BR
```

Esses valores podem representar o mesmo país canônico.

---

## 16. Identidade de competições

A resolução de competições poderá considerar:

```text
nome
nome oficial
país
organizador
tipo
escopo
temporada
```

Mudanças de patrocinador ou nome comercial não devem criar automaticamente uma
nova competição.

Exemplo:

```text
Brasileirão Assaí
Campeonato Brasileiro Série A
```

Esses nomes podem representar a mesma competição canônica.

Mudanças estruturais relevantes devem ser analisadas individualmente.

---

## 17. Identidade de temporadas

A resolução de temporadas poderá considerar:

```text
competição
nome
ano inicial
ano final
data inicial
data final
```

Exemplo:

```text
2026
2026/2027
Season 2026
```

O significado depende da competição.

Uma temporada não deve ser resolvida apenas pelo texto do nome.

---

## 18. Identidade de equipes

A resolução de equipes poderá considerar:

```text
nome
nome oficial
aliases
país
cidade
tipo da equipe
competição
temporada
ano de fundação
```

Exemplo:

```text
Manchester United
Manchester United FC
Man United
Manchester Utd
```

Esses nomes podem representar a mesma equipe.

Por outro lado:

```text
Real Madrid
Real Madrid Castilla
```

São equipes diferentes.

---

## 19. Identidade de jogadores

Jogadores não devem ser identificados apenas pelo nome.

A resolução de jogadores poderá considerar:

```text
nome completo
nome conhecido
data de nascimento
nacionalidade
posição
altura
equipe atual
histórico de equipes
```

Jogadores homônimos devem permanecer como entidades diferentes.

Exemplo:

```text
dois jogadores com o mesmo nome
datas de nascimento diferentes
```

Nesse caso, devem existir duas entidades canônicas.

---

## 20. Identidade de treinadores

A resolução de treinadores poderá considerar:

```text
nome completo
data de nascimento
nacionalidade
equipe atual
histórico de equipes
função
```

Treinadores com o mesmo nome devem ser tratados como possíveis homônimos.

---

## 21. Identidade de árbitros

A resolução de árbitros poderá considerar:

```text
nome completo
data de nascimento
nacionalidade
competições em que atua
histórico de partidas
```

A identificação não deve depender apenas do nome.

---

## 22. Identidade de estádios

A resolução de estádios poderá considerar:

```text
nome
nome oficial
cidade
país
capacidade
latitude
longitude
```

Mudanças pequenas no nome não devem criar automaticamente um novo estádio.

Exemplo:

```text
Estádio do Maracanã
Maracanã
Jornalista Mário Filho
```

Esses nomes podem representar o mesmo estádio.

---

## 23. Identidade de partidas

Partidas exigem tratamento especial.

A resolução poderá considerar:

```text
competição
temporada
fase
rodada
mandante
visitante
data
horário
estádio
status
```

Mudanças de horário não devem criar automaticamente uma nova partida.

Partidas com equipes invertidas devem ser tratadas como possível conflito.

Exemplo:

```text
Team A x Team B
```

não deve ser automaticamente considerado igual a:

```text
Team B x Team A
```

O contexto da competição e da rodada deverá ser analisado.

---

## 24. Alterações de horário

Quando uma partida tiver o horário alterado:

```text
o mesmo match_id canônico deve ser preservado
```

O novo horário deverá atualizar a partida canônica.

O horário anterior deverá ser preservado no histórico de agendamento.

O mapeamento externo da partida não deverá ser recriado sem necessidade.

---

## 25. Alterações de nome

Mudanças de nome de uma entidade não devem obrigatoriamente criar uma nova
entidade canônica.

Exemplos:

```text
mudança de patrocinador
mudança de nome comercial
abreviação diferente
tradução diferente
```

O sistema deve avaliar se houve mudança apenas de representação ou mudança real
de identidade.

---

## 26. Inativação de mapeamentos

Um mapeamento poderá ser marcado como:

```text
INACTIVE
```

Isso pode ocorrer quando:

```text
o provedor deixa de utilizar o identificador
a entidade deixa de existir no provedor
o endpoint é descontinuado
o mapeamento é substituído por outro identificador
```

Mapeamentos inativos não devem ser apagados automaticamente.

---

## 27. Auditoria

Toda alteração relevante deverá ser auditável.

A auditoria deverá registrar:

```text
mapeamento alterado
valor anterior
valor novo
responsável
horário
motivo
origem da alteração
```

Alterações automáticas e manuais deverão ser diferenciadas.

---

## 28. Regras de integridade

O sistema deverá impedir ou sinalizar:

```text
identificador externo sem provedor
identificador externo sem tipo de entidade
mapeamento duplicado
um ID externo apontando para duas entidades canônicas
confiança fora do intervalo de 0 a 1
mapeamento verificado sem entidade canônica
mapeamento rejeitado sendo utilizado como válido
conflito sobrescrevendo entidade canônica
```

---

## 29. Relação com payloads brutos

Todo mapeamento criado a partir de dados externos deverá permitir localizar o
payload bruto de origem.

Essa relação pode ser feita por:

```text
external_payload_reference
```

Isso permitirá:

```text
investigar erros
reprocessar dados
comparar versões
auditar decisões
recalcular confiança
```

---

## 30. Fora do escopo deste documento

Este documento não define:

```text
algoritmos definitivos de similaridade
implementação SQLAlchemy
migrations
interfaces de revisão manual
regras finais de fusão
modelos preditivos
mercados de apostas
odds
```

Esses elementos serão definidos em etapas futuras.