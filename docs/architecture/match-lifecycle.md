# UltraStats AI — Ciclo de Vida da Partida

## 1. Objetivo

Este documento define os estados possíveis de uma partida de futebol e as
transições permitidas entre esses estados.

O objetivo é evitar mudanças incoerentes e garantir que o sistema trate
corretamente partidas agendadas, adiadas, suspensas, abandonadas, finalizadas
ou decididas administrativamente.

---

## 2. Estados principais

Uma partida poderá utilizar os seguintes estados:

```text
SCHEDULED
TIME_TO_BE_DEFINED
POSTPONED
CANCELLED
DELAYED
WARMUP
FIRST_HALF
HALFTIME
SECOND_HALF
EXTRA_TIME
PENALTY_SHOOTOUT
SUSPENDED
ABANDONED
FINISHED
AWARDED
```

---

## 3. Significado dos estados

### SCHEDULED

A partida está agendada e possui data e horário definidos.

### TIME_TO_BE_DEFINED

A partida está prevista, mas ainda não possui horário confirmado.

### POSTPONED

A partida foi adiada e deverá receber uma nova data.

### CANCELLED

A partida foi cancelada e não deverá acontecer.

### DELAYED

A partida continua prevista para o mesmo dia, mas seu início está atrasado.

### WARMUP

As equipes estão em preparação e a partida está próxima do início.

### FIRST_HALF

O primeiro tempo está em andamento.

### HALFTIME

A partida está no intervalo entre o primeiro e o segundo tempo.

### SECOND_HALF

O segundo tempo está em andamento.

### EXTRA_TIME

A prorrogação está em andamento.

### PENALTY_SHOOTOUT

A disputa de pênaltis está em andamento.

### SUSPENDED

A partida foi interrompida temporariamente e poderá ser retomada.

### ABANDONED

A partida foi encerrada sem conclusão normal.

### FINISHED

A partida foi concluída normalmente.

### AWARDED

O resultado foi definido por decisão administrativa.

---

## 4. Fluxo normal

O fluxo normal de uma partida será:

```text
SCHEDULED
    ↓
WARMUP
    ↓
FIRST_HALF
    ↓
HALFTIME
    ↓
SECOND_HALF
    ↓
FINISHED
```

O estado `WARMUP` poderá ser ignorado quando o provedor não fornecer essa
informação.

Nesse caso, a transição poderá ocorrer diretamente:

```text
SCHEDULED
    ↓
FIRST_HALF
```

---

## 5. Partida com horário ainda não definido

Uma partida poderá ser criada inicialmente como:

```text
TIME_TO_BE_DEFINED
```

Quando a data e o horário forem confirmados:

```text
TIME_TO_BE_DEFINED
    ↓
SCHEDULED
```

O horário confirmado deverá ser armazenado em UTC.

O fuso horário original também deverá ser preservado.

---

## 6. Partida com prorrogação

Quando uma partida eliminatória terminar empatada no tempo regulamentar e
possuir previsão de prorrogação:

```text
SECOND_HALF
    ↓
EXTRA_TIME
    ↓
FINISHED
```

O placar da prorrogação deverá ser armazenado separadamente do placar do tempo
regulamentar.

---

## 7. Partida com disputa de pênaltis

Quando a partida seguir para disputa de pênaltis:

```text
EXTRA_TIME
    ↓
PENALTY_SHOOTOUT
    ↓
FINISHED
```

Em competições sem prorrogação, poderá ocorrer:

```text
SECOND_HALF
    ↓
PENALTY_SHOOTOUT
    ↓
FINISHED
```

O placar da disputa de pênaltis não deverá ser somado ao placar normal da
partida.

---

## 8. Partida adiada

Uma partida agendada poderá ser adiada:

```text
SCHEDULED
    ↓
POSTPONED
```

Quando a nova data for definida:

```text
POSTPONED
    ↓
SCHEDULED
```

A mudança de horário ou data não deverá criar automaticamente uma nova partida.

O mesmo `match_id` canônico deverá ser preservado.

A alteração deverá ser registrada em:

```text
MatchScheduleHistory
```

---

## 9. Partida atrasada

Uma partida poderá continuar prevista para o mesmo dia, mas começar com atraso:

```text
SCHEDULED
    ↓
DELAYED
```

Quando estiver próxima do início:

```text
DELAYED
    ↓
WARMUP
```

Ou diretamente:

```text
DELAYED
    ↓
FIRST_HALF
```

Também poderá ocorrer:

```text
DELAYED
    ↓
POSTPONED
```

O estado `DELAYED` não deverá ser tratado como adiamento definitivo.

---

## 10. Partida cancelada

Uma partida poderá ser cancelada antes do início:

```text
SCHEDULED
    ↓
CANCELLED
```

Também poderá ocorrer:

```text
TIME_TO_BE_DEFINED
    ↓
CANCELLED
```

Uma partida cancelada deverá permanecer registrada.

Ela não deverá ser removida do banco de dados.

O motivo do cancelamento deverá ser preservado quando estiver disponível.

---

## 11. Partida suspensa

Uma partida em andamento poderá ser suspensa:

```text
FIRST_HALF
    ↓
SUSPENDED
```

ou:

```text
SECOND_HALF
    ↓
SUSPENDED
```

Também poderá ocorrer durante a prorrogação:

```text
EXTRA_TIME
    ↓
SUSPENDED
```

Uma partida suspensa poderá posteriormente:

```text
ser retomada
ser abandonada
ser finalizada administrativamente
receber nova data de continuação
```

---

## 12. Retomada de partida suspensa

Quando uma partida suspensa for retomada, ela deverá voltar ao período
correspondente.

Exemplo:

```text
SUSPENDED
    ↓
SECOND_HALF
```

A retomada deverá preservar:

```text
momento da suspensão
placar no momento da suspensão
eventos já ocorridos
tempo já disputado
data e horário da retomada
```

A retomada não deverá apagar os dados anteriores.

---

## 13. Partida abandonada

Uma partida poderá ser abandonada durante o jogo:

```text
FIRST_HALF
    ↓
ABANDONED
```

ou:

```text
SECOND_HALF
    ↓
ABANDONED
```

Também poderá ocorrer:

```text
SUSPENDED
    ↓
ABANDONED
```

O estado `ABANDONED` significa que a partida não foi concluída normalmente.

O placar existente deverá ser preservado como placar observado, mas não deverá
ser tratado automaticamente como resultado final oficial.

---

## 14. Resultado administrativo

Uma partida poderá receber resultado administrativo.

Exemplo antes do início:

```text
SCHEDULED
    ↓
AWARDED
```

Exemplo após abandono:

```text
ABANDONED
    ↓
AWARDED
```

Exemplo após suspensão:

```text
SUSPENDED
    ↓
AWARDED
```

O resultado administrativo deverá preservar:

```text
motivo
placar concedido
autoridade responsável
data da decisão
fonte
observações
```

O estado `AWARDED` representa uma decisão externa ao fluxo normal da partida.

---

## 15. Partida finalizada

Uma partida concluída normalmente deverá utilizar:

```text
FINISHED
```

A finalização poderá ocorrer a partir de:

```text
SECOND_HALF
EXTRA_TIME
PENALTY_SHOOTOUT
```

Exemplos:

```text
SECOND_HALF
    ↓
FINISHED
```

```text
EXTRA_TIME
    ↓
FINISHED
```

```text
PENALTY_SHOOTOUT
    ↓
FINISHED
```

---

## 16. Transições que não devem ocorrer automaticamente

O sistema não deverá aceitar automaticamente transições incoerentes como:

```text
FINISHED
    ↓
FIRST_HALF
```

```text
CANCELLED
    ↓
SECOND_HALF
```

```text
ABANDONED
    ↓
FIRST_HALF
```

```text
AWARDED
    ↓
WARMUP
```

```text
PENALTY_SHOOTOUT
    ↓
FIRST_HALF
```

Correções excepcionais poderão existir, mas deverão ser auditadas.

---

## 17. Correções de provedor

Um provedor poderá enviar um estado incorreto e corrigi-lo posteriormente.

Exemplo:

```text
FINISHED
```

enviado por engano, quando a partida ainda estava:

```text
SECOND_HALF
```

Nesse caso:

- a correção não deverá ser ignorada;
- a alteração deverá ser auditada;
- o valor anterior deverá ser preservado no histórico;
- a origem da correção deverá ser registrada;
- previsões ou recomendações afetadas deverão poder ser identificadas.

---

## 18. Histórico de estados

Mudanças importantes de estado deverão preservar histórico.

Uma estrutura futura poderá registrar:

```text
match_status_history_id
match_id
previous_status
new_status
changed_at
source
reason
raw_payload_reference
```

O estado atual continuará armazenado em `Match`.

O histórico completo poderá ser armazenado em uma estrutura específica.

---

## 19. Fonte do estado

O estado de uma partida poderá ser informado por diferentes provedores.

Cada atualização deverá registrar:

```text
provider
horário da coleta
estado recebido
confiança
payload de origem
```

O motor de fusão será responsável por definir o estado canônico.

Nenhum provedor deverá sobrescrever silenciosamente o estado consolidado.

---

## 20. Conflitos entre provedores

Exemplo de conflito:

```text
Provider A = SECOND_HALF
Provider B = FINISHED
```

O sistema deverá considerar:

```text
horário da coleta
confiabilidade do provedor
sequência anterior de estados
eventos recebidos
placar
tempo de jogo
```

Se o conflito não puder ser resolvido com segurança:

```text
o estado deverá ser marcado para revisão
os dados conflitantes deverão ser preservados
o sistema poderá entrar em degradação controlada
```

---

## 21. Relação com eventos da partida

Os eventos podem ajudar a validar o estado.

Exemplos:

```text
KICK_OFF pode indicar início do primeiro tempo
HALFTIME pode indicar intervalo
SECOND_HALF_START pode indicar início do segundo tempo
MATCH_END pode indicar finalização
```

Entretanto, os eventos não deverão ser a única fonte do estado oficial.

O sistema deverá cruzar:

```text
estado informado
eventos
placar
tempo de jogo
dados de outros provedores
```

---

## 22. Relação com placar

O placar deverá ser coerente com o estado da partida.

Exemplos:

```text
SCHEDULED normalmente não possui placar iniciado
FIRST_HALF pode possuir placar parcial
HALFTIME possui placar parcial
FINISHED possui placar final
PENALTY_SHOOTOUT pode possuir placar de pênaltis separado
```

Inconsistências deverão ser sinalizadas.

Exemplo:

```text
status = SCHEDULED
home_score = 2
away_score = 1
```

Esse caso pode indicar:

```text
erro de estado
erro de placar
partida já iniciada
payload desatualizado
```

---

## 23. Relação com probabilidades pré-jogo

Probabilidades pré-jogo poderão ser calculadas enquanto a partida estiver em:

```text
TIME_TO_BE_DEFINED
SCHEDULED
DELAYED
POSTPONED
```

No caso de `POSTPONED`, o sistema deverá verificar se as informações ainda são
válidas após a remarcação.

Probabilidades pré-jogo deverão ser encerradas ou congeladas quando a partida
iniciar.

---

## 24. Relação com probabilidades ao vivo

Probabilidades ao vivo poderão ser utilizadas nos estados:

```text
FIRST_HALF
HALFTIME
SECOND_HALF
EXTRA_TIME
PENALTY_SHOOTOUT
```

Elas deverão ser suspensas em:

```text
SUSPENDED
ABANDONED
CANCELLED
POSTPONED
FINISHED
AWARDED
```

Durante `DELAYED`, o sistema deverá tratar a partida como ainda não iniciada.

---

## 25. Relação com recomendações

Recomendações deverão considerar o estado atual da partida.

Exemplos:

```text
recomendação pré-jogo não deve ser criada após o início
recomendação ao vivo não deve ser criada após FINISHED
recomendação deve ser suspensa durante SUSPENDED
recomendação deve ser invalidada em CANCELLED
```

Uma mudança de estado poderá alterar a validade de uma recomendação.

---

## 26. Relação com odds

Odds pré-jogo poderão existir antes do início da partida.

Odds ao vivo poderão existir durante a partida.

O estado da partida deverá ajudar a classificar a odd como:

```text
PRE_MATCH
LIVE
SUSPENDED
CLOSED
```

Odds recebidas após `FINISHED` poderão ser preservadas para histórico, mas não
deverão ser tratadas como oportunidades ativas.

---

## 27. Relação com notificações

Mudanças importantes de estado poderão gerar notificações dentro da aplicação
ou notificações push.

Exemplos:

```text
partida adiada
partida cancelada
partida iniciada
partida suspensa
partida retomada
partida finalizada
resultado administrativo
```

Notificações não deverão ser enviadas por:

```text
email
Telegram
Discord
WhatsApp
```

---

## 28. Regras de integridade

O sistema deverá impedir ou sinalizar:

```text
partida finalizada voltando para estado ao vivo sem auditoria
partida cancelada recebendo eventos ao vivo
partida sem horário definido marcada como WARMUP
partida em PENALTY_SHOOTOUT sem contexto eliminatório
partida FINISHED sem placar quando o placar deveria existir
partida POSTPONED sem preservação do horário anterior
partida AWARDED sem motivo ou fonte
transição incompatível com a sequência anterior
```

---

## 29. Regras de degradação controlada

Quando o estado não puder ser determinado com segurança, o sistema deverá evitar
inventar uma situação.

Poderá ser utilizado temporariamente:

```text
último estado confiável
estado recebido com baixa confiança
marcação de revisão necessária
suspensão de recomendações
suspensão de probabilidades ao vivo
```

A interface deverá indicar a incerteza de forma discreta.

---

## 30. Resumo das principais transições

```text
TIME_TO_BE_DEFINED → SCHEDULED

SCHEDULED → WARMUP
SCHEDULED → FIRST_HALF
SCHEDULED → DELAYED
SCHEDULED → POSTPONED
SCHEDULED → CANCELLED
SCHEDULED → AWARDED

DELAYED → WARMUP
DELAYED → FIRST_HALF
DELAYED → POSTPONED
DELAYED → CANCELLED

POSTPONED → SCHEDULED
POSTPONED → CANCELLED

WARMUP → FIRST_HALF
WARMUP → DELAYED
WARMUP → POSTPONED

FIRST_HALF → HALFTIME
FIRST_HALF → SUSPENDED
FIRST_HALF → ABANDONED

HALFTIME → SECOND_HALF
HALFTIME → SUSPENDED
HALFTIME → ABANDONED

SECOND_HALF → FINISHED
SECOND_HALF → EXTRA_TIME
SECOND_HALF → PENALTY_SHOOTOUT
SECOND_HALF → SUSPENDED
SECOND_HALF → ABANDONED

EXTRA_TIME → FINISHED
EXTRA_TIME → PENALTY_SHOOTOUT
EXTRA_TIME → SUSPENDED
EXTRA_TIME → ABANDONED

PENALTY_SHOOTOUT → FINISHED
PENALTY_SHOOTOUT → SUSPENDED
PENALTY_SHOOTOUT → ABANDONED

SUSPENDED → FIRST_HALF
SUSPENDED → SECOND_HALF
SUSPENDED → EXTRA_TIME
SUSPENDED → PENALTY_SHOOTOUT
SUSPENDED → ABANDONED
SUSPENDED → AWARDED

ABANDONED → AWARDED
```

---

## 31. Fora do escopo deste documento

Este documento não define:

```text
implementação SQLAlchemy
migrations
tabelas definitivas
algoritmo final de fusão
regras específicas de cada provedor
interface visual da linha do tempo
mercados de apostas
cálculo de probabilidades
modelos preditivos
```

Esses elementos serão definidos em etapas futuras.