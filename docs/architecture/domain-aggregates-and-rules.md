# Arquitetura dos Agregados e Regras do Domínio

## 1. Visão Geral

Este documento define a arquitetura dos agregados, os limites dos contextos, os objetos de valor e as principais regras de organização do domínio canônico do UltraStats AI.

O Modelo Canônico do Domínio descreve quais entidades existem, seus atributos, relacionamentos e significados. Este documento complementa essa modelagem ao estabelecer como essas entidades são organizadas, quais delas controlam ciclos de vida, onde as regras de negócio devem ser executadas e quais limites devem ser preservados durante a implementação.

A arquitetura descrita neste documento deverá orientar:

- os modelos de domínio;
- os modelos SQLAlchemy;
- os schemas de entrada e saída;
- os repositories;
- os services;
- as migrations;
- as validações;
- os processos de integração;
- os testes automatizados;
- os futuros fluxos estatísticos e preditivos.

Este documento não substitui o Modelo Canônico do Domínio. Os dois documentos possuem responsabilidades complementares.

O documento `canonical-domain-model.md` responde principalmente:

> Quais conceitos e entidades existem no domínio?

O documento `domain-aggregates-and-rules.md` responde principalmente:

> Como esses conceitos são organizados, modificados e mantidos de forma consistente?

---

## 2. Objetivo

O objetivo desta arquitetura é definir limites claros para o domínio do UltraStats AI, estabelecendo:

- os Bounded Contexts da plataforma;
- os Aggregate Roots;
- as entidades internas de cada agregado;
- as regras de ownership;
- os Value Objects;
- as regras de identidade;
- os limites transacionais;
- as dependências permitidas entre agregados;
- as regras de consistência;
- os serviços de domínio;
- os eventos de domínio;
- as estratégias de histórico e evolução.

Ao final da fase G4.A.4, deverá ser possível iniciar a implementação persistente do domínio sem depender de decisões arquiteturais improvisadas durante a criação dos modelos SQLAlchemy.

---

## 3. Escopo da G4.A.4

A etapa G4.A.4 está dividida em três subetapas.

| Subetapa | Descrição |
|---|---|
| G4.A.4.1 | Agregados, Bounded Contexts e Value Objects |
| G4.A.4.2 | Regras de consistência, serviços, políticas e eventos de domínio |
| G4.A.4.3 | Arquitetura transacional, histórico, concorrência e evolução |

Este documento será expandido progressivamente durante as três subetapas.

---

# Parte I — Agregados, Bounded Contexts e Value Objects

## 4. Objetivo da Parte I

A Parte I estabelece como o domínio do UltraStats AI será dividido e quais conceitos pertencem a cada fronteira arquitetural.

Esta parte deverá definir:

- os contextos do domínio;
- o vocabulário de cada contexto;
- as responsabilidades de cada contexto;
- as relações permitidas entre contextos;
- os agregados existentes;
- as raízes de agregados;
- as entidades internas;
- os objetos de valor;
- as regras de identidade e referência.

A Parte I está organizada nos seguintes capítulos:

1. filosofia do domínio e Bounded Contexts;
2. Aggregate Roots e fronteiras dos agregados;
3. entidades internas e regras de ownership;
4. Value Objects e regras de identidade.

---

## 5. Filosofia da Arquitetura do Domínio

### 5.1 Domínio independente de providers

O domínio canônico do UltraStats AI não deverá depender da estrutura de nenhum provider externo.

Providers podem representar os mesmos conceitos de maneiras diferentes. Um provider pode utilizar uma entidade específica para temporada, enquanto outro pode representar a temporada apenas como um atributo da competição. Um provider pode separar fases e rodadas, enquanto outro pode reuni-las em uma única estrutura.

Essas diferenças não devem alterar o domínio canônico.

O fluxo obrigatório de entrada dos dados será:

```text
Provider
    ↓
Raw Payload
    ↓
Validação
    ↓
Normalização
    ↓
Resolução de identidade
    ↓
Data Fusion
    ↓
Domínio Canônico
```

Payloads externos nunca deverão ser persistidos diretamente em tabelas canônicas de produção.

Os payloads brutos deverão permanecer em uma camada própria, preservando:

- provider de origem;
- horário de coleta;
- endpoint;
- parâmetros utilizados;
- versão do contrato;
- conteúdo original;
- hash do conteúdo;
- status do processamento;
- erros de validação;
- rastreabilidade do processamento.

---

### 5.2 Fonte única da verdade

Cada informação canônica deverá possuir um responsável claramente definido.

Uma informação poderá aparecer em diferentes contextos como referência, projeção, cache ou histórico, mas somente um contexto será considerado proprietário da informação oficial.

Por exemplo:

- o contexto de Competições é responsável pela identidade de uma competição;
- o contexto de Equipes é responsável pela identidade de uma equipe;
- o contexto de Pessoas é responsável pela identidade de uma pessoa;
- o contexto de Partidas é responsável pelo estado oficial de uma partida;
- o contexto de Mercado é responsável pelas odds coletadas;
- o contexto de Predições é responsável pelas probabilidades calculadas pelos modelos.

Quando uma informação for reproduzida fora do contexto proprietário, ela não deverá ser tratada como uma segunda fonte oficial.

---

### 5.3 Independência tecnológica

As regras do domínio não deverão depender diretamente de:

- SQLAlchemy;
- PostgreSQL;
- Streamlit;
- FastAPI;
- Celery;
- Redis;
- Kafka;
- RabbitMQ;
- bibliotecas de providers;
- formatos JSON externos.

A implementação poderá utilizar essas tecnologias, mas os conceitos do domínio deverão continuar compreensíveis e válidos sem elas.

---

### 5.4 Alta coesão

Entidades e regras relacionadas ao mesmo conceito de negócio deverão permanecer próximas.

Por exemplo, as seguintes estruturas apresentam alta coesão com uma partida:

- participantes;
- local da partida;
- árbitros designados;
- períodos;
- escalações;
- eventos;
- estatísticas;
- interrupções;
- alterações de horário;
- decisões oficiais;
- revisões.

Essas estruturas devem ser organizadas ao redor do contexto de Partidas, mesmo quando referenciarem entidades pertencentes a outros contextos.

---

### 5.5 Baixo acoplamento

Um contexto deverá conhecer apenas o contrato necessário para interagir com outro contexto.

O contexto de Partidas não precisa conhecer todos os atributos internos de uma equipe. Ele precisa conhecer apenas a identidade canônica da equipe e, quando necessário, uma projeção estável das informações relevantes.

Da mesma forma, o contexto de Predições não deverá modificar diretamente uma partida. Ele deverá consumir dados oficiais ou projeções produzidas pelos contextos responsáveis.

---

### 5.6 Evolução independente

Cada contexto deverá possuir capacidade de evolução sem exigir alterações desnecessárias nos demais.

Por exemplo, adicionar novos tipos de estatísticas de jogador não deverá exigir mudanças na identidade de competições, países ou estádios.

Adicionar um novo provider de odds também não deverá alterar o modelo de partidas.

---

### 5.7 Rastreabilidade

Toda informação relevante deverá ser rastreável até sua origem.

A rastreabilidade deverá permitir identificar:

- qual provider forneceu o dado;
- qual payload continha a informação;
- quando o dado foi recebido;
- como o dado foi normalizado;
- qual regra de resolução foi aplicada;
- qual decisão de fusão foi tomada;
- qual entidade canônica foi afetada;
- qual versão anterior foi substituída;
- qual usuário ou processo realizou uma correção manual.

---

### 5.8 Preservação de histórico

Alterações importantes não deverão apagar silenciosamente o estado anterior.

O sistema deverá preservar histórico sempre que houver impacto em:

- datas de partidas;
- horários;
- locais;
- status;
- participantes;
- escalações;
- resultados;
- decisões oficiais;
- dados disciplinares;
- odds;
- previsões;
- recomendações.

A estratégia detalhada de histórico será definida na G4.A.4.3.

---

### 5.9 Consistência orientada pelo domínio

A consistência não deverá ser definida apenas por constraints do banco de dados.

Constraints são importantes, mas determinadas regras exigem conhecimento do domínio.

Exemplos:

- uma partida não pode ter a mesma equipe ocupando dois papéis incompatíveis;
- um evento não pode ocorrer fora da partida à qual pertence;
- uma temporada deve pertencer à competição correta;
- uma escalação não pode vincular um jogador a uma equipe que não participa da partida;
- uma odd deve referenciar uma seleção pertencente ao mercado correto.

As regras serão distribuídas entre:

- Value Objects;
- entidades;
- Aggregate Roots;
- Domain Services;
- Domain Policies;
- constraints de persistência.

---

## 6. Bounded Context

### 6.1 Definição

Um Bounded Context é uma fronteira conceitual dentro da qual termos, entidades e regras possuem significado específico e consistente.

O mesmo termo pode apresentar significados diferentes em contextos distintos.

Por exemplo, o termo `status` pode representar:

- o estado operacional de uma coleta;
- o estado esportivo de uma partida;
- o estado de uma aposta;
- o estado de processamento de um payload;
- o estado de uma recomendação.

Esses significados não deverão ser reunidos em uma única enumeração genérica.

Cada contexto deverá possuir:

- responsabilidade definida;
- vocabulário próprio;
- regras próprias;
- modelos próprios;
- contratos de integração;
- limites de alteração;
- proprietário das informações.

---

### 6.2 Bounded Context não é apenas uma pasta

Um Bounded Context não deverá ser tratado apenas como uma divisão de diretórios.

A organização de pacotes poderá refletir os contextos, mas a existência de uma pasta não garante a existência de uma fronteira arquitetural.

Um contexto somente estará corretamente definido quando possuir:

- responsabilidade exclusiva;
- linguagem consistente;
- regras identificáveis;
- limites claros;
- contratos de comunicação;
- independência razoável de evolução.

---

### 6.3 Critérios utilizados

Os Bounded Contexts do UltraStats AI foram identificados com base nos seguintes critérios:

- responsabilidade funcional;
- ciclo de vida das entidades;
- origem das regras de negócio;
- necessidade de consistência;
- frequência de atualização;
- dependências externas;
- possibilidade de evolução independente;
- necessidade de auditoria;
- volume esperado de dados;
- perfil de leitura e escrita.

---

## 7. Bounded Contexts do UltraStats AI

O domínio completo do UltraStats AI será organizado nos contextos descritos a seguir.

### 7.1 Geography Context

Responsável pela organização geográfica utilizada pelas demais áreas do domínio.

Conceitos principais:

- Country;
- Region;
- City;
- GeoCoordinate;
- endereços e referências territoriais.

Responsabilidades:

- manter a identidade canônica de países;
- manter divisões territoriais;
- manter cidades;
- fornecer referências geográficas estáveis;
- representar coordenadas e localizações;
- manter aliases geográficos quando necessários.

O Geography Context não será responsável por:

- definir competições;
- definir nacionalidade esportiva;
- controlar locais de partidas;
- decidir elegibilidade de jogadores;
- processar endereços de usuários.

---

### 7.2 Competition Context

Responsável pela estrutura organizacional das competições esportivas.

Conceitos principais:

- Competition;
- Season;
- Stage;
- Round;
- Tie;
- regras estruturais da competição.

Responsabilidades:

- identificar competições;
- organizar temporadas;
- definir fases;
- definir rodadas;
- representar confrontos agregados;
- representar estruturas de calendário esportivo;
- manter regras organizacionais específicas de competições.

O Competition Context não será responsável por:

- controlar o estado operacional de uma partida;
- registrar eventos ocorridos durante uma partida;
- controlar equipes;
- calcular previsões;
- armazenar odds.

---

### 7.3 People Context

Responsável pela identidade canônica das pessoas relacionadas ao futebol.

Conceitos principais:

- Person;
- Player;
- Coach;
- Referee;
- perfis profissionais;
- nomes e aliases de pessoas.

Responsabilidades:

- manter a identidade canônica de pessoas;
- preservar nomes oficiais e alternativos;
- representar dados pessoais esportivamente relevantes;
- representar especializações profissionais;
- fornecer referências estáveis para jogadores, treinadores e árbitros.

O People Context não será responsável por:

- controlar o vínculo atual de uma pessoa com uma equipe;
- definir escalações;
- registrar participação em uma partida;
- registrar eventos de jogo;
- determinar punições aplicadas por uma competição.

---

### 7.4 Team Context

Responsável pela identidade e pela estrutura esportiva das equipes.

Conceitos principais:

- Team;
- TeamMembership;
- SquadRegistration;
- elenco;
- vínculo entre equipe e pessoa.

Responsabilidades:

- manter a identidade canônica das equipes;
- diferenciar clubes, seleções e outros tipos de equipe;
- controlar vínculos esportivos;
- representar registros em elencos;
- preservar histórico de associação entre pessoas e equipes.

O Team Context não será responsável por:

- definir os participantes oficiais de uma partida;
- controlar a escalação de um jogo específico;
- registrar gols ou cartões;
- definir a estrutura de uma competição.

---

### 7.5 Venue Context

Responsável pelos locais físicos em que partidas podem ser realizadas.

Conceitos principais:

- Stadium;
- instalações esportivas;
- capacidade;
- localização;
- nomes históricos e comerciais.

Responsabilidades:

- manter a identidade canônica dos estádios;
- representar localização;
- manter nomes oficiais e aliases;
- registrar características físicas relevantes;
- preservar alterações históricas importantes.

O Venue Context não será responsável por:

- decidir em qual estádio uma partida será realizada;
- controlar alterações de local de uma partida;
- registrar público e renda de um jogo;
- controlar competições.

A designação de um estádio para uma partida pertence ao Match Context.

---

### 7.6 Match Context

Responsável pelo ciclo de vida esportivo e operacional das partidas.

Conceitos principais:

- Match;
- MatchParticipant;
- MatchVenue;
- MatchOfficial;
- MatchPeriod;
- MatchSquad;
- Lineup;
- LineupEntry;
- MatchEvent;
- MatchStatistic;
- MatchInterruption;
- MatchScheduleChange;
- MatchDecision;
- MatchRevision.

Responsabilidades:

- criar e identificar partidas;
- vincular participantes;
- controlar data e horário;
- controlar local;
- registrar oficiais;
- controlar status;
- representar períodos;
- registrar escalações;
- registrar eventos;
- registrar estatísticas;
- registrar interrupções;
- preservar alterações de agenda;
- registrar decisões oficiais;
- preservar revisões.

O Match Context não será responsável por:

- manter a identidade principal de equipes;
- manter a identidade principal de pessoas;
- definir competições;
- calcular probabilidades;
- armazenar ofertas de bookmakers.

---

### 7.7 Identity Resolution Context

Responsável por relacionar identidades externas às entidades canônicas.

Conceitos principais:

- ProviderEntity;
- ExternalIdentifier;
- EntityAlias;
- IdentityCandidate;
- IdentityMatch;
- ConfidenceScore;
- ManualReview;
- ResolutionDecision.

Responsabilidades:

- armazenar identificadores externos;
- gerar candidatos de correspondência;
- executar matching automático;
- calcular confiança;
- encaminhar casos ambíguos para revisão;
- preservar decisões;
- permitir reprocessamento;
- impedir duplicação de entidades canônicas.

O Identity Resolution Context não será proprietário das entidades resolvidas. Ele apenas manterá o relacionamento entre representações externas e identidades canônicas.

---

### 7.8 Data Fusion Context

Responsável por consolidar informações normalizadas provenientes de múltiplos providers.

Conceitos principais:

- FusionCandidate;
- FusionRule;
- ProviderPriority;
- FieldProvenance;
- Conflict;
- FusionDecision;
- CanonicalUpdateProposal.

Responsabilidades:

- comparar valores concorrentes;
- aplicar prioridade de fontes;
- identificar conflitos;
- registrar proveniência por campo;
- produzir propostas de atualização canônica;
- preservar decisões automáticas e manuais;
- permitir reprocessamento.

O Data Fusion Context não deverá modificar tabelas canônicas sem passar pelos contratos de escrita do contexto proprietário.

---

### 7.9 Provider Integration Context

Responsável pela comunicação com providers externos.

Conceitos principais:

- Provider;
- ProviderCredential;
- ProviderRequest;
- RawPayload;
- Collector;
- SyncExecution;
- RateLimit;
- Retry;
- ProviderHealth.

Responsabilidades:

- realizar chamadas externas;
- controlar autenticação;
- respeitar rate limits;
- executar retries;
- armazenar payloads brutos;
- monitorar disponibilidade;
- registrar sincronizações;
- encaminhar dados para validação e normalização.

O Provider Integration Context não deverá conhecer regras internas detalhadas dos agregados canônicos.

---

### 7.10 Betting Market Context

Responsável por representar mercados e preços oferecidos por bookmakers.

Conceitos principais:

- Bookmaker;
- BettingMarket;
- BettingSelection;
- Odd;
- OddsSnapshot;
- MarketStatus.

Responsabilidades:

- manter bookmakers;
- definir mercados canônicos;
- definir seleções possíveis;
- registrar odds;
- preservar histórico de preços;
- controlar disponibilidade de mercados;
- permitir comparação entre bookmakers.

O Betting Market Context não será responsável por:

- calcular probabilidades próprias;
- recomendar apostas;
- controlar a banca do usuário;
- modificar resultados de partidas.

---

### 7.11 Statistics Context

Responsável por produzir indicadores derivados a partir dos dados canônicos.

Conceitos principais:

- StatisticalFeature;
- TeamForm;
- PlayerForm;
- CompetitionBaseline;
- SampleQuality;
- Trend;
- AggregatedStatistic.

Responsabilidades:

- calcular médias;
- produzir indicadores históricos;
- aplicar pesos temporais;
- avaliar qualidade das amostras;
- gerar features para modelos;
- produzir projeções estatísticas reutilizáveis.

O Statistics Context deverá consumir dados canônicos, sem modificar as entidades esportivas de origem.

---

### 7.12 Prediction Context

Responsável pela geração e pelo armazenamento de probabilidades próprias.

Conceitos principais:

- Prediction;
- PredictionModel;
- ModelVersion;
- Probability;
- FairOdd;
- PredictionExplanation;
- PredictionRun.

Responsabilidades:

- executar modelos;
- calcular probabilidades;
- calcular odds justas;
- preservar versões;
- registrar parâmetros;
- manter resultados imutáveis de inferência;
- fornecer explicabilidade;
- permitir comparação entre modelos.

Uma Prediction deverá ser tratada como resultado histórico de uma execução. Uma previsão já produzida não deverá ser alterada para refletir uma nova versão do modelo.

---

### 7.13 Recommendation Context

Responsável por transformar probabilidades e odds em oportunidades analisáveis.

Conceitos principais:

- BetRecommendation;
- OpportunityScore;
- ExpectedValue;
- ConfidenceLevel;
- RiskClassification;
- RecommendationExplanation.

Responsabilidades:

- comparar probabilidade própria e probabilidade implícita;
- calcular valor esperado;
- classificar risco;
- avaliar confiança;
- aplicar bloqueios de segurança;
- gerar explicações;
- preservar o histórico das recomendações.

O Recommendation Context não deverá garantir resultados financeiros.

---

### 7.14 Risk and Portfolio Context

Responsável pela gestão financeira e pela exposição do usuário.

Conceitos principais:

- Bankroll;
- BankrollTransaction;
- Bet;
- BetLeg;
- Stake;
- Exposure;
- RiskProfile;
- Portfolio;
- Settlement.

Responsabilidades:

- manter bancas;
- registrar movimentações;
- registrar apostas;
- calcular exposição;
- aplicar limites;
- liquidar apostas;
- calcular ROI, yield e drawdown;
- apoiar estratégias de stake.

Esse contexto poderá utilizar recomendações, mas a decisão final de registrar uma aposta pertence ao fluxo do usuário.

---

### 7.15 User Experience Context

Responsável pelas preferências e interações específicas do usuário.

Conceitos principais:

- User;
- UserPreference;
- Favorite;
- Alert;
- Notification;
- SavedFilter;
- DashboardConfiguration.

Responsabilidades:

- manter preferências;
- gerenciar favoritos;
- controlar alertas;
- registrar configurações de interface;
- organizar filtros salvos;
- controlar notificações internas e push.

Dados de interface não deverão alterar o significado das entidades canônicas.

---

## 8. Mapa de Contextos

### 8.1 Fluxo principal de dados

```text
Provider Integration
        ↓
Identity Resolution
        ↓
Data Fusion
        ↓
Contextos Canônicos
        ↓
Statistics
        ↓
Prediction
        ↓
Recommendation
        ↓
Risk and Portfolio
        ↓
User Experience
```

---

### 8.2 Contextos canônicos esportivos

```text
Geography
    │
    ├───────────────┐
    ▼               ▼
Competition       Venue
    │               │
    ├───────┐       │
    ▼       ▼       │
Team     People     │
    └───────┬───────┘
            ▼
           Match
```

O diagrama representa dependências conceituais e não autoriza modificação direta entre contextos.

---

### 8.3 Fluxo analítico

```text
Competition ─┐
Team ────────┤
People ──────┤
Match ───────┼──→ Statistics
Market ──────┘          │
                        ▼
                   Prediction
                        │
                        ▼
                 Recommendation
                        │
                        ▼
                Risk and Portfolio
```

---

## 9. Relações entre Contextos

### 9.1 Relação por identificador canônico

Quando um contexto precisar referenciar uma entidade pertencente a outro contexto, deverá utilizar o identificador canônico da entidade.

Exemplo conceitual:

```text
MatchParticipant
    match_id
    team_id
```

O `team_id` referencia uma equipe existente no Team Context.

O Match Context poderá usar essa referência, mas não deverá alterar diretamente os atributos internos da equipe.

---

### 9.2 Relação por snapshot

Algumas informações poderão ser preservadas como snapshot quando o valor histórico precisar permanecer imutável.

Exemplos:

- nome exibido por uma equipe no momento da partida;
- nome comercial de um estádio no momento do evento;
- descrição de uma seleção de aposta;
- versão do modelo utilizada em uma previsão;
- odd utilizada na criação de uma recomendação.

O snapshot não substitui a referência canônica. Ele preserva o contexto histórico da operação.

---

### 9.3 Relação por evento

Um contexto poderá informar outro contexto sobre uma alteração relevante por meio de eventos de domínio ou eventos de integração.

Exemplo:

```text
MatchFinished
    ↓
Statistics recalcula indicadores
    ↓
Prediction pode gerar novas previsões
    ↓
Recommendation reavalia oportunidades
```

O evento comunica um fato ocorrido. Ele não autoriza o consumidor a modificar o agregado que publicou o evento.

---

### 9.4 Relação por serviço de consulta

Um contexto poderá consultar dados de outro contexto através de um contrato de leitura.

Por exemplo, o Match Context poderá consultar se uma equipe existe e está ativa antes de criar um participante.

Essa consulta não deverá expor detalhes internos desnecessários do agregado consultado.

---

## 10. Regras Gerais dos Bounded Contexts

### 10.1 Responsabilidade exclusiva

Cada entidade canônica deverá possuir exatamente um contexto proprietário.

Uma entidade não deverá ser implementada simultaneamente como parte independente de dois contextos.

---

### 10.2 Modificação pelo contexto proprietário

Somente o contexto proprietário poderá alterar diretamente o estado oficial de suas entidades.

Outros contextos deverão:

- emitir comandos;
- enviar propostas;
- publicar eventos;
- utilizar serviços;
- manter projeções;
- armazenar referências.

---

### 10.3 Proibição de identificadores externos como identidade canônica

Identificadores de providers não poderão ser utilizados como chaves primárias das entidades canônicas.

A identidade canônica deverá ser gerada e controlada pelo UltraStats AI.

Identificadores externos deverão permanecer no Identity Resolution Context.

---

### 10.4 Proibição de payload direto

Nenhum payload bruto poderá ser transformado diretamente em uma gravação canônica sem passar pelo pipeline de:

```text
Validação
    ↓
Normalização
    ↓
Resolução de identidade
    ↓
Fusão
    ↓
Contrato de escrita do contexto proprietário
```

---

### 10.5 Ausência de dependência circular obrigatória

As relações entre contextos deverão evitar dependências circulares de escrita.

Dois contextos podem consultar informações um do outro em cenários específicos, mas não deverão depender de alterações transacionais simultâneas para preservar suas invariantes internas.

---

### 10.6 Contratos explícitos

A comunicação entre contextos deverá ocorrer por contratos explícitos.

Esses contratos poderão assumir a forma de:

- commands;
- query services;
- application services;
- domain events;
- integration events;
- schemas de entrada;
- schemas de saída;
- interfaces de repositories;
- propostas de atualização.

---

### 10.7 Modelos de leitura não definem propriedade

Um dashboard ou serviço analítico poderá reunir informações de diferentes contextos em uma única visualização.

Essa união não cria um novo proprietário para os dados.

Read Models e projeções poderão ser desnormalizados sem modificar as responsabilidades dos contextos originais.

---

### 10.8 Falhas entre contextos

Uma falha em um contexto consumidor não deverá invalidar automaticamente uma operação já confirmada pelo contexto produtor.

Por exemplo, uma falha no cálculo estatístico não deverá desfazer a finalização oficial de uma partida.

O processamento dependente deverá poder ser repetido posteriormente.

---

### 10.9 Idempotência

Operações provenientes de integrações e eventos deverão ser idempotentes sempre que possível.

O processamento repetido do mesmo payload, comando ou evento não deverá criar duplicações ou resultados inconsistentes.

---

### 10.10 Auditoria

Decisões que afetem dados canônicos deverão registrar informações suficientes para auditoria.

A auditoria deverá permitir responder:

- qual dado foi alterado;
- qual era o valor anterior;
- qual é o novo valor;
- quando ocorreu;
- qual processo realizou a alteração;
- qual foi a fonte;
- qual regra foi aplicada;
- se houve intervenção manual.

---

## 11. Contextos Canônicos e Contextos de Suporte

Os contextos do UltraStats AI podem ser classificados em três grupos.

### 11.1 Contextos canônicos esportivos

Mantêm os fatos oficiais do futebol:

- Geography;
- Competition;
- People;
- Team;
- Venue;
- Match.

---

### 11.2 Contextos de ingestão e consolidação

Transformam dados externos em propostas de dados canônicos:

- Provider Integration;
- Identity Resolution;
- Data Fusion.

---

### 11.3 Contextos analíticos e de produto

Utilizam dados canônicos para gerar análises e funcionalidades:

- Betting Market;
- Statistics;
- Prediction;
- Recommendation;
- Risk and Portfolio;
- User Experience.

---

## 12. Ordem Conceitual das Dependências

A ordem conceitual preferencial será:

```text
1. Geography
2. Competition
3. People
4. Team
5. Venue
6. Match
7. Betting Market
8. Statistics
9. Prediction
10. Recommendation
11. Risk and Portfolio
12. User Experience
```

Essa ordem não significa que todos os registros precisam ser criados exatamente nessa sequência.

Ela indica a direção principal das dependências conceituais.

Os contextos de integração operam paralelamente:

```text
Provider Integration
    ↓
Identity Resolution
    ↓
Data Fusion
    ↓
Contexto canônico proprietário
```

---

## 13. Regras de Nomenclatura

Cada contexto deverá utilizar termos específicos e consistentes.

Deverão ser evitadas classes genéricas como:

- `Data`;
- `Info`;
- `Item`;
- `Object`;
- `Record`;
- `EntityData`;
- `GenericService`;
- `Manager`;
- `Helper`.

Os nomes devem representar conceitos reconhecíveis do domínio.

Exemplos adequados:

- `MatchScheduleChange`;
- `IdentityResolutionDecision`;
- `OddsSnapshot`;
- `PredictionRun`;
- `BankrollTransaction`.

---

## 14. Decisões desta Parte

As seguintes decisões passam a fazer parte da arquitetura oficial do UltraStats AI:

1. O domínio será dividido em Bounded Contexts explícitos.
2. Cada entidade canônica possuirá um único contexto proprietário.
3. Providers não poderão escrever diretamente no domínio canônico.
4. Identificadores externos não serão identidades canônicas.
5. Relações entre contextos utilizarão identificadores canônicos, snapshots, contratos de consulta ou eventos.
6. Contextos analíticos não poderão modificar fatos esportivos oficiais.
7. Dados históricos relevantes deverão ser preservados.
8. Processamentos derivados deverão ser repetíveis.
9. A comunicação entre contextos deverá ser auditável.
10. Modelos de leitura poderão combinar contextos sem assumir propriedade sobre os dados.

---

## 15. Resultado da G4.A.4.1 — Parte 1

Com a conclusão desta parte, ficam definidos:

- a finalidade da arquitetura de agregados;
- os princípios do domínio;
- os Bounded Contexts;
- as responsabilidades de cada contexto;
- o mapa de dependências;
- as formas permitidas de comunicação;
- as regras gerais de propriedade;
- a separação entre contextos canônicos, de integração e analíticos.

A próxima parte definirá os Aggregate Roots e suas fronteiras.

Nela serão estabelecidos:

- quais entidades são raízes de agregado;
- quais entidades dependem dessas raízes;
- quais operações devem passar pela raiz;
- quais limites transacionais deverão ser preservados;
- quais referências entre agregados serão permitidas.
---

# Parte II — Aggregate Roots e Fronteiras dos Agregados

## 16. Objetivo

Esta parte define os Aggregate Roots do UltraStats AI, estabelecendo quais entidades controlam o ciclo de vida das demais e quais fronteiras transacionais deverão ser respeitadas durante a implementação.

Ao final desta seção deverá estar claramente definido:

- quais entidades são Aggregate Roots;
- quais entidades pertencem a cada agregado;
- quais entidades possuem existência independente;
- quais entidades dependem obrigatoriamente de outra entidade;
- quais operações devem ser executadas através do Aggregate Root;
- quais referências entre agregados são permitidas.

---

# 17. O que é um Aggregate

Um Aggregate é um conjunto de entidades e objetos de valor tratados como uma única unidade de consistência.

Todas as alterações relevantes devem ocorrer através de sua entidade principal, denominada Aggregate Root.

O Aggregate Root protege as invariantes do domínio e impede que entidades internas sejam modificadas de maneira inconsistente.

Uma transação nunca deverá alterar diretamente uma entidade interna ignorando sua raiz.

---

# 18. Critérios adotados

Uma entidade será considerada Aggregate Root quando atender à maioria dos seguintes critérios:

- possuir identidade própria;
- possuir ciclo de vida independente;
- representar um conceito de negócio completo;
- controlar invariantes importantes;
- ser frequentemente referenciada por outros agregados;
- existir independentemente de outras entidades;
- sobreviver à remoção de entidades internas.

Nem toda entidade canônica será uma Aggregate Root.

---

# 19. Aggregate Roots do UltraStats AI

Os Aggregate Roots definidos para o domínio são:

| Aggregate Root | Contexto |
|----------------|----------|
| Country | Geography |
| Competition | Competition |
| Season | Competition |
| Team | Team |
| Person | People |
| Stadium | Venue |
| Match | Match |
| Tie | Competition |
| Bookmaker | Betting Market |
| Prediction | Prediction |
| Bankroll | Risk and Portfolio |

Cada um desses agregados possui responsabilidade exclusiva sobre suas entidades internas.

---

# 20. Aggregate: Country

## Responsabilidade

Representar a identidade canônica de um país.

### Entidades pertencentes

- Region
- City

### Não pertencem ao agregado

- Stadium
- Team
- Person

Essas entidades apenas referenciam um país.

### Invariantes

- toda região pertence a um único país;
- toda cidade pertence a uma única região;
- regiões não podem existir sem um país.

---

# 21. Aggregate: Competition

## Responsabilidade

Controlar toda a estrutura organizacional de uma competição.

### Entidades pertencentes

- Stage
- Round

### Relacionamentos externos

- Season
- Match
- Tie

### Invariantes

- toda fase pertence a uma competição;
- toda rodada pertence à fase correspondente;
- fases não existem isoladamente.

---

# 22. Aggregate: Season

Embora relacionada a uma competição, Season possui ciclo de vida próprio.

Ela pode ser criada antes da definição completa das fases e continua existindo mesmo que novas estruturas organizacionais sejam adicionadas posteriormente.

### Responsabilidades

- calendário esportivo;
- período oficial;
- identificação da temporada.

### Referências

- Competition
- Match
- Tie

---

# 23. Aggregate: Team

O agregado Team controla toda a identidade esportiva de uma equipe.

### Entidades pertencentes

- TeamMembership
- SquadRegistration

### Não pertencem

- MatchParticipant
- MatchSquad
- Lineup

Essas entidades pertencem ao agregado Match.

### Invariantes

- um vínculo sempre pertence a uma equipe;
- registros históricos nunca alteram a identidade da equipe.

---

# 24. Aggregate: Person

Representa qualquer pessoa do domínio esportivo.

### Especializações

- Player
- Coach
- Referee

Essas especializações compartilham a mesma identidade canônica.

### Invariantes

Uma pessoa nunca poderá possuir múltiplas identidades canônicas.

Especializações representam papéis, não novas pessoas.

---

# 25. Aggregate: Stadium

Controla a identidade oficial dos locais esportivos.

### Responsabilidades

- nomes;
- localização;
- capacidade;
- aliases.

### Não pertencem

- MatchVenue

MatchVenue pertence ao agregado Match.

---

# 26. Aggregate: Match

Este é o agregado mais complexo de todo o domínio.

Sua responsabilidade é representar completamente uma partida.

### Entidades pertencentes

- MatchParticipant
- MatchVenue
- MatchOfficial
- MatchPeriod
- MatchSquad
- Lineup
- LineupEntry
- MatchEvent
- MatchStatistic
- MatchInterruption
- MatchScheduleChange
- MatchDecision
- MatchRevision

Todas essas entidades possuem ciclo de vida subordinado à partida.

Nenhuma delas poderá existir sem um Match.

---

### Invariantes

O agregado Match deverá preservar, entre outras, as seguintes regras:

- existe exatamente uma identidade oficial para cada partida;
- toda partida possui exatamente dois participantes esportivos;
- toda escalação pertence a uma única partida;
- todo evento pertence a uma única partida;
- toda estatística pertence a uma única partida;
- toda revisão pertence ao histórico daquela partida.

---

### Responsabilidade exclusiva

Somente o agregado Match poderá modificar:

- participantes;
- oficiais;
- local da partida;
- escalações;
- eventos;
- estatísticas;
- interrupções;
- histórico operacional.

Outros contextos apenas referenciam essas informações.

---

# 27. Aggregate: Tie

Responsável por confrontos compostos por múltiplas partidas.

### Responsabilidades

- jogos de ida e volta;
- placar agregado;
- critérios de classificação;
- vencedor do confronto.

As partidas permanecem pertencendo ao agregado Match.

---

# 28. Aggregate: Bookmaker

Responsável pela identidade de uma casa de apostas.

Controla:

- mercados;
- seleções;
- histórico de odds.

---

# 29. Aggregate: Prediction

Representa o resultado imutável de uma execução de modelo.

Uma Prediction nunca deverá ser modificada após publicada.

Novas execuções gerarão novas Predictions.

---

# 30. Aggregate: Bankroll

Responsável pela gestão financeira do usuário.

Controla:

- saldo;
- movimentações;
- apostas;
- liquidações;
- exposição.

---

# 31. Relações entre Agregados

Os agregados comunicam-se exclusivamente através de referências.

Exemplo:

```text
Match
 ├── competition_id
 ├── season_id
 ├── home_team_id
 ├── away_team_id
 ├── stadium_id
 └── referee_id
```

O agregado Match nunca controla diretamente essas entidades.

Ele apenas mantém referências para suas identidades.

---

# 32. Regras Gerais dos Aggregate Roots

Todos os Aggregate Roots deverão obedecer às seguintes regras:

1. somente o Aggregate Root pode modificar entidades internas;
2. entidades internas não poderão ser modificadas diretamente por outros agregados;
3. agregados comunicam-se por identificadores canônicos;
4. transações não deverão atravessar múltiplos agregados sem necessidade explícita;
5. cada agregado preserva suas próprias invariantes;
6. remoções deverão respeitar regras de integridade e histórico;
7. entidades internas nunca deverão sobreviver à remoção do Aggregate Root quando sua existência depender dele.

---

# 33. Resultado da Parte II

Com a conclusão desta etapa ficam definidos:

- os Aggregate Roots oficiais do UltraStats AI;
- as fronteiras dos agregados;
- as entidades pertencentes a cada agregado;
- as regras de composição;
- as referências permitidas entre agregados;
- as responsabilidades de cada Aggregate Root.

A próxima parte detalhará as entidades internas, as regras de ownership e os critérios que determinam quando uma entidade deve existir de forma independente ou subordinada a outra.
---

# Parte III — Entidades Internas e Regras de Ownership

## 34. Objetivo

Esta parte define as entidades internas dos agregados do UltraStats AI e estabelece as regras de ownership responsáveis por controlar seus ciclos de vida.

As entidades internas representam conceitos que possuem identidade própria dentro de um agregado, mas não possuem existência independente fora dele.

Ao final desta parte deverá estar claramente definido:

- quais entidades são internas;
- qual Aggregate Root controla cada entidade;
- quais entidades podem ser criadas isoladamente;
- quais entidades dependem obrigatoriamente de outra;
- quais operações deverão passar pelo Aggregate Root;
- quais referências externas poderão ser mantidas;
- como deverá ocorrer a remoção de entidades dependentes;
- quais dados deverão permanecer preservados como histórico.

---

## 35. Definição de Entidade Interna

Uma entidade interna é uma entidade que:

- possui identidade própria dentro de um agregado;
- possui estado e comportamento;
- apresenta ciclo de vida subordinado;
- não deve ser acessada como unidade independente de escrita;
- não pode existir sem o Aggregate Root ao qual pertence;
- deve ser criada, alterada ou removida através da raiz do agregado.

Uma entidade interna poderá possuir identificador próprio para permitir:

- rastreabilidade;
- auditoria;
- referências internas;
- persistência;
- versionamento;
- comparação histórica.

A existência de um identificador próprio não transforma automaticamente uma entidade interna em Aggregate Root.

---

## 36. Definição de Ownership

Ownership representa a responsabilidade de um Aggregate Root sobre o ciclo de vida de uma entidade interna.

Quando um Aggregate Root possui ownership sobre uma entidade, ele controla:

- criação;
- validação;
- alteração;
- inativação;
- remoção;
- histórico;
- consistência;
- relacionamento com outras entidades internas.

A entidade proprietária será responsável por garantir que nenhuma operação viole as invariantes do agregado.

---

## 37. Tipos de Ownership

O UltraStats AI utilizará três formas principais de ownership.

### 37.1 Ownership exclusivo

A entidade interna pertence a exatamente um Aggregate Root e não pode ser compartilhada por outros agregados.

Exemplos:

- MatchEvent pertence a um Match;
- MatchPeriod pertence a um Match;
- MatchScheduleChange pertence a um Match;
- LineupEntry pertence a uma Lineup subordinada a um Match.

---

### 37.2 Ownership hierárquico

Uma entidade interna pertence diretamente a outra entidade interna, mas todo o conjunto permanece subordinado ao mesmo Aggregate Root.

Exemplo:

```text
Match
    └── Lineup
            └── LineupEntry
```

Nesse caso:

- Match é o Aggregate Root;
- Lineup é uma entidade interna;
- LineupEntry é uma entidade interna subordinada à Lineup;
- todas as alterações permanecem controladas pelo Match.

---

### 37.3 Referência sem ownership

Um agregado pode referenciar uma entidade pertencente a outro agregado sem controlar seu ciclo de vida.

Exemplo:

```text
MatchParticipant
    └── team_id
```

O Match controla o MatchParticipant, mas não controla a Team referenciada por `team_id`.

A remoção ou alteração de MatchParticipant não deverá alterar a Team.

---

## 38. Regras Gerais de Ownership

As seguintes regras deverão ser aplicadas a todas as entidades internas.

### 38.1 Criação através da raiz

Uma entidade interna deverá ser criada através do Aggregate Root ou de um serviço autorizado que execute a operação em nome da raiz.

Exemplo conceitual:

```text
match.add_participant(...)
match.add_event(...)
match.register_lineup(...)
match.change_schedule(...)
```

Não deverá existir uma operação pública independente como:

```text
match_event_repository.create(...)
```

quando essa operação permitir contornar as invariantes do Match.

---

### 38.2 Alteração através da raiz

Alterações em entidades internas deverão passar pelo Aggregate Root.

Exemplo:

```text
match.correct_event(...)
match.replace_official(...)
match.update_lineup_entry(...)
```

A implementação poderá utilizar repositories internos para persistência, mas as decisões de negócio deverão permanecer sob controle da raiz.

---

### 38.3 Remoção controlada

Uma entidade interna não deverá ser removida sem validação do Aggregate Root.

A remoção poderá assumir uma das seguintes formas:

- remoção física;
- inativação;
- cancelamento;
- substituição;
- revisão histórica;
- marcação como incorreta.

A estratégia dependerá da importância histórica da entidade.

---

### 38.4 Proibição de compartilhamento

Uma mesma instância de entidade interna não poderá pertencer simultaneamente a dois Aggregate Roots.

Um MatchEvent não poderá pertencer a duas partidas.

Uma Lineup não poderá pertencer a dois Matches.

Uma SquadRegistration não poderá pertencer simultaneamente a duas equipes.

---

### 38.5 Referências externas por identidade

Entidades internas poderão referenciar Aggregate Roots externos apenas por identificadores canônicos.

Exemplo:

```text
MatchOfficial
    person_id
    role
```

O MatchOfficial pertence ao Match, enquanto a pessoa identificada por `person_id` pertence ao People Context.

---

### 38.6 Não propagação automática de alterações externas

Alterações em um Aggregate Root externo não deverão modificar automaticamente o histórico interno de outro agregado.

Exemplo:

Se o nome atual de uma equipe for alterado, o registro histórico de uma partida poderá continuar preservando o nome exibido no momento do jogo através de snapshot.

---

### 38.7 Validação de referência

Antes de aceitar uma referência externa, o Aggregate Root poderá validar:

- existência;
- estado ativo;
- compatibilidade;
- papel;
- vigência;
- pertencimento ao contexto esperado.

Essa validação não transfere ownership.

---

## 39. Entidades Internas do Geography Aggregate

### 39.1 Region

Region representa uma divisão territorial pertencente a um Country.

Ownership:

```text
Country
    └── Region
```

Regras:

- toda Region pertence a exatamente um Country;
- uma Region não poderá existir sem Country;
- o código regional deverá ser único dentro do Country quando aplicável;
- a remoção do Country deverá considerar a existência de referências históricas;
- uma Region não poderá ser movida silenciosamente para outro Country.

A transferência de uma Region entre países, quando necessária por razões históricas ou políticas, deverá ser representada como alteração auditável e não como simples substituição de chave estrangeira.

---

### 39.2 City

City representa uma cidade vinculada a uma Region ou diretamente a um Country quando não houver divisão regional aplicável.

Ownership conceitual:

```text
Country
    └── Region
            └── City
```

Em territórios sem divisão regional:

```text
Country
    └── City
```

Regras:

- uma City deverá possuir Country;
- Region poderá ser opcional conforme a estrutura territorial;
- uma City não poderá pertencer a Country incompatível com sua Region;
- mudanças territoriais deverão preservar histórico;
- aliases de cidade deverão permanecer associados à identidade canônica.

---

## 40. Entidades Internas do Competition Aggregate

### 40.1 Stage

Stage representa uma fase de uma competição ou temporada.

Ownership:

```text
Competition
    └── Stage
```

Quando a fase for específica de uma temporada, deverá manter referência à Season correspondente.

Regras:

- uma Stage deverá pertencer a uma Competition;
- uma Stage poderá estar limitada a uma Season;
- a ordem das fases deverá ser coerente;
- fases eliminatórias e classificatórias poderão possuir regras diferentes;
- uma Stage não deverá ser reutilizada entre competições distintas;
- alterações estruturais deverão preservar o histórico da temporada.

---

### 40.2 Round

Round representa uma rodada dentro de uma fase ou temporada.

Ownership hierárquico:

```text
Competition
    └── Stage
            └── Round
```

Regras:

- uma Round deverá pertencer a uma Stage;
- sua Stage deverá pertencer à mesma Competition;
- a numeração ou ordenação deverá ser única dentro do escopo definido;
- rodadas não deverão existir isoladamente;
- alterações de nome ou ordem deverão ser auditáveis;
- a remoção de uma Round não deverá apagar partidas históricas.

---

## 41. Entidades Internas do Team Aggregate

### 41.1 TeamMembership

TeamMembership representa o vínculo de uma pessoa com uma equipe durante determinado período.

Ownership:

```text
Team
    └── TeamMembership
```

Referências externas:

- Person;
- função ou papel;
- período de vigência.

Regras:

- todo TeamMembership pertence a uma Team;
- toda associação deverá referenciar uma Person válida;
- períodos de vínculo deverão ser consistentes;
- vínculos históricos não deverão ser sobrescritos;
- uma pessoa poderá possuir múltiplos vínculos históricos;
- vínculos simultâneos poderão existir apenas quando permitidos pelo domínio;
- o encerramento de um vínculo não deverá remover seu histórico.

---

### 41.2 SquadRegistration

SquadRegistration representa o registro de uma pessoa em um elenco específico.

Ownership:

```text
Team
    └── SquadRegistration
```

Referências externas:

- Person;
- Competition;
- Season;
- função esportiva;
- número de inscrição.

Regras:

- toda SquadRegistration pertence a uma Team;
- deverá existir período ou contexto de validade;
- a pessoa registrada deverá possuir papel compatível;
- registros duplicados deverão ser impedidos;
- o número da camisa poderá variar por temporada ou competição;
- alterações deverão preservar o histórico;
- o registro não garante participação em uma partida específica.

A participação em uma partida pertence ao Match Aggregate.

---

## 42. Entidades Internas do Person Aggregate

### 42.1 Player

Player representa uma especialização esportiva de Person.

Ownership:

```text
Person
    └── Player
```

Player não deverá possuir identidade canônica independente de Person.

Regras:

- um Player deverá referenciar exatamente uma Person;
- a identidade principal será a identidade da Person;
- atributos específicos de jogador permanecerão na especialização;
- a remoção da especialização não deverá remover a Person;
- uma Person poderá adquirir ou perder um papel profissional ao longo do tempo;
- histórico profissional deverá ser preservado.

---

### 42.2 Coach

Coach representa uma especialização profissional de Person.

Ownership:

```text
Person
    └── Coach
```

Regras:

- Coach deverá compartilhar a identidade da Person;
- licenças, funções e especialidades poderão possuir histórico;
- vínculos com equipes não pertencem ao Person Aggregate;
- a atuação em uma partida pertence ao Match Aggregate;
- uma Person poderá ser Player e Coach em períodos diferentes ou simultaneamente, quando aplicável.

---

### 42.3 Referee

Referee representa uma especialização profissional de Person.

Ownership:

```text
Person
    └── Referee
```

Regras:

- Referee deverá compartilhar a identidade da Person;
- categorias e credenciais poderão possuir vigência;
- designações para partidas não pertencem ao Person Aggregate;
- MatchOfficial será responsável pelo papel exercido em uma partida específica;
- alterações de categoria deverão preservar histórico.

---

## 43. Entidades Internas do Match Aggregate

O Match Aggregate possui a maior quantidade de entidades internas do domínio.

Todas as entidades descritas nesta seção dependem de um Match.

---

### 43.1 MatchParticipant

MatchParticipant representa uma equipe participante de uma partida.

Ownership:

```text
Match
    └── MatchParticipant
```

Referência externa:

- Team.

Regras:

- deverá pertencer a exatamente um Match;
- deverá referenciar exatamente uma Team;
- uma Team não poderá ocupar papéis incompatíveis na mesma partida;
- os papéis deverão ser únicos quando o formato exigir;
- alterações de participante deverão preservar histórico;
- o participante não controla a Team referenciada;
- placares e resultados deverão permanecer vinculados ao participante correto.

---

### 43.2 MatchVenue

MatchVenue representa o local designado para a realização da partida.

Ownership:

```text
Match
    └── MatchVenue
```

Referência externa:

- Stadium.

Regras:

- deverá pertencer a exatamente um Match;
- poderá representar local confirmado, provisório ou histórico;
- mudanças de estádio deverão gerar histórico;
- o MatchVenue não poderá alterar o Stadium;
- dados históricos relevantes poderão ser preservados por snapshot;
- uma partida poderá possuir múltiplos registros históricos de local, mas apenas um local vigente por vez.

---

### 43.3 MatchOfficial

MatchOfficial representa a atuação de uma pessoa como oficial em uma partida.

Ownership:

```text
Match
    └── MatchOfficial
```

Referência externa:

- Person ou Referee.

Regras:

- deverá pertencer a exatamente um Match;
- deverá possuir papel definido;
- papéis exclusivos não poderão ser duplicados;
- substituições deverão preservar histórico;
- uma pessoa não poderá exercer papéis incompatíveis na mesma partida;
- o MatchOfficial não altera o perfil profissional da pessoa.

---

### 43.4 MatchPeriod

MatchPeriod representa um período regulamentar ou adicional da partida.

Ownership:

```text
Match
    └── MatchPeriod
```

Regras:

- deverá pertencer a exatamente um Match;
- a ordem dos períodos deverá ser válida;
- intervalos de tempo não deverão se sobrepor de forma inválida;
- períodos adicionais dependerão das regras da competição;
- placares parciais deverão ser coerentes com os eventos;
- períodos encerrados não deverão ser alterados sem revisão auditável.

---

### 43.5 MatchSquad

MatchSquad representa o grupo de pessoas disponibilizadas por uma equipe para uma partida.

Ownership:

```text
Match
    └── MatchSquad
```

Referências externas:

- Team;
- Person;
- SquadRegistration.

Regras:

- deverá pertencer a exatamente um Match;
- deverá estar associado a um MatchParticipant;
- pessoas incluídas deverão possuir vínculo ou justificativa válida;
- uma pessoa não poderá integrar os dois lados da mesma partida;
- alterações posteriores à confirmação deverão ser auditadas;
- MatchSquad não substitui o elenco permanente da Team.

---

### 43.6 Lineup

Lineup representa a escalação de uma equipe em uma partida.

Ownership:

```text
Match
    └── Lineup
```

Regras:

- deverá pertencer a exatamente um Match;
- deverá estar vinculada a um MatchParticipant;
- uma equipe deverá possuir no máximo uma escalação vigente por tipo;
- versões anteriores deverão ser preservadas quando substituídas;
- a escalação oficial deverá respeitar as regras da competição;
- Lineup controla suas LineupEntries internamente.

---

### 43.7 LineupEntry

LineupEntry representa a participação planejada de uma pessoa em uma Lineup.

Ownership hierárquico:

```text
Match
    └── Lineup
            └── LineupEntry
```

Referências externas:

- Person;
- Player;
- MatchSquad.

Regras:

- deverá pertencer a exatamente uma Lineup;
- a pessoa deverá pertencer ao lado correspondente;
- uma pessoa não poderá aparecer duplicada na mesma escalação;
- titular e reserva deverão possuir classificações compatíveis;
- número de camisa deverá respeitar as regras aplicáveis;
- posição poderá ser representada por Value Object;
- alterações após confirmação deverão gerar revisão.

---

### 43.8 MatchEvent

MatchEvent representa um acontecimento registrado durante a partida.

Ownership:

```text
Match
    └── MatchEvent
```

Referências externas possíveis:

- MatchParticipant;
- Person;
- MatchPeriod;
- outro MatchEvent.

Regras:

- deverá pertencer a exatamente um Match;
- deverá possuir tipo válido;
- o tempo deverá ser compatível com o período;
- participantes referenciados deverão pertencer à partida;
- pessoas referenciadas deverão estar relacionadas à equipe correta;
- eventos anulados deverão permanecer preservados;
- correções deverão gerar revisão ou histórico;
- eventos que alteram o placar deverão passar pelas regras do Match.

---

### 43.9 MatchStatistic

MatchStatistic representa uma estatística oficial ou consolidada da partida.

Ownership:

```text
Match
    └── MatchStatistic
```

Referências internas possíveis:

- MatchParticipant;
- Person;
- MatchPeriod.

Regras:

- deverá pertencer a exatamente um Match;
- deverá possuir métrica definida;
- unidade e escopo deverão ser compatíveis;
- estatísticas de equipe deverão referenciar participante válido;
- estatísticas individuais deverão referenciar pessoa válida;
- valores concorrentes de providers deverão passar por fusão;
- revisões deverão preservar proveniência;
- estatísticas derivadas poderão pertencer ao Statistics Context quando não forem fatos oficiais da partida.

---

### 43.10 MatchInterruption

MatchInterruption representa uma interrupção operacional da partida.

Ownership:

```text
Match
    └── MatchInterruption
```

Regras:

- deverá pertencer a exatamente um Match;
- deverá registrar motivo;
- deverá registrar início e, quando aplicável, encerramento;
- interrupções não poderão produzir intervalos temporais inválidos;
- suspensão e abandono deverão seguir políticas específicas;
- a retomada deverá ser auditável;
- interrupções históricas não deverão ser apagadas.

---

### 43.11 MatchScheduleChange

MatchScheduleChange representa uma alteração de data, horário ou planejamento da partida.

Ownership:

```text
Match
    └── MatchScheduleChange
```

Regras:

- deverá pertencer a exatamente um Match;
- deverá preservar valor anterior e novo valor;
- deverá registrar motivo quando disponível;
- deverá registrar origem da alteração;
- múltiplas alterações deverão formar uma sequência cronológica;
- o estado atual do Match deverá ser coerente com a alteração mais recente;
- alterações não deverão apagar o planejamento anterior.

---

### 43.12 MatchDecision

MatchDecision representa uma decisão oficial que afeta a interpretação ou o resultado da partida.

Ownership:

```text
Match
    └── MatchDecision
```

Regras:

- deverá pertencer a exatamente um Match;
- deverá possuir autoridade ou fonte;
- deverá registrar data de vigência;
- deverá preservar o estado anterior;
- decisões posteriores poderão substituir efeitos anteriores sem apagar o histórico;
- decisões poderão alterar placar oficial, vencedor ou classificação;
- alterações deverão gerar eventos e revisões apropriadas.

---

### 43.13 MatchRevision

MatchRevision representa uma revisão auditável do estado da partida.

Ownership:

```text
Match
    └── MatchRevision
```

Regras:

- deverá pertencer a exatamente um Match;
- deverá identificar o dado revisado;
- deverá preservar valor anterior e novo valor;
- deverá registrar origem;
- deverá registrar justificativa;
- deverá possuir ordem cronológica;
- revisões não deverão ser editadas silenciosamente;
- correções de revisão deverão gerar nova revisão.

---

## 44. Entidades Internas do Tie Aggregate

### 44.1 TieMatchReference

O Tie poderá manter referências para as partidas que compõem o confronto.

Ownership:

```text
Tie
    └── TieMatchReference
```

Referência externa:

- Match.

Regras:

- cada referência deverá apontar para uma partida válida;
- uma partida não deverá ser duplicada no mesmo confronto;
- a ordem dos jogos deverá ser preservada;
- o Tie não controla o ciclo de vida do Match;
- alterações no resultado oficial de uma partida poderão exigir recálculo do confronto;
- referências removidas deverão preservar auditoria quando já utilizadas oficialmente.

---

### 44.2 TieScore

O placar agregado poderá ser representado como estado interno calculado ou como Value Object.

Ele não deverá ser mantido como fonte independente quando puder ser derivado das partidas oficiais.

Quando persistido por desempenho, deverá ser tratado como projeção recalculável.

---

## 45. Entidades Internas do Bookmaker Aggregate

A estrutura definitiva do Betting Market Context será aprofundada durante a modelagem específica de mercados e odds.

Inicialmente, o ownership deverá seguir:

```text
Bookmaker
    └── OddsSourceConfiguration
```

Mercados canônicos e seleções não deverão necessariamente pertencer ao Bookmaker, pois devem permanecer reutilizáveis entre diferentes casas de apostas.

Odds e snapshots poderão exigir agregados próprios devido ao volume, frequência de atualização e necessidade de escrita independente.

Essa decisão deverá ser revisada antes da implementação do Betting Market Context.

---

## 46. Entidades Internas do Prediction Aggregate

### 46.1 PredictionResult

PredictionResult representa uma probabilidade calculada para um mercado ou seleção.

Ownership:

```text
Prediction
    └── PredictionResult
```

Regras:

- deverá pertencer a exatamente uma Prediction;
- deverá referenciar mercado e seleção válidos;
- a probabilidade deverá respeitar os limites permitidos;
- resultados publicados serão imutáveis;
- nova execução deverá gerar nova Prediction;
- valores não deverão ser sobrescritos por versões futuras do modelo.

---

### 46.2 PredictionExplanation

PredictionExplanation registra fatores utilizados para explicar uma previsão.

Ownership:

```text
Prediction
    └── PredictionExplanation
```

Regras:

- deverá pertencer a exatamente uma Prediction;
- deverá referenciar a versão do modelo utilizada;
- deverá preservar os fatores relevantes;
- não deverá expor informações técnicas sensíveis desnecessárias;
- deverá permanecer coerente com o resultado publicado.

---

## 47. Entidades Internas do Bankroll Aggregate

### 47.1 BankrollTransaction

BankrollTransaction representa uma movimentação financeira da banca.

Ownership:

```text
Bankroll
    └── BankrollTransaction
```

Regras:

- deverá pertencer a exatamente uma Bankroll;
- deverá possuir tipo e valor;
- deverá preservar data e origem;
- movimentações confirmadas deverão ser imutáveis;
- correções deverão ocorrer por movimentação compensatória;
- o saldo deverá ser derivável das movimentações.

---

### 47.2 Bet

Bet representa uma aposta registrada dentro da banca.

Ownership inicial:

```text
Bankroll
    └── Bet
```

Regras:

- deverá pertencer a exatamente uma Bankroll;
- deverá possuir stake válida;
- deverá preservar odd registrada;
- deverá possuir status controlado;
- liquidação deverá ser auditável;
- uma aposta confirmada não deverá ser alterada silenciosamente;
- correções deverão preservar o estado anterior.

Dependendo do crescimento do domínio, Bet poderá futuramente tornar-se Aggregate Root independente. Essa decisão deverá considerar:

- volume de operações;
- concorrência;
- necessidade de acesso individual;
- complexidade de liquidação;
- múltiplas seleções;
- integração com portfólio.

---

### 47.3 BetLeg

BetLeg representa uma seleção individual dentro de uma aposta múltipla.

Ownership hierárquico:

```text
Bankroll
    └── Bet
            └── BetLeg
```

Regras:

- deverá pertencer a exatamente uma Bet;
- deverá referenciar mercado e seleção;
- deverá preservar odd registrada;
- deverá possuir resultado individual;
- não poderá existir sem Bet;
- alterações após confirmação deverão ser proibidas ou auditadas.

---

### 47.4 Settlement

Settlement representa a liquidação de uma aposta.

Ownership:

```text
Bankroll
    └── Bet
            └── Settlement
```

Regras:

- deverá pertencer a uma Bet;
- deverá registrar resultado;
- deverá registrar retorno;
- deverá registrar horário;
- deverá preservar regra aplicada;
- reliquidações deverão gerar novo histórico;
- a liquidação não deverá apagar o resultado anterior.

---

## 48. Matriz de Ownership

| Aggregate Root | Entidade interna | Tipo de ownership |
|---|---|---|
| Country | Region | Exclusivo |
| Country | City | Hierárquico |
| Competition | Stage | Exclusivo |
| Competition | Round | Hierárquico |
| Team | TeamMembership | Exclusivo |
| Team | SquadRegistration | Exclusivo |
| Person | Player | Exclusivo |
| Person | Coach | Exclusivo |
| Person | Referee | Exclusivo |
| Match | MatchParticipant | Exclusivo |
| Match | MatchVenue | Exclusivo |
| Match | MatchOfficial | Exclusivo |
| Match | MatchPeriod | Exclusivo |
| Match | MatchSquad | Exclusivo |
| Match | Lineup | Exclusivo |
| Match | LineupEntry | Hierárquico |
| Match | MatchEvent | Exclusivo |
| Match | MatchStatistic | Exclusivo |
| Match | MatchInterruption | Exclusivo |
| Match | MatchScheduleChange | Exclusivo |
| Match | MatchDecision | Exclusivo |
| Match | MatchRevision | Exclusivo |
| Tie | TieMatchReference | Exclusivo |
| Prediction | PredictionResult | Exclusivo |
| Prediction | PredictionExplanation | Exclusivo |
| Bankroll | BankrollTransaction | Exclusivo |
| Bankroll | Bet | Exclusivo inicial |
| Bankroll | BetLeg | Hierárquico |
| Bankroll | Settlement | Hierárquico |

---

## 49. Regras de Persistência

A persistência deverá respeitar as fronteiras de ownership.

### 49.1 Repository por Aggregate Root

A regra preferencial será criar repositories para Aggregate Roots.

Exemplos:

```text
CountryRepository
CompetitionRepository
TeamRepository
PersonRepository
MatchRepository
PredictionRepository
BankrollRepository
```

Entidades internas não deverão possuir repositories públicos independentes quando isso permitir contornar a raiz.

---

### 49.2 Carregamento do agregado

O repository deverá carregar os dados necessários para executar a operação de domínio.

Isso não significa que todas as coleções deverão ser carregadas integralmente em todas as consultas.

Poderão ser utilizadas:

- estratégias de carregamento específicas;
- consultas direcionadas;
- projeções;
- paginação;
- comandos especializados;
- persistência incremental controlada.

A otimização não deverá permitir a violação das invariantes.

---

### 49.3 Persistência de grandes coleções

Agregados como Match poderão possuir milhares de eventos ou estatísticas.

Nesses casos, a implementação poderá adotar estratégias específicas para evitar carregamento integral.

Entretanto:

- Match continuará sendo a fronteira conceitual;
- operações deverão validar a identidade da partida;
- regras críticas deverão permanecer centralizadas;
- gravações deverão ser idempotentes;
- entidades internas não deverão tornar-se independentes apenas por conveniência técnica.

---

## 50. Regras de Exclusão

### 50.1 Exclusão de entidades históricas

Entidades que representam fatos históricos não deverão ser removidas fisicamente após confirmação oficial, salvo em processos administrativos controlados.

Exemplos:

- MatchEvent;
- MatchScheduleChange;
- MatchDecision;
- MatchRevision;
- BankrollTransaction;
- PredictionResult;
- Settlement.

A estratégia preferencial será:

- cancelamento;
- anulação;
- substituição;
- revisão;
- inativação;
- registro compensatório.

---

### 50.2 Exclusão do Aggregate Root

A exclusão de um Aggregate Root deverá avaliar:

- referências externas;
- registros históricos;
- impacto analítico;
- auditoria;
- obrigações de retenção;
- possibilidade de anonimização;
- possibilidade de inativação.

Aggregate Roots relevantes deverão preferencialmente ser inativados em vez de removidos.

---

### 50.3 Cascade técnico e cascade de domínio

Cascade de banco de dados não deverá substituir decisões de domínio.

Uma configuração `ON DELETE CASCADE` poderá ser tecnicamente conveniente, mas somente deverá ser utilizada quando a remoção automática estiver alinhada às regras históricas e de auditoria.

---

## 51. Regras de Acesso

### 51.1 Escrita

A escrita em entidades internas deverá ocorrer através:

- do Aggregate Root;
- de Application Services;
- de Domain Services autorizados;
- de comandos de domínio;
- de processos internos idempotentes.

---

### 51.2 Leitura

A leitura poderá ocorrer através de:

- repositories;
- query services;
- read models;
- projeções;
- views;
- materialized views;
- caches;
- APIs de consulta.

A liberdade de leitura não implica liberdade de escrita.

---

### 51.3 Exposição por API

Schemas externos não deverão expor automaticamente toda a estrutura interna do agregado.

A API deverá apresentar apenas:

- dados necessários;
- comandos permitidos;
- identificadores estáveis;
- estados relevantes;
- erros de domínio compreensíveis.

---

## 52. Decisões desta Parte

As seguintes decisões passam a integrar a arquitetura oficial:

1. entidades internas possuem identidade, mas não ciclo de vida independente;
2. toda entidade interna possui exatamente um proprietário;
3. entidades internas deverão ser criadas e alteradas através do Aggregate Root;
4. referências externas não transferem ownership;
5. entidades históricas não deverão ser apagadas silenciosamente;
6. repositories públicos deverão ser preferencialmente criados por Aggregate Root;
7. otimizações técnicas não poderão eliminar as fronteiras conceituais;
8. snapshots poderão preservar informações históricas externas;
9. entidades internas não poderão pertencer a múltiplas raízes;
10. exclusões deverão respeitar histórico, auditoria e integridade.

---

## 53. Pontos para Revisão Antes do G5

Antes da implementação persistente, os seguintes pontos deverão ser revisitados:

- Season como Aggregate Root independente ou parte de Competition;
- Tie como Aggregate Root independente;
- estrutura definitiva de mercados e odds;
- Bookmaker como proprietário ou apenas referência de Odds;
- Bet como entidade interna ou Aggregate Root;
- estratégia de persistência de grandes coleções de Match;
- granularidade dos repositories;
- política de exclusão física;
- regras de snapshot;
- limites entre estatísticas oficiais e estatísticas derivadas.

Esses pontos não impedem o avanço da arquitetura, mas deverão ser resolvidos antes das migrations definitivas.

---

## 54. Resultado da G4.A.4.1 — Parte 3

Com a conclusão desta parte, ficam definidos:

- o conceito de entidade interna;
- o conceito de ownership;
- os tipos de ownership;
- as entidades internas de cada agregado;
- as regras de criação e alteração;
- as referências externas permitidas;
- as regras de persistência;
- as regras de exclusão;
- os limites de leitura e escrita;
- os principais pontos que exigirão revisão antes do G5.

A próxima parte concluirá a G4.A.4.1 com a definição dos Value Objects e das regras de identidade.

Serão documentados:

- objetos imutáveis;
- igualdade por valor;
- identificadores canônicos;
- identificadores externos;
- aliases;
- snapshots;
- regras de comparação;
- normalização de valores;
- critérios de criação de novos Value Objects.
---

# Parte IV — Value Objects e Regras de Identidade

## 55. Objetivo

Esta parte define os Value Objects do UltraStats AI e estabelece as regras de identidade aplicáveis às entidades canônicas, entidades internas, aliases, snapshots e identificadores externos.

Ao final desta parte deverá estar claramente definido:

- o que caracteriza um Value Object;
- quando um conceito deve ser modelado como Value Object;
- quais Value Objects serão utilizados no domínio;
- como ocorre a igualdade por valor;
- como ocorre a imutabilidade;
- como identificadores canônicos serão gerados;
- como identificadores externos serão armazenados;
- como aliases serão tratados;
- como snapshots preservarão contexto histórico;
- como duplicações de identidade serão evitadas.

---

## 56. Definição de Value Object

Um Value Object representa um conceito do domínio definido por seus valores e não por uma identidade própria.

Dois Value Objects serão considerados equivalentes quando todos os seus componentes relevantes forem equivalentes.

Exemplo:

```text
GeoCoordinate
    latitude: -21.7946
    longitude: -48.1756
```

Duas instâncias com os mesmos valores representam a mesma coordenada, independentemente de terem sido criadas em momentos diferentes.

Value Objects não deverão possuir identificadores canônicos próprios apenas para diferenciar instâncias equivalentes.

---

## 57. Características dos Value Objects

Os Value Objects deverão seguir as características descritas nesta seção.

### 57.1 Igualdade por valor

A comparação entre dois Value Objects deverá ocorrer por meio dos valores que os compõem.

Exemplo:

```text
Money(100.00, "BRL") == Money(100.00, "BRL")
```

O resultado deverá ser verdadeiro.

Por outro lado:

```text
Money(100.00, "BRL") != Money(100.00, "USD")
```

O resultado deverá ser verdadeiro, pois a moeda faz parte do valor.

---

### 57.2 Imutabilidade

Value Objects deverão ser preferencialmente imutáveis.

Quando um valor precisar mudar, uma nova instância deverá ser criada.

Exemplo conceitual:

```text
current_score = Score(home=1, away=0)

updated_score = Score(home=2, away=0)
```

O objeto anterior não deverá ser alterado internamente.

Essa regra facilita:

- previsibilidade;
- rastreabilidade;
- comparação;
- testes;
- concorrência;
- auditoria.

---

### 57.3 Validação na criação

Um Value Object deverá nascer em estado válido.

Exemplo:

```text
Probability(1.4)
```

deverá ser rejeitado, pois uma probabilidade não pode ser superior a `1`.

Da mesma forma:

```text
Percentage(-10)
```

deverá ser rejeitado quando o domínio não permitir percentuais negativos.

---

### 57.4 Ausência de ciclo de vida independente

Um Value Object não possui ciclo de vida próprio.

Ele existe como parte de:

- uma entidade;
- outro Value Object;
- um comando;
- um evento;
- um resultado de cálculo;
- um snapshot.

---

### 57.5 Comportamento próprio

Value Objects não devem ser tratados apenas como estruturas passivas de dados.

Eles poderão possuir métodos relacionados ao próprio conceito.

Exemplos:

```text
Money.add(...)
Money.subtract(...)
Probability.to_percentage(...)
Score.total_goals(...)
DateRange.contains(...)
GeoCoordinate.distance_to(...)
```

Esses comportamentos deverão preservar as invariantes do objeto.

---

## 58. Critérios para Criação de um Value Object

Um conceito deverá ser modelado como Value Object quando atender à maioria dos critérios a seguir:

- não possuir identidade própria;
- ser definido completamente por seus valores;
- exigir validação específica;
- possuir comportamento próprio;
- ser reutilizado em diferentes entidades;
- representar uma unidade semântica;
- ser naturalmente imutável;
- reduzir o uso de tipos primitivos sem significado.

Exemplo inadequado:

```text
probability: float
```

Exemplo preferencial:

```text
probability: Probability
```

O segundo formato expressa melhor o domínio e impede valores inválidos.

---

## 59. Primitive Obsession

O domínio deverá evitar o uso excessivo de tipos primitivos para representar conceitos relevantes.

Tipos como:

- `str`;
- `int`;
- `float`;
- `Decimal`;
- `datetime`;
- `tuple`;

não carregam significado suficiente quando utilizados isoladamente.

Exemplo:

```text
latitude: float
longitude: float
```

Esse formato permite combinações inválidas.

Uma alternativa mais segura será:

```text
location: GeoCoordinate
```

O Value Object poderá validar limites, precisão e ausência de valores incompatíveis.

---

# 60. Catálogo Inicial de Value Objects

Os Value Objects descritos nesta seção formam o catálogo inicial do UltraStats AI.

O catálogo poderá ser expandido durante a implementação, desde que novos objetos respeitem os critérios arquiteturais definidos.

---

## 61. CanonicalId

### Finalidade

Representar o identificador canônico interno de uma entidade.

Estrutura conceitual:

```text
CanonicalId
    value
```

Regras:

- deverá ser único;
- deverá ser imutável;
- não deverá depender de provider;
- não deverá carregar significado de negócio mutável;
- deverá possuir representação estável;
- deverá ser validado na criação.

O tipo concreto poderá utilizar UUID, desde que a decisão permaneça consistente em todo o domínio.

---

## 62. ExternalIdentifier

### Finalidade

Representar um identificador atribuído por um provider externo.

Estrutura conceitual:

```text
ExternalIdentifier
    provider_id
    entity_type
    external_value
```

Regras:

- deverá identificar o provider de origem;
- deverá identificar o tipo da entidade;
- deverá preservar o valor original;
- deverá ser único dentro do escopo do provider e tipo;
- não deverá ser utilizado como identidade canônica;
- deverá permitir rastreabilidade até o payload de origem.

Exemplo:

```text
provider_id: football_data_org
entity_type: team
external_value: "64"
```

---

## 63. EntityReference

### Finalidade

Representar uma referência canônica entre agregados.

Estrutura conceitual:

```text
EntityReference
    entity_type
    canonical_id
```

Regras:

- deverá apontar para um Aggregate Root válido;
- não deverá carregar estado mutável da entidade;
- poderá ser usada em comandos, eventos e snapshots;
- não transfere ownership;
- deverá ser comparável por tipo e identificador.

---

## 64. EntityAlias

### Finalidade

Representar um nome alternativo ou representação textual associada a uma entidade canônica.

Estrutura conceitual:

```text
EntityAlias
    value
    language
    alias_type
    provider_id
    valid_from
    valid_until
```

Possíveis tipos:

- nome abreviado;
- nome histórico;
- nome comercial;
- nome transliterado;
- nome fornecido por provider;
- sigla;
- apelido esportivo.

Regras:

- deverá preservar o valor original;
- poderá ser normalizado para comparação;
- deverá possuir contexto de origem;
- não deverá substituir silenciosamente o nome oficial;
- aliases duplicados deverão ser evitados dentro do mesmo escopo;
- aliases históricos deverão preservar vigência quando conhecida.

---

## 65. NormalizedName

### Finalidade

Representar uma versão normalizada de nome utilizada para busca, comparação e resolução de identidade.

Estrutura conceitual:

```text
NormalizedName
    original
    normalized
```

A normalização poderá considerar:

- caixa;
- acentuação;
- pontuação;
- espaços;
- abreviações;
- caracteres especiais;
- transliteração.

Regras:

- o valor original deverá ser preservado;
- a normalização deverá ser determinística;
- alterações no algoritmo deverão ser versionadas;
- o nome normalizado não deverá substituir o nome oficial;
- igualdade de nome normalizado não garante igualdade de entidade.

---

## 66. LocalizedName

### Finalidade

Representar um nome em determinado idioma ou localidade.

Estrutura conceitual:

```text
LocalizedName
    value
    language_code
    country_code
```

Regras:

- o idioma deverá utilizar código padronizado;
- o país poderá ser opcional;
- valores vazios não serão permitidos;
- múltiplas traduções poderão coexistir;
- deverá ser preservada a distinção entre tradução e alias.

---

## 67. GeoCoordinate

### Finalidade

Representar uma coordenada geográfica.

Estrutura conceitual:

```text
GeoCoordinate
    latitude
    longitude
```

Regras:

- latitude entre `-90` e `90`;
- longitude entre `-180` e `180`;
- precisão deverá ser controlada;
- coordenadas incompletas não serão permitidas;
- o objeto poderá calcular distância aproximada;
- a ausência de localização deverá ser representada por valor nulo e não por coordenadas artificiais.

---

## 68. Address

### Finalidade

Representar um endereço estruturado.

Estrutura conceitual:

```text
Address
    street
    number
    complement
    district
    postal_code
    city_id
    region_id
    country_id
```

Regras:

- campos obrigatórios dependerão do contexto;
- códigos postais deverão preservar o formato original;
- referências geográficas deverão ser coerentes;
- o endereço poderá ser parcial;
- campos não disponíveis não deverão receber valores artificiais;
- snapshots de endereço poderão ser preservados em eventos históricos.

---

## 69. DateRange

### Finalidade

Representar um período delimitado por datas.

Estrutura conceitual:

```text
DateRange
    start_date
    end_date
```

Regras:

- `start_date` deverá ser anterior ou igual a `end_date`;
- `end_date` poderá ser opcional para períodos abertos;
- o objeto poderá verificar sobreposição;
- o objeto poderá verificar contenção;
- limites deverão possuir semântica explícita;
- intervalos históricos não deverão ser alterados sem auditoria.

---

## 70. DateTimeRange

### Finalidade

Representar um intervalo de data e hora.

Estrutura conceitual:

```text
DateTimeRange
    start_at
    end_at
    timezone
```

Regras:

- `start_at` deverá ser anterior ou igual a `end_at`;
- timezone deverá ser explícito;
- armazenamento deverá preferencialmente utilizar UTC;
- exibição poderá utilizar timezone local;
- intervalos abertos poderão ser permitidos;
- horários ambíguos deverão ser tratados de forma explícita.

---

## 71. SeasonPeriod

### Finalidade

Representar o período oficial de uma temporada.

Estrutura conceitual:

```text
SeasonPeriod
    start_date
    end_date
```

Regras:

- deverá formar intervalo válido;
- poderá cruzar anos civis;
- não deverá presumir formato anual;
- deverá permitir temporadas curtas ou especiais;
- sobreposição entre temporadas dependerá da competição.

---

## 72. MatchClock

### Finalidade

Representar o tempo esportivo de um evento dentro da partida.

Estrutura conceitual:

```text
MatchClock
    period
    minute
    second
    added_minute
```

Regras:

- valores negativos não serão permitidos;
- o período deverá existir na partida;
- acréscimo deverá ser representado separadamente;
- o tempo esportivo não deverá ser confundido com timestamp de coleta;
- o objeto poderá fornecer representação textual como `90+4`.

---

## 73. Score

### Finalidade

Representar um placar entre dois participantes.

Estrutura conceitual:

```text
Score
    home
    away
```

Regras:

- valores não poderão ser negativos;
- deverá utilizar números inteiros;
- poderá representar placar parcial ou final;
- o contexto deverá indicar o tipo do placar;
- o objeto poderá calcular total de gols;
- o objeto poderá identificar vencedor ou empate;
- placares administrativos deverão manter origem explícita.

---

## 74. AggregateScore

### Finalidade

Representar o placar agregado de um confronto com múltiplas partidas.

Estrutura conceitual:

```text
AggregateScore
    participant_a
    participant_b
```

Regras:

- valores não poderão ser negativos;
- deverá ser derivável das partidas oficiais sempre que possível;
- critérios como gols fora não deverão ser embutidos no valor;
- o vencedor poderá depender de Domain Policy;
- o objeto poderá representar igualdade sem decidir classificação.

---

## 75. PenaltyScore

### Finalidade

Representar o resultado de uma disputa de pênaltis.

Estrutura conceitual:

```text
PenaltyScore
    participant_a
    participant_b
```

Regras:

- deverá ser tratado separadamente do placar regulamentar;
- valores não poderão ser negativos;
- deverá estar associado a uma decisão ou período válido;
- não deverá ser somado automaticamente ao placar oficial.

---

## 76. FormationCode

### Finalidade

Representar uma formação tática.

Exemplos:

```text
4-3-3
4-2-3-1
3-5-2
```

Regras:

- deverá possuir formato válido;
- a soma dos jogadores de linha deverá ser coerente;
- o goleiro poderá ser implícito;
- formações incomuns deverão ser permitidas quando válidas;
- o valor original do provider poderá ser preservado separadamente.

---

## 77. ShirtNumber

### Finalidade

Representar o número de camisa de uma pessoa em determinado contexto.

Estrutura conceitual:

```text
ShirtNumber
    value
```

Regras:

- deverá utilizar número inteiro positivo;
- os limites poderão variar por competição;
- poderá ser temporário;
- não deverá fazer parte da identidade da pessoa;
- duplicações deverão ser avaliadas dentro do contexto apropriado.

---

## 78. FieldPosition

### Finalidade

Representar uma posição ou função em campo.

Estrutura conceitual:

```text
FieldPosition
    category
    role
    side
```

Exemplos:

```text
goalkeeper
center_back
left_back
defensive_midfielder
right_winger
center_forward
```

Regras:

- deverá utilizar vocabulário canônico;
- valores de providers deverão ser normalizados;
- posição principal e posição na partida poderão ser diferentes;
- o objeto poderá preservar nível de detalhe variável.

---

## 79. Probability

### Finalidade

Representar uma probabilidade matemática.

Estrutura conceitual:

```text
Probability
    value
```

Regras:

- valor entre `0` e `1`;
- precisão deverá ser controlada;
- cálculos deverão evitar erros de ponto flutuante;
- poderá ser convertido em percentual;
- não deverá aceitar valores ausentes como zero;
- probabilidades complementares deverão respeitar tolerância definida.

---

## 80. Percentage

### Finalidade

Representar um percentual.

Estrutura conceitual:

```text
Percentage
    value
```

Regras:

- limites dependerão do contexto;
- o padrão será entre `0` e `100`;
- percentuais acima de `100` somente serão permitidos em conceitos específicos;
- deverá preservar precisão;
- não deverá ser confundido com Probability.

---

## 81. DecimalOdd

### Finalidade

Representar uma odd decimal.

Estrutura conceitual:

```text
DecimalOdd
    value
```

Regras:

- deverá ser maior que `1` para odds comuns;
- odds especiais poderão exigir política própria;
- deverá utilizar Decimal;
- deverá preservar a precisão coletada;
- poderá calcular probabilidade implícita;
- não deverá ser alterada após o registro histórico.

---

## 82. Money

### Finalidade

Representar um valor monetário.

Estrutura conceitual:

```text
Money
    amount
    currency
```

Regras:

- deverá utilizar Decimal;
- moeda deverá ser explícita;
- operações entre moedas diferentes deverão ser bloqueadas sem conversão;
- precisão deverá respeitar a moeda;
- arredondamento deverá utilizar regra definida;
- valores negativos dependerão do contexto.

---

## 83. Stake

### Finalidade

Representar o valor financeiro arriscado em uma aposta.

Estrutura conceitual:

```text
Stake
    money
```

Regras:

- deverá ser maior que zero;
- deverá possuir moeda compatível com a Bankroll;
- deverá respeitar limites configurados;
- não deverá exceder o saldo disponível quando essa regra estiver ativa.

---

## 84. ExpectedValue

### Finalidade

Representar o valor esperado de uma oportunidade.

Estrutura conceitual:

```text
ExpectedValue
    value
```

Regras:

- poderá ser positivo, negativo ou zero;
- deverá registrar fórmula ou versão de cálculo;
- deverá usar Probability e DecimalOdd;
- precisão deverá ser controlada;
- não deverá ser tratado como garantia de retorno.

---

## 85. ConfidenceScore

### Finalidade

Representar o grau de confiança de uma decisão ou correspondência.

Estrutura conceitual:

```text
ConfidenceScore
    value
```

Regras:

- valor entre `0` e `1`;
- deverá possuir interpretação definida por contexto;
- não deverá ser comparado entre algoritmos diferentes sem calibração;
- limiares deverão ser configuráveis;
- a versão do algoritmo deverá ser preservada.

---

## 86. OpportunityScore

### Finalidade

Representar a classificação consolidada de uma oportunidade de aposta.

Estrutura conceitual:

```text
OpportunityScore
    value
    version
```

Regras:

- escala deverá ser documentada;
- cálculo deverá ser versionado;
- deverá combinar apenas fatores definidos;
- não deverá ocultar os componentes utilizados;
- alterações no cálculo deverão gerar nova versão.

---

## 87. SampleQuality

### Finalidade

Representar a confiabilidade estatística de uma amostra.

Estrutura conceitual:

```text
SampleQuality
    score
    sample_size
    completeness
    recency
```

Regras:

- deverá registrar fatores principais;
- não deverá ser reduzida apenas ao tamanho da amostra;
- critérios deverão ser versionados;
- poderá bloquear ou reduzir confiança de previsões;
- deverá ser explicável.

---

## 88. ModelVersion

### Finalidade

Representar uma versão imutável de modelo preditivo.

Estrutura conceitual:

```text
ModelVersion
    model_name
    version
    artifact_hash
```

Regras:

- deverá identificar unicamente o artefato;
- não poderá ser reutilizada para modelos diferentes;
- alterações exigem nova versão;
- deverá permitir rastrear treinamento e inferência;
- deverá preservar hash do artefato.

---

## 89. DataProvenance

### Finalidade

Representar a origem de um dado.

Estrutura conceitual:

```text
DataProvenance
    provider_id
    payload_id
    collected_at
    processed_at
    rule_version
```

Regras:

- deverá apontar para origem rastreável;
- poderá representar origem manual;
- deverá preservar versão da regra aplicada;
- não deverá ser alterada silenciosamente;
- múltiplas proveniências poderão coexistir para o mesmo campo.

---

## 90. EntitySnapshot

### Finalidade

Preservar uma representação histórica de uma entidade externa ao agregado.

Estrutura conceitual:

```text
EntitySnapshot
    entity_id
    display_name
    relevant_attributes
    captured_at
```

Regras:

- deverá preservar apenas os dados relevantes ao contexto;
- não substituirá a referência canônica;
- deverá ser imutável;
- deverá registrar quando foi capturado;
- não deverá ser atualizado quando a entidade original mudar.

---

# 91. Regras de Identidade Canônica

## 91.1 Identidade independente de provider

Toda entidade canônica deverá possuir identidade própria gerada pelo UltraStats AI.

Exemplo:

```text
Team
    id: canonical_uuid

ExternalIdentifier
    provider: football_data_org
    external_value: 64
```

O identificador `64` não deverá ser usado como `Team.id`.

---

## 91.2 Identidade estável

A identidade canônica deverá permanecer estável ao longo do tempo.

Alterações em:

- nome;
- estádio;
- escudo;
- país;
- treinador;
- competição;
- provider;
- status;

não deverão gerar automaticamente uma nova identidade.

---

## 91.3 Identidade sem significado mutável

Identificadores canônicos não deverão incorporar informações mutáveis.

Exemplo inadequado:

```text
team_id = "BRA-SP-PALMEIRAS"
```

Esse identificador depende de nome e localização.

Exemplo preferencial:

```text
team_id = UUID
```

Nomes, códigos e localizações permanecem como atributos.

---

## 91.4 Identidade por entidade

Cada entidade canônica deverá possuir exatamente uma identidade principal.

Especializações não deverão gerar identidades paralelas quando representam a mesma entidade.

Exemplo:

```text
Person
    id: person_id

Player
    person_id: person_id
```

Player reutiliza a identidade da Person.

---

## 91.5 Identidade interna

Entidades internas poderão possuir identificador próprio para persistência e auditoria.

Exemplo:

```text
MatchEvent
    id
    match_id
```

A identidade do MatchEvent será válida apenas dentro de sua fronteira conceitual.

Mesmo possuindo `id`, MatchEvent não se torna Aggregate Root.

---

## 91.6 Identidade temporal

Determinadas entidades representam uma relação em certo período.

Exemplo:

```text
TeamMembership
    team_id
    person_id
    valid_from
    valid_until
```

A combinação dos valores poderá participar de constraints de unicidade, mas a entidade ainda poderá possuir identificador próprio para auditoria.

---

# 92. Estratégia de Identificadores

## 92.1 UUID como padrão

A estratégia preferencial será utilizar UUID para identidades canônicas.

Vantagens:

- geração distribuída;
- independência do banco;
- menor risco de colisão entre ambientes;
- ausência de informação de negócio;
- facilidade de sincronização;
- menor acoplamento com providers.

A versão concreta do UUID deverá ser definida antes do G5.

---

## 92.2 Identificadores sequenciais

Identificadores sequenciais poderão ser utilizados internamente em tabelas de grande volume quando houver justificativa técnica.

Entretanto, o uso de identificador sequencial deverá avaliar:

- exposição pública;
- previsibilidade;
- replicação;
- fusão entre ambientes;
- migração de dados;
- desempenho.

Quando necessário, uma entidade poderá possuir:

- identificador técnico sequencial;
- identificador canônico UUID.

Essa duplicidade somente deverá ser adotada com justificativa clara.

---

## 92.3 Identificadores públicos

Identificadores expostos em APIs ou URLs poderão utilizar:

- UUID;
- identificador codificado;
- slug estável;
- chave pública específica.

Slugs não deverão substituir identidades canônicas.

---

## 92.4 IDs de eventos de integração

Eventos de integração deverão possuir identificador próprio.

Exemplo:

```text
event_id
event_type
aggregate_id
occurred_at
```

O `event_id` será utilizado para:

- idempotência;
- rastreabilidade;
- deduplicação;
- reprocessamento.

---

# 93. Regras de Identificadores Externos

## 93.1 Escopo composto

Um identificador externo somente será único dentro do conjunto:

```text
provider
entity_type
external_value
```

O valor `64` poderá identificar entidades diferentes em providers distintos.

---

## 93.2 Preservação do valor original

O valor externo deverá ser armazenado sem perda de informação.

Caso o provider utilize string, não deverá ser convertido automaticamente para inteiro.

Exemplo:

```text
"00064"
```

não deverá ser transformado em:

```text
64
```

quando os zeros fizerem parte do identificador original.

---

## 93.3 Histórico de mapeamento

Alterações de mapeamento deverão preservar histórico.

Exemplo:

```text
ExternalIdentifier X
    previously mapped to Team A
    corrected to Team B
```

A correção deverá registrar:

- valor anterior;
- novo valor;
- motivo;
- autor;
- data;
- evidência.

---

## 93.4 Um externo para um canônico

Como regra geral, um ExternalIdentifier ativo deverá apontar para uma única entidade canônica.

Exceções deverão ser tratadas explicitamente.

---

## 93.5 Múltiplos externos para um canônico

Uma entidade canônica poderá possuir vários identificadores externos.

Exemplo:

```text
Team A
    Football-Data.org: 64
    Provider B: "palmeiras"
    Provider C: 9921
```

Todos representam a mesma equipe canônica.

---

# 94. Regras de Aliases

## 94.1 Alias não cria identidade

Um alias não deverá criar uma nova entidade automaticamente.

Exemplo:

```text
Manchester United
Man United
Manchester Utd
```

Esses valores poderão representar a mesma entidade.

---

## 94.2 Alias ambíguo

Um mesmo alias poderá estar relacionado a múltiplas entidades.

Exemplo:

```text
United
```

A resolução não poderá utilizar apenas igualdade textual.

Deverão ser considerados:

- país;
- competição;
- período;
- tipo da entidade;
- provider;
- relações conhecidas;
- contexto do payload.

---

## 94.3 Normalização de alias

Aliases poderão possuir versões normalizadas para matching.

Exemplo:

```text
São Paulo FC
sao paulo fc
```

A normalização não deverá apagar o valor original.

---

## 94.4 Alias histórico

Nomes históricos deverão possuir vigência quando possível.

Exemplo:

```text
official_name
valid_from
valid_until
```

A ausência de vigência não deverá impedir o armazenamento, mas reduzirá a confiança em processos automáticos.

---

## 94.5 Alias de provider

Aliases provenientes de providers deverão registrar origem.

Eles não deverão ser promovidos automaticamente a nome oficial.

---

# 95. Regras de Snapshots

## 95.1 Finalidade histórica

Snapshots serão utilizados quando o estado histórico de uma entidade externa precisar ser preservado.

Exemplo:

Uma partida poderá preservar o nome exibido da equipe no momento do jogo, mesmo que a equipe seja renomeada posteriormente.

---

## 95.2 Snapshot mínimo

O snapshot deverá conter apenas os atributos necessários ao contexto histórico.

Ele não deverá copiar toda a entidade externa.

---

## 95.3 Imutabilidade

Snapshots deverão ser imutáveis.

Alterações na entidade original não deverão alterar snapshots existentes.

---

## 95.4 Referência conjunta

Sempre que possível, o snapshot deverá manter:

```text
canonical_id
captured_values
captured_at
```

Assim, o sistema preserva simultaneamente:

- identidade atual;
- representação histórica.

---

# 96. Regras de Igualdade

## 96.1 Entidades

Entidades serão comparadas por identidade.

Exemplo:

```text
Team(id=A, name="Name 1")
Team(id=A, name="Name 2")
```

Representam a mesma entidade, mesmo com nomes diferentes.

---

## 96.2 Value Objects

Value Objects serão comparados por seus componentes.

Exemplo:

```text
GeoCoordinate(-21.1, -48.2)
GeoCoordinate(-21.1, -48.2)
```

Representam o mesmo valor.

---

## 96.3 Snapshots

Snapshots deverão ser comparados pelo conjunto:

- entidade referenciada;
- instante de captura;
- valores capturados.

Dois snapshots iguais em conteúdo, mas capturados em momentos diferentes, poderão representar registros históricos distintos.

---

# 97. Regras de Normalização

## 97.1 Normalização não destrutiva

Toda normalização deverá preservar o valor original.

Exemplo:

```text
original: "  São   Paulo F.C. "
normalized: "sao paulo fc"
```

---

## 97.2 Algoritmo versionado

Algoritmos de normalização deverão possuir versão.

Mudanças poderão alterar resultados de matching.

Exemplo:

```text
normalization_version: 2
```

---

## 97.3 Normalização específica por tipo

Diferentes tipos de entidade poderão utilizar regras diferentes.

Exemplos:

- nomes de pessoas;
- nomes de equipes;
- nomes de estádios;
- códigos de competição;
- nomes de cidades.

Não deverá existir uma única função genérica aplicada indiscriminadamente.

---

## 97.4 Normalização cultural

A normalização deverá considerar diferenças linguísticas e culturais.

Exemplos:

- acentuação;
- transliteração;
- partículas de sobrenome;
- abreviações esportivas;
- sufixos jurídicos de clubes;
- nomes históricos.

---

# 98. Regras de Criação de Novos Value Objects

Antes de criar um novo Value Object, deverá ser avaliado:

1. o conceito possui significado próprio no domínio?
2. possui regras de validação?
3. possui comportamento?
4. aparece em mais de uma entidade?
5. tipos primitivos permitiriam estados inválidos?
6. a igualdade é baseada em valor?
7. o conceito é imutável?
8. o nome melhora a clareza do modelo?

Um Value Object não deverá ser criado apenas para envolver um único campo sem ganho semântico.

---

# 99. Persistência de Value Objects

Value Objects poderão ser persistidos de diferentes formas:

- colunas embutidas;
- composite types;
- JSON estruturado;
- tabelas auxiliares;
- tipos customizados;
- serialização específica.

A estratégia concreta dependerá de:

- frequência de consulta;
- necessidade de índices;
- volume;
- portabilidade;
- suporte do ORM;
- necessidade de constraints.

A persistência não deverá alterar a semântica do objeto.

---

# 100. Serialização

Value Objects expostos por APIs deverão possuir serialização estável.

Exemplo:

```json
{
  "amount": "150.00",
  "currency": "BRL"
}
```

A serialização deverá:

- evitar perda de precisão;
- preservar timezone;
- preservar códigos;
- utilizar formatos documentados;
- ser compatível com versionamento.

---

# 101. Decisões desta Parte

As seguintes decisões passam a integrar a arquitetura oficial do UltraStats AI:

1. Value Objects serão definidos por valor e não por identidade.
2. Value Objects serão preferencialmente imutáveis.
3. Value Objects deverão nascer válidos.
4. Conceitos relevantes não deverão ser representados apenas por tipos primitivos.
5. Identidades canônicas serão independentes de providers.
6. UUID será a estratégia preferencial para IDs canônicos.
7. Identificadores externos serão armazenados separadamente.
8. Aliases não criarão identidades automaticamente.
9. Normalizações preservarão o valor original.
10. Snapshots serão utilizados para preservar contexto histórico.
11. Entidades serão comparadas por identidade.
12. Value Objects serão comparados por valor.
13. Algoritmos de normalização deverão ser versionados.
14. Especializações reutilizarão a identidade da entidade principal.
15. A persistência não poderá alterar a semântica dos Value Objects.

---

# 102. Pontos para Revisão Antes do G5

Antes da implementação persistente, deverão ser confirmados:

- versão de UUID adotada;
- uso de UUID nativo no PostgreSQL;
- necessidade de identificadores técnicos sequenciais;
- estratégia de composite types no SQLAlchemy;
- precisão de Probability;
- precisão de DecimalOdd;
- precisão de Money;
- política de arredondamento;
- representação de timezone;
- catálogo inicial de moedas;
- estratégia de normalização textual;
- versionamento dos algoritmos;
- persistência de snapshots;
- constraints de ExternalIdentifier;
- índices de aliases normalizados.

---

# 103. Resultado da G4.A.4.1 — Parte 4

Com a conclusão desta parte, ficam definidos:

- o conceito de Value Object;
- os critérios para criação de Value Objects;
- o catálogo inicial de objetos de valor;
- as regras de igualdade;
- as regras de imutabilidade;
- a estratégia de identidade canônica;
- a estratégia de identificadores externos;
- as regras de aliases;
- as regras de snapshots;
- as regras de normalização;
- as diretrizes de persistência e serialização.

---

# 104. Conclusão da G4.A.4.1

A subetapa G4.A.4.1 — Agregados, Bounded Contexts e Value Objects está concluída.

Foram definidos:

- os Bounded Contexts do UltraStats AI;
- as responsabilidades de cada contexto;
- os Aggregate Roots;
- as fronteiras dos agregados;
- as entidades internas;
- as regras de ownership;
- os Value Objects;
- as regras de identidade;
- as regras de aliases;
- as regras de snapshots;
- as regras de normalização.

A próxima subetapa será:

```text
G4.A.4.2 — Regras de Consistência, Serviços, Políticas e Eventos de Domínio
```

Essa subetapa definirá:

- invariantes;
- regras de consistência;
- consistência forte;
- consistência eventual;
- Domain Services;
- Domain Policies;
- Domain Events;
- Integration Events;
- comandos;
- fluxos de alteração;
- validações entre agregados;
- tratamento de falhas de domínio.
---

# Parte V — Regras de Consistência, Serviços, Políticas e Eventos de Domínio

## 105. Objetivo da G4.A.4.2

Esta parte define como o UltraStats AI preservará a consistência do domínio durante operações de criação, alteração, integração, processamento estatístico e geração de previsões.

Ao final desta subetapa deverão estar definidos:

- invariantes dos agregados;
- regras de consistência forte;
- regras de consistência eventual;
- validações internas e externas;
- responsabilidades dos Domain Services;
- responsabilidades das Domain Policies;
- comandos de domínio;
- Domain Events;
- Integration Events;
- fluxos de escrita;
- tratamento de falhas;
- idempotência;
- reprocessamento;
- compensações;
- limites entre domínio e aplicação.

---

## 106. Consistência do Domínio

Consistência representa a garantia de que o estado do sistema respeita as regras de negócio definidas.

Um estado será considerado consistente quando:

- entidades obrigatórias existirem;
- relacionamentos forem válidos;
- valores respeitarem limites;
- identidades não forem duplicadas;
- ciclos de vida forem respeitados;
- transições de estado forem permitidas;
- históricos forem preservados;
- operações concorrentes não produzirem resultados incompatíveis;
- dados derivados puderem ser rastreados até suas fontes.

A consistência do domínio não deverá depender exclusivamente do banco de dados.

Ela deverá ser preservada por uma combinação de:

- Value Objects;
- entidades;
- Aggregate Roots;
- Domain Services;
- Domain Policies;
- Application Services;
- constraints;
- transações;
- eventos;
- processos de reconciliação.

---

## 107. Invariantes

Uma invariante é uma regra que deverá permanecer verdadeira durante todo o ciclo de vida de um agregado.

Uma operação somente poderá ser confirmada quando todas as invariantes relevantes estiverem satisfeitas.

Exemplos:

```text
Uma partida não pode possuir a mesma equipe como mandante e visitante.

Uma probabilidade não pode ser menor que zero ou maior que um.

Uma odd histórica confirmada não pode ser sobrescrita.

Uma aposta não pode ser liquidada antes de ser confirmada.

Um evento de partida não pode referenciar uma pessoa sem relação válida com a partida.
```

As invariantes deverão ser protegidas dentro da fronteira do agregado sempre que dependerem apenas de seu próprio estado.

---

## 108. Classificação das Regras

As regras do domínio serão classificadas em cinco grupos.

| Tipo | Responsabilidade |
|---|---|
| Regra de Value Object | Garante validade de um valor isolado. |
| Regra de entidade | Garante validade do estado de uma entidade. |
| Invariante de agregado | Garante consistência entre entidades do mesmo agregado. |
| Domain Policy | Define regra variável ou estratégia de negócio. |
| Domain Service | Executa operação envolvendo múltiplos conceitos ou agregados. |

Essa classificação deverá evitar a concentração de toda a lógica em services genéricos.

---

## 109. Regras de Value Objects

Value Objects deverão rejeitar estados inválidos no momento de sua criação.

Exemplos:

```text
Probability
    0 <= value <= 1

GeoCoordinate
    -90 <= latitude <= 90
    -180 <= longitude <= 180

Money
    currency obrigatória
    precisão compatível

DateRange
    start_date <= end_date
```

Uma entidade não deverá receber um Value Object inválido.

---

## 110. Regras de Entidade

Uma entidade será responsável por regras relacionadas ao próprio estado, desde que não dependam de outras entidades do agregado.

Exemplos:

- MatchEvent valida seu tipo;
- MatchScheduleChange valida os valores anterior e posterior;
- BankrollTransaction valida seu tipo e valor;
- ExternalIdentifier valida provider, tipo e valor externo;
- PredictionResult valida probabilidade e seleção.

Uma entidade não deverá validar regras que dependam de todo o agregado sem acesso à raiz.

---

## 111. Regras do Aggregate Root

O Aggregate Root deverá controlar regras que envolvam múltiplas entidades internas.

Exemplos do Match Aggregate:

- impedir participantes duplicados;
- impedir papéis incompatíveis;
- impedir duas escalações oficiais vigentes para a mesma equipe;
- validar que um jogador pertence ao lado correto;
- validar que um evento referencia um período existente;
- validar coerência entre eventos e placar;
- validar transições de status;
- registrar revisão quando um fato oficial for alterado.

Exemplos do Bankroll Aggregate:

- impedir stake inválida;
- validar moeda;
- validar saldo;
- controlar liquidação;
- impedir duplicação de movimentação;
- manter saldo coerente com transações.

---

# 112. Consistência Forte

## 112.1 Definição

Consistência forte será exigida quando uma operação não puder ser considerada concluída enquanto todas as regras críticas do agregado não forem validadas e persistidas.

A operação deverá ser confirmada como uma única unidade transacional.

---

## 112.2 Casos de consistência forte

A consistência forte deverá ser utilizada principalmente em:

- criação de Aggregate Roots;
- alteração de estado oficial;
- atualização de entidades internas;
- movimentações financeiras;
- confirmação de apostas;
- liquidação;
- resolução manual de identidade;
- alteração de participante de partida;
- correção de placar oficial;
- publicação de previsão;
- registro de decisão oficial.

---

## 112.3 Limite da consistência forte

A consistência forte deverá permanecer preferencialmente dentro de um único agregado.

Exemplo:

```text
Match
    ↓
validar participantes
    ↓
validar estado
    ↓
registrar alteração
    ↓
criar revisão
    ↓
persistir Match
```

Todas essas ações poderão ocorrer na mesma transação por pertencerem ao mesmo agregado.

---

## 112.4 Operações entre agregados

Operações que envolvam múltiplos agregados não deverão criar transações distribuídas por padrão.

A estratégia preferencial será:

```text
Agregado A confirma operação
    ↓
publica evento
    ↓
Agregado B processa evento
    ↓
Agregado B confirma sua própria operação
```

---

# 113. Consistência Eventual

## 113.1 Definição

Consistência eventual significa que diferentes partes do sistema poderão ser atualizadas em momentos distintos, desde que o sistema possua mecanismos para convergir para o estado correto.

Essa estratégia será utilizada quando:

- a operação atravessar contextos;
- o processamento for derivado;
- houver grande volume;
- houver dependência de serviços externos;
- a atualização imediata não for obrigatória;
- o processamento puder ser repetido.

---

## 113.2 Casos de consistência eventual

Exemplos:

- recalcular estatísticas após término de partida;
- gerar features;
- atualizar projeções;
- executar previsões;
- recalcular recomendações;
- atualizar dashboards;
- invalidar cache;
- enviar notificações;
- sincronizar dados de providers;
- recalcular placar agregado de Tie;
- atualizar ranking;
- atualizar performance de modelo.

---

## 113.3 Exemplo de fluxo eventual

```text
Match finalizado
    ↓
MatchFinished publicado
    ↓
Statistics processa
    ↓
StatisticsUpdated publicado
    ↓
Prediction processa
    ↓
PredictionPublished publicado
    ↓
Recommendation processa
```

Uma falha em Recommendation não deverá desfazer a finalização do Match.

---

## 113.4 Estado de processamento

Processos de consistência eventual deverão registrar:

- status;
- tentativas;
- horário da última tentativa;
- erro;
- próximo retry;
- payload ou referência;
- versão do consumidor;
- resultado;
- chave de idempotência.

---

# 114. Validações Internas e Externas

## 114.1 Validação interna

Validação interna depende apenas do estado do agregado.

Exemplo:

```text
Match.add_participant(team_id)
```

O Match poderá verificar se já existe participante com o mesmo papel.

---

## 114.2 Validação externa

Validação externa depende de informações pertencentes a outro agregado ou contexto.

Exemplo:

- verificar se Team existe;
- verificar se Person possui perfil de jogador;
- verificar se Stadium está ativo;
- verificar se Competition permite determinada formação;
- verificar se Bankroll utiliza a moeda da Stake.

Validações externas deverão ocorrer antes da confirmação da operação, através de contratos explícitos.

---

## 114.3 Validação externa não transfere responsabilidade

O fato de Match consultar Team não permite que Match altere Team.

A validação externa apenas confirma uma pré-condição.

---

## 114.4 Falha entre validação e persistência

Quando existir intervalo entre validação externa e persistência, o sistema deverá avaliar:

- risco de alteração concorrente;
- necessidade de versionamento;
- uso de snapshot;
- consistência eventual;
- repetição da validação;
- compensação.

---

# 115. Domain Services

## 115.1 Definição

Domain Service representa uma operação de negócio que não pertence naturalmente a uma única entidade ou Value Object.

Um Domain Service deverá:

- representar uma ação real do domínio;
- utilizar linguagem de negócio;
- evitar dependência de infraestrutura;
- receber objetos de domínio;
- devolver resultados de domínio;
- não funcionar como agrupador genérico de funções.

---

## 115.2 Quando utilizar

Domain Services deverão ser utilizados quando:

- a regra envolver múltiplos agregados;
- a operação não possuir proprietário natural;
- o cálculo representar conceito relevante;
- a decisão depender de política;
- a lógica precisar ser reutilizada;
- a operação for mais importante que os dados manipulados.

---

## 115.3 Quando não utilizar

Não deverá ser criado Domain Service para:

- getters;
- setters;
- formatação;
- consultas simples;
- acesso ao banco;
- serialização;
- chamadas HTTP;
- validação pertencente a Value Object;
- regra pertencente claramente a um Aggregate Root.

---

# 116. Catálogo Inicial de Domain Services

## 116.1 IdentityResolutionService

Responsável por relacionar representações externas a entidades canônicas.

Operações conceituais:

```text
generate_candidates(...)
calculate_match_score(...)
resolve_automatically(...)
request_manual_review(...)
apply_resolution(...)
```

O serviço deverá considerar:

- nome normalizado;
- aliases;
- país;
- competição;
- período;
- relações conhecidas;
- identificadores externos;
- confiança;
- evidências.

---

## 116.2 DataFusionService

Responsável por comparar dados concorrentes provenientes de múltiplos providers.

Operações:

```text
collect_candidates(...)
compare_values(...)
apply_provider_priority(...)
detect_conflict(...)
propose_canonical_update(...)
```

O serviço não deverá gravar diretamente no agregado proprietário sem utilizar seu contrato de escrita.

---

## 116.3 MatchResultService

Responsável por determinar o resultado esportivo a partir de:

- placar regulamentar;
- prorrogação;
- pênaltis;
- decisões administrativas;
- regras da competição.

Operações:

```text
calculate_official_score(...)
determine_winner(...)
determine_outcome(...)
```

---

## 116.4 TieResolutionService

Responsável por calcular o resultado de confrontos com múltiplas partidas.

Poderá considerar:

- placar agregado;
- gols fora;
- prorrogação;
- pênaltis;
- vantagem esportiva;
- decisão administrativa.

As regras concretas serão fornecidas por Domain Policies.

---

## 116.5 ProbabilityCalibrationService

Responsável por ajustar probabilidades de acordo com um método de calibração.

Operações:

```text
calibrate(...)
validate_distribution(...)
calculate_calibration_error(...)
```

Resultados deverão registrar:

- método;
- versão;
- parâmetros;
- data;
- amostra.

---

## 116.6 FairOddCalculationService

Responsável por converter Probability em DecimalOdd justa.

Operação conceitual:

```text
calculate_fair_odd(probability)
```

Deverá tratar:

- probabilidade zero;
- precisão;
- arredondamento;
- limites;
- ausência de margem.

---

## 116.7 ExpectedValueCalculationService

Responsável por calcular valor esperado a partir de:

- probabilidade própria;
- odd oferecida;
- stake ou unidade de referência.

A fórmula e sua versão deverão ser explícitas.

---

## 116.8 RecommendationEvaluationService

Responsável por combinar:

- ExpectedValue;
- ConfidenceScore;
- SampleQuality;
- liquidez;
- disponibilidade;
- risco;
- limites do usuário.

O resultado será uma decisão de recomendação, bloqueio ou necessidade de revisão.

---

## 116.9 StakeCalculationService

Responsável por sugerir stake de acordo com:

- Bankroll;
- perfil de risco;
- probabilidade;
- odd;
- exposição;
- estratégia configurada;
- limites máximos.

Poderá utilizar políticas como:

- stake fixa;
- percentual da banca;
- Kelly fracionado;
- limite por mercado;
- limite por competição.

---

## 116.10 BetSettlementService

Responsável por liquidar apostas com base em:

- resultado oficial;
- regras do mercado;
- regras da casa;
- void;
- push;
- meia vitória;
- meia perda;
- múltiplas seleções.

A liquidação deverá ser auditável e repetível.

---

# 117. Domain Policies

## 117.1 Definição

Domain Policy representa uma regra substituível, configurável ou variável de acordo com competição, provider, mercado, perfil ou estratégia.

Uma policy deverá responder a uma decisão específica.

Exemplos:

```text
AwayGoalsPolicy
MatchWinnerPolicy
ProviderPriorityPolicy
IdentityResolutionThresholdPolicy
StakeLimitPolicy
RecommendationRiskPolicy
```

---

## 117.2 Diferença entre Service e Policy

Domain Service executa uma operação.

Domain Policy define como determinada decisão deverá ser tomada.

Exemplo:

```text
TieResolutionService
    utiliza
AwayGoalsPolicy
```

---

## 117.3 Policies por competição

Competições poderão possuir políticas específicas para:

- pontuação;
- classificação;
- desempate;
- prorrogação;
- pênaltis;
- gols fora;
- número de participantes;
- formato de fase;
- limite de jogadores;
- substituições;
- suspensão.

---

## 117.4 Policies de integração

A integração poderá utilizar:

- ProviderPriorityPolicy;
- RetryPolicy;
- RateLimitPolicy;
- StalenessPolicy;
- ConflictResolutionPolicy;
- ProviderTrustPolicy.

---

## 117.5 Policies de identidade

A resolução de identidade poderá utilizar:

- AutoMatchThresholdPolicy;
- ManualReviewThresholdPolicy;
- DuplicateDetectionPolicy;
- AliasComparisonPolicy;
- TemporalCompatibilityPolicy.

---

## 117.6 Policies de recomendação

O Recommendation Context poderá utilizar:

- MinimumExpectedValuePolicy;
- MinimumConfidencePolicy;
- MinimumSampleQualityPolicy;
- MaximumOddPolicy;
- MarketAvailabilityPolicy;
- RiskClassificationPolicy;
- RecommendationSuppressionPolicy.

---

## 117.7 Policies de banca

O Risk and Portfolio Context poderá utilizar:

- MaximumStakePolicy;
- DailyExposurePolicy;
- CompetitionExposurePolicy;
- CorrelatedBetPolicy;
- DrawdownProtectionPolicy;
- KellyFractionPolicy.

---

# 118. Commands

## 118.1 Definição

Command representa uma intenção explícita de alterar o estado do sistema.

Um Command deverá expressar uma ação de negócio.

Exemplos:

```text
CreateMatch
AddMatchParticipant
RegisterMatchEvent
ChangeMatchSchedule
PublishPrediction
CreateRecommendation
RegisterBet
SettleBet
ResolveExternalIdentity
```

---

## 118.2 Características

Commands deverão possuir:

- identificador;
- tipo;
- dados necessários;
- autor ou processo;
- horário;
- chave de idempotência;
- correlation_id quando aplicável;
- causation_id quando aplicável.

---

## 118.3 Command não é evento

Command expressa intenção:

```text
ChangeMatchSchedule
```

Evento expressa fato ocorrido:

```text
MatchScheduleChanged
```

Um Command pode ser rejeitado.

Um evento somente deverá ser publicado após a operação correspondente ter sido confirmada.

---

## 118.4 Commands internos e externos

Commands externos poderão ser recebidos por:

- API;
- interface;
- importação;
- scheduler;
- processo de integração.

Commands internos poderão ser gerados por:

- Application Services;
- consumers;
- workflows;
- jobs;
- processos de reconciliação.

---

# 119. Application Services

## 119.1 Responsabilidade

Application Services deverão coordenar casos de uso.

Eles poderão:

- receber Command;
- validar autorização;
- carregar Aggregate Root;
- consultar outros contextos;
- executar método de domínio;
- persistir agregado;
- publicar eventos;
- iniciar transação;
- registrar auditoria;
- devolver resultado.

---

## 119.2 O que não pertence ao Application Service

Application Services não deverão concentrar regras centrais de negócio.

Exemplo inadequado:

```text
MatchApplicationService
    verifica manualmente todas as regras
    altera campos diretamente
    salva entidades internas
```

Exemplo preferencial:

```text
MatchApplicationService
    carrega Match
    consulta referências necessárias
    chama match.change_schedule(...)
    salva Match
    publica eventos
```

---

## 119.3 Fluxo padrão

```text
Entrada
    ↓
Validação estrutural
    ↓
Autorização
    ↓
Carregamento do Aggregate Root
    ↓
Validações externas
    ↓
Execução do domínio
    ↓
Persistência
    ↓
Publicação de eventos
    ↓
Resposta
```

---

# 120. Domain Events

## 120.1 Definição

Domain Event representa um fato relevante ocorrido dentro do domínio.

Exemplos:

```text
MatchCreated
MatchStarted
MatchFinished
MatchScheduleChanged
MatchEventRegistered
OfficialResultChanged
ExternalIdentityResolved
PredictionPublished
BetRegistered
BetSettled
```

---

## 120.2 Características

Domain Events deverão ser:

- imutáveis;
- nomeados no passado;
- associados ao Aggregate Root;
- versionados;
- rastreáveis;
- serializáveis;
- idempotentes para consumidores;
- publicados apenas após validação do domínio.

---

## 120.3 Estrutura base

```text
DomainEvent
    event_id
    event_type
    event_version
    aggregate_type
    aggregate_id
    aggregate_version
    occurred_at
    correlation_id
    causation_id
    actor_id
    payload
```

---

## 120.4 Eventos do Geography Context

Exemplos:

```text
CountryCreated
RegionAdded
CityAdded
GeographicAliasAdded
GeographicBoundaryChanged
```

---

## 120.5 Eventos do Competition Context

Exemplos:

```text
CompetitionCreated
SeasonCreated
StageCreated
RoundCreated
CompetitionRuleChanged
TieCreated
TieResolved
```

---

## 120.6 Eventos do Team Context

Exemplos:

```text
TeamCreated
TeamRenamed
TeamMembershipStarted
TeamMembershipEnded
SquadRegistrationCreated
SquadRegistrationEnded
```

---

## 120.7 Eventos do People Context

Exemplos:

```text
PersonCreated
PersonAliasAdded
PlayerProfileCreated
CoachProfileCreated
RefereeProfileCreated
PersonIdentityMerged
```

---

## 120.8 Eventos do Match Context

Exemplos:

```text
MatchCreated
MatchParticipantAdded
MatchVenueAssigned
MatchOfficialAssigned
MatchScheduleChanged
MatchStarted
MatchInterrupted
MatchResumed
MatchEventRegistered
LineupConfirmed
MatchFinished
MatchAbandoned
OfficialResultChanged
MatchRevised
```

---

## 120.9 Eventos do Identity Resolution Context

Exemplos:

```text
IdentityCandidateGenerated
ExternalIdentityMatched
ExternalIdentityRejected
IdentityReviewRequested
IdentityResolutionCorrected
CanonicalDuplicateDetected
```

---

## 120.10 Eventos do Data Fusion Context

Exemplos:

```text
FusionConflictDetected
FusionDecisionCreated
CanonicalUpdateProposed
ProviderValueRejected
FieldProvenanceUpdated
```

---

## 120.11 Eventos do Betting Market Context

Exemplos:

```text
OddsSnapshotCollected
MarketOpened
MarketSuspended
MarketClosed
OddChanged
BookmakerUnavailable
```

---

## 120.12 Eventos do Statistics Context

Exemplos:

```text
StatisticsCalculationRequested
StatisticsCalculated
StatisticalFeatureUpdated
SampleQualityChanged
StatisticsCalculationFailed
```

---

## 120.13 Eventos do Prediction Context

Exemplos:

```text
PredictionRequested
PredictionRunStarted
PredictionPublished
PredictionFailed
ModelVersionActivated
ModelVersionDeprecated
```

---

## 120.14 Eventos do Recommendation Context

Exemplos:

```text
RecommendationCreated
RecommendationSuppressed
RecommendationExpired
RecommendationRiskChanged
OpportunityDetected
```

---

## 120.15 Eventos do Risk and Portfolio Context

Exemplos:

```text
BankrollCreated
BankrollTransactionRegistered
BetRegistered
BetConfirmed
BetSettled
BetVoided
ExposureLimitReached
DrawdownLimitReached
```

---

# 121. Integration Events

## 121.1 Definição

Integration Event representa um fato publicado para consumo por outros contextos, módulos ou serviços.

Um Domain Event poderá gerar um Integration Event, mas eles não são obrigatoriamente o mesmo objeto.

---

## 121.2 Diferenças

| Domain Event | Integration Event |
|---|---|
| Interno ao domínio ou contexto | Contrato entre contextos |
| Pode conter detalhes internos | Deve possuir contrato estável |
| Pode evoluir junto ao agregado | Exige versionamento cuidadoso |
| Pode ser processado na transação | Normalmente é publicado após commit |

---

## 121.3 Estrutura base

```text
IntegrationEvent
    event_id
    event_name
    event_version
    occurred_at
    producer
    subject_id
    correlation_id
    causation_id
    payload
```

---

## 121.4 Compatibilidade

Integration Events deverão seguir regras de compatibilidade.

Alterações compatíveis:

- adicionar campo opcional;
- adicionar novo tipo de evento;
- ampliar enumeração quando consumidores tolerarem valores desconhecidos.

Alterações incompatíveis:

- remover campo obrigatório;
- alterar significado;
- alterar tipo;
- reutilizar nome para outro fato.

Alterações incompatíveis deverão gerar nova versão.

---

# 122. Publicação Confiável de Eventos

## 122.1 Problema do dual write

Não deverá existir um fluxo em que o sistema:

1. salva no banco;
2. publica evento;
3. falha entre as duas operações.

Esse cenário pode produzir estado confirmado sem evento correspondente.

---

## 122.2 Transactional Outbox

A estratégia preferencial será utilizar Transactional Outbox.

Fluxo:

```text
Início da transação
    ↓
Persistência do agregado
    ↓
Persistência do evento na Outbox
    ↓
Commit
    ↓
Publisher lê Outbox
    ↓
Publica evento
    ↓
Marca como publicado
```

---

## 122.3 Estrutura conceitual da Outbox

```text
OutboxMessage
    id
    event_type
    event_version
    aggregate_id
    payload
    occurred_at
    created_at
    published_at
    attempts
    last_error
    status
```

---

## 122.4 Idempotência do publisher

O publisher deverá suportar repetição.

A publicação duplicada poderá ocorrer.

Consumidores deverão utilizar `event_id` para deduplicação.

---

# 123. Inbox e Deduplicação

## 123.1 Transactional Inbox

Consumidores poderão utilizar Inbox para registrar eventos já processados.

Estrutura:

```text
InboxMessage
    event_id
    consumer
    received_at
    processed_at
    status
    attempts
    last_error
```

---

## 123.2 Fluxo de processamento

```text
Evento recebido
    ↓
event_id já processado?
    ├── Sim → ignorar com sucesso
    └── Não
          ↓
      processar
          ↓
      persistir resultado e Inbox
          ↓
      commit
```

---

# 124. Idempotência

## 124.1 Definição

Uma operação idempotente poderá ser executada múltiplas vezes sem produzir efeitos adicionais indevidos.

---

## 124.2 Chaves de idempotência

Poderão ser utilizadas:

- command_id;
- event_id;
- provider + endpoint + external_id + updated_at;
- payload_hash;
- sync_execution_id;
- client_request_id;
- business_key.

---

## 124.3 Idempotência em integrações

O processamento repetido do mesmo payload não deverá:

- duplicar partida;
- duplicar evento;
- duplicar odd;
- duplicar movimentação;
- duplicar previsão;
- duplicar recomendação.

---

## 124.4 Idempotência em operações financeiras

Commands financeiros deverão exigir chave de idempotência.

Exemplo:

```text
RegisterBankrollTransaction
    command_id
    bankroll_id
    amount
    type
```

A repetição do mesmo `command_id` deverá devolver o resultado existente.

---

# 125. Reprocessamento

## 125.1 Reprocessamento seguro

Processos derivados deverão poder ser executados novamente.

Exemplos:

- normalização;
- resolução de identidade;
- fusão;
- estatísticas;
- features;
- previsões;
- recomendações;
- projeções.

---

## 125.2 Versionamento de processamento

Cada execução deverá registrar:

- algoritmo;
- versão;
- parâmetros;
- entrada;
- saída;
- horário;
- status;
- erro;
- ambiente;
- código ou artifact hash.

---

## 125.3 Resultado imutável

Quando o resultado representar uma decisão histórica, a estratégia preferencial será criar nova versão em vez de sobrescrever.

Exemplo:

```text
Prediction v1
Prediction v2
Prediction v3
```

---

# 126. Compensações

## 126.1 Definição

Compensação representa uma nova operação que reduz ou corrige o efeito de uma operação anterior.

Ela não apaga o histórico.

---

## 126.2 Exemplos

- movimentação financeira compensatória;
- nova resolução de identidade;
- revisão de partida;
- anulação de evento;
- reliquidação de aposta;
- nova decisão de fusão;
- nova previsão;
- cancelamento de recomendação.

---

## 126.3 Operações irreversíveis

Operações que envolvam fatos históricos ou valores financeiros não deverão ser revertidas por exclusão silenciosa.

---

# 127. Tratamento de Falhas de Domínio

## 127.1 Tipos de falha

As falhas serão classificadas em:

- validação estrutural;
- violação de invariante;
- referência inexistente;
- conflito de concorrência;
- duplicação;
- autorização;
- dependência indisponível;
- erro de integração;
- erro de processamento;
- estado incompatível.

---

## 127.2 Erros de domínio

Erros de domínio deverão possuir códigos estáveis.

Exemplos:

```text
MATCH_PARTICIPANT_DUPLICATED
MATCH_INVALID_STATUS_TRANSITION
PERSON_NOT_ELIGIBLE_FOR_LINEUP
PROBABILITY_OUT_OF_RANGE
BANKROLL_INSUFFICIENT_BALANCE
BET_ALREADY_SETTLED
EXTERNAL_IDENTITY_CONFLICT
```

---

## 127.3 Mensagem e código

O código deverá ser estável para sistemas.

A mensagem poderá ser localizada para usuários.

---

## 127.4 Falhas transitórias

Falhas transitórias poderão ser repetidas.

Exemplos:

- timeout;
- provider indisponível;
- lock;
- falha temporária de broker;
- conexão com banco.

---

## 127.5 Falhas permanentes

Falhas permanentes exigem correção de dados, regra ou comando.

Exemplos:

- identificador inválido;
- entidade inexistente;
- regra incompatível;
- estado proibido;
- duplicação real.

---

# 128. Retry

## 128.1 Regras

Retries deverão ser aplicados apenas a falhas transitórias.

Não deverão ser utilizados indiscriminadamente para violações de domínio.

---

## 128.2 Backoff

A estratégia deverá preferencialmente utilizar:

- atraso progressivo;
- limite de tentativas;
- jitter;
- registro de erro;
- dead-letter após limite.

---

## 128.3 Dead-letter

Mensagens que excederem o limite de tentativas deverão ser encaminhadas para análise.

O registro deverá preservar:

- payload;
- evento;
- erro;
- stack trace técnica;
- consumidor;
- tentativas;
- horário.

---

# 129. Fluxos de Escrita

## 129.1 Criação de entidade canônica

```text
Command
    ↓
Validação estrutural
    ↓
Busca de duplicidade
    ↓
Resolução de identidade
    ↓
Criação pelo contexto proprietário
    ↓
Persistência
    ↓
Outbox
    ↓
Evento publicado
```

---

## 129.2 Atualização por provider

```text
Payload bruto
    ↓
Validação
    ↓
Normalização
    ↓
ExternalIdentifier
    ↓
Identity Resolution
    ↓
Data Fusion
    ↓
CanonicalUpdateProposal
    ↓
Application Service do contexto proprietário
    ↓
Aggregate Root
    ↓
Persistência e auditoria
```

---

## 129.3 Correção manual

```text
Usuário autorizado
    ↓
Command de correção
    ↓
Validação
    ↓
Carregamento do agregado
    ↓
Registro de motivo
    ↓
Nova revisão
    ↓
Persistência
    ↓
Evento
```

---

## 129.4 Processamento analítico

```text
Evento canônico
    ↓
Statistics
    ↓
Feature versionada
    ↓
Prediction
    ↓
Prediction imutável
    ↓
Recommendation
```

---

# 130. Invariantes por Contexto

## 130.1 Geography

- Country deverá possuir identidade única;
- códigos oficiais não deverão ser duplicados no mesmo padrão;
- Region deverá pertencer ao Country correto;
- City deverá ser compatível com Region e Country;
- alterações territoriais deverão preservar histórico.

---

## 130.2 Competition

- Season deverá pertencer a Competition válida;
- Stage deverá pertencer à Competition;
- Round deverá pertencer à Stage;
- ordenações deverão ser consistentes;
- regras de competição deverão possuir vigência;
- partidas históricas não deverão perder suas referências.

---

## 130.3 People

- Person deverá possuir identidade canônica única;
- especializações deverão compartilhar a identidade;
- aliases deverão preservar origem;
- merge de pessoas deverá ser auditável;
- perfis profissionais não deverão criar pessoas duplicadas.

---

## 130.4 Team

- Team deverá possuir identidade única;
- TeamMembership deverá possuir vigência coerente;
- SquadRegistration deverá possuir contexto válido;
- vínculos históricos não deverão ser sobrescritos;
- a mesma inscrição não deverá ser duplicada.

---

## 130.5 Match

- participantes deverão ser distintos;
- papéis deverão ser válidos;
- status deverá seguir transições permitidas;
- eventos deverão pertencer à partida;
- escalações deverão pertencer ao participante correto;
- pessoas deverão possuir relação válida;
- horários deverão preservar histórico;
- resultado oficial deverá refletir decisões vigentes;
- revisões deverão ser imutáveis.

---

## 130.6 Identity Resolution

- ExternalIdentifier ativo deverá apontar para uma identidade canônica;
- decisões deverão possuir evidências;
- correções deverão preservar decisão anterior;
- confiança deverá utilizar algoritmo versionado;
- duplicidades deverão ser sinalizadas.

---

## 130.7 Data Fusion

- toda decisão deverá preservar proveniência;
- conflitos não deverão ser ocultados;
- prioridade de provider deverá ser versionada;
- propostas deverão possuir destino;
- rejeições deverão registrar motivo.

---

## 130.8 Betting Market

- mercado deverá possuir definição canônica;
- seleção deverá pertencer ao mercado;
- odd deverá ser positiva e válida;
- snapshot deverá preservar horário;
- odds históricas não deverão ser sobrescritas;
- mercado fechado não deverá receber atualização ativa sem reabertura.

---

## 130.9 Prediction

- Prediction deverá referenciar ModelVersion;
- resultados deverão ser imutáveis;
- probabilidades deverão ser válidas;
- entrada deverá ser rastreável;
- publicação deverá registrar data;
- nova versão não deverá alterar execução antiga.

---

## 130.10 Recommendation

- recomendação deverá referenciar Prediction;
- ExpectedValue deverá ser rastreável;
- risco deverá utilizar policy versionada;
- recomendação expirada não deverá permanecer ativa;
- bloqueios deverão registrar motivo.

---

## 130.11 Risk and Portfolio

- movimentações confirmadas deverão ser imutáveis;
- saldo deverá ser derivável;
- stake deverá respeitar moeda;
- aposta não deverá ser liquidada duas vezes sem reliquidação;
- exposição deverá considerar apostas abertas;
- compensações deverão preservar histórico.

---

# 131. Decisões da G4.A.4.2

As seguintes decisões passam a integrar a arquitetura oficial:

1. invariantes deverão ser protegidas pelo componente mais próximo do domínio;
2. consistência forte permanecerá preferencialmente dentro de um agregado;
3. operações entre agregados utilizarão consistência eventual por padrão;
4. Domain Services representarão operações reais do negócio;
5. Domain Policies representarão regras substituíveis ou configuráveis;
6. Commands representarão intenção de mudança;
7. Domain Events representarão fatos ocorridos;
8. Integration Events possuirão contratos estáveis e versionados;
9. Transactional Outbox será a estratégia preferencial de publicação;
10. consumidores deverão ser idempotentes;
11. processos derivados deverão ser reprocessáveis;
12. falhas transitórias e permanentes serão tratadas de forma diferente;
13. correções históricas utilizarão revisão ou compensação;
14. Application Services coordenarão casos de uso sem concentrar regras de negócio;
15. erros de domínio possuirão códigos estáveis.

---

# 132. Conclusão da G4.A.4.2

A subetapa G4.A.4.2 — Regras de Consistência, Serviços, Políticas e Eventos de Domínio está concluída.

Foram definidos:

- tipos de consistência;
- invariantes;
- validações;
- Domain Services;
- Domain Policies;
- Commands;
- Application Services;
- Domain Events;
- Integration Events;
- Outbox;
- Inbox;
- idempotência;
- retry;
- reprocessamento;
- compensações;
- tratamento de falhas;
- fluxos de escrita.

---

# Parte VI — Arquitetura Transacional, Histórico e Evolução

## 133. Objetivo da G4.A.4.3

Esta parte define como o UltraStats AI controlará:

- transações;
- concorrência;
- versionamento;
- histórico;
- auditoria;
- identificação;
- projeções;
- cache;
- evolução de contratos;
- integração;
- processamento analítico;
- modelos preditivos;
- observabilidade;
- retenção de dados.

Ao final desta parte, a arquitetura estará preparada para orientar a implementação do G5.

---

# 134. Unidade de Trabalho

## 134.1 Definição

Uma Unit of Work representa o conjunto de operações persistidas como uma única unidade transacional.

A Unit of Work deverá:

- iniciar transação;
- carregar repositories;
- rastrear agregados modificados;
- persistir alterações;
- persistir Outbox;
- confirmar ou reverter;
- liberar recursos.

---

## 134.2 Escopo

Uma Unit of Work deverá possuir escopo curto.

Ela não deverá permanecer aberta durante:

- chamadas externas;
- processamento estatístico longo;
- treinamento;
- inferência remota;
- espera de usuário;
- upload de arquivos;
- retries prolongados.

---

## 134.3 Exemplo conceitual

```text
with unit_of_work:
    match = match_repository.get(match_id)
    match.change_schedule(...)
    match_repository.save(match)
    outbox_repository.add(match.pull_events())
    unit_of_work.commit()
```

---

# 135. Fronteiras Transacionais

## 135.1 Um agregado por transação

A regra preferencial será modificar um Aggregate Root por transação.

Essa regra reduz:

- contenção;
- deadlocks;
- dependências;
- conflitos;
- complexidade de rollback.

---

## 135.2 Exceções

Uma transação poderá envolver mais de um agregado quando:

- ambos estiverem no mesmo contexto;
- a operação exigir atomicidade real;
- a quantidade for pequena;
- o risco de contenção for aceitável;
- a justificativa estiver documentada.

---

## 135.3 Proibição de transação distribuída por padrão

Não será adotado two-phase commit como estratégia padrão entre contextos.

A coordenação será preferencialmente feita por:

- eventos;
- workflows;
- sagas;
- compensações;
- reprocessamento.

---

# 136. Concorrência

## 136.1 Problema

Dois processos poderão tentar alterar o mesmo agregado simultaneamente.

Exemplos:

- dois providers atualizando uma partida;
- correção manual durante sincronização;
- duas liquidações;
- múltiplos consumers;
- processamento repetido.

---

## 136.2 Optimistic Locking

A estratégia preferencial será Optimistic Locking.

Aggregate Roots deverão possuir campo de versão.

Exemplo:

```text
Match
    id
    version
```

A atualização deverá utilizar condição:

```text
WHERE id = :id
AND version = :expected_version
```

Após sucesso, a versão será incrementada.

---

## 136.3 Conflito de versão

Quando a versão esperada não corresponder:

- a transação deverá falhar;
- o estado deverá ser recarregado;
- a operação poderá ser repetida quando segura;
- conflitos manuais poderão exigir revisão.

---

## 136.4 Pessimistic Locking

Pessimistic Locking poderá ser utilizado em casos específicos:

- liquidação financeira crítica;
- alocação de recurso único;
- operação curta;
- alta chance de conflito;
- necessidade de serialização explícita.

Seu uso deverá ser restrito.

---

## 136.5 Lock lógico

Poderão existir locks lógicos para:

- sincronização de provider;
- reprocessamento de competição;
- geração de previsão;
- treinamento;
- liquidação em lote.

Locks lógicos deverão possuir:

- owner;
- início;
- expiração;
- heartbeat quando necessário;
- liberação;
- recuperação de lock abandonado.

---

# 137. Versionamento de Agregados

## 137.1 Aggregate version

Todo Aggregate Root relevante deverá possuir versão numérica crescente.

A versão será utilizada para:

- concorrência otimista;
- eventos;
- auditoria;
- cache;
- sincronização;
- projeções.

---

## 137.2 Versão de entidade interna

Entidades internas poderão possuir versão própria quando:

- forem atualizadas independentemente na persistência;
- possuírem alto volume;
- exigirem auditoria específica;
- forem alvo de concorrência.

A versão interna não elimina a responsabilidade do Aggregate Root.

---

## 137.3 Versão de schema

Schemas de API e eventos deverão possuir versão independente da versão do agregado.

Exemplo:

```text
aggregate_version: 18
event_version: 2
schema_version: 1
```

---

# 138. Histórico

## 138.1 Princípio

Fatos relevantes não deverão ser sobrescritos sem preservação do estado anterior.

---

## 138.2 Estratégias de histórico

Poderão ser utilizadas:

- tabelas de revisão;
- tabelas temporais;
- registros append-only;
- snapshots;
- eventos;
- campos de vigência;
- versões imutáveis;
- transações compensatórias.

---

## 138.3 Histórico por vigência

Entidades temporais deverão utilizar:

```text
valid_from
valid_until
```

Exemplos:

- TeamMembership;
- SquadRegistration;
- alias;
- regra de competição;
- credencial profissional;
- provider priority.

---

## 138.4 Histórico append-only

Registros históricos críticos deverão preferencialmente ser append-only.

Exemplos:

- MatchRevision;
- BankrollTransaction;
- Prediction;
- OddsSnapshot;
- Settlement;
- FusionDecision;
- IdentityResolutionDecision;
- AuditLog.

---

## 138.5 Estado atual e histórico

O sistema poderá manter simultaneamente:

- estado atual otimizado;
- histórico completo.

Exemplo:

```text
Match
    scheduled_at atual

MatchScheduleChange
    todas as alterações
```

---

# 139. Auditoria

## 139.1 Objetivo

A auditoria deverá permitir reconstruir:

- quem alterou;
- o que alterou;
- quando alterou;
- valor anterior;
- valor novo;
- origem;
- motivo;
- processo;
- correlação;
- versão.

---

## 139.2 Audit Log

Estrutura conceitual:

```text
AuditLog
    id
    aggregate_type
    aggregate_id
    action
    actor_type
    actor_id
    source
    before
    after
    reason
    occurred_at
    correlation_id
    command_id
```

---

## 139.3 Actor

O ator poderá ser:

- usuário;
- administrador;
- provider;
- collector;
- scheduler;
- consumer;
- modelo;
- processo de migração;
- script de manutenção.

---

## 139.4 Dados sensíveis

Audit Logs não deverão registrar:

- credenciais;
- tokens;
- senhas;
- secrets;
- payloads sensíveis completos;
- dados pessoais desnecessários.

---

## 139.5 Imutabilidade

Audit Logs deverão ser imutáveis.

Correções no próprio log deverão gerar novo registro administrativo.

---

# 140. Exclusão Lógica

## 140.1 Uso

Aggregate Roots relevantes poderão utilizar:

```text
is_active
deleted_at
deleted_by
deletion_reason
```

---

## 140.2 Não equivalência

Inativação e exclusão lógica não possuem o mesmo significado.

Uma Team inativa ainda existe historicamente.

Um registro marcado como excluído poderá ter sido removido por erro, privacidade ou administração.

---

## 140.3 Consultas

Queries padrão deverão excluir registros logicamente removidos quando apropriado.

Consultas administrativas deverão permitir visualização controlada.

---

# 141. Retenção de Dados

## 141.1 Classificação

Os dados serão classificados em:

- permanentes;
- históricos;
- temporários;
- derivados;
- reprocessáveis;
- sensíveis;
- operacionais.

---

## 141.2 Dados permanentes ou históricos

Exemplos:

- identidades canônicas;
- partidas oficiais;
- decisões;
- movimentações financeiras;
- apostas;
- previsões publicadas;
- resoluções de identidade;
- decisões de fusão.

---

## 141.3 Dados temporários

Exemplos:

- locks;
- cache;
- arquivos intermediários;
- respostas temporárias;
- resultados parciais;
- tokens;
- sessões.

---

## 141.4 Dados reprocessáveis

Exemplos:

- projeções;
- features;
- agregações;
- dashboards;
- cache estatístico;
- rankings derivados.

Esses dados poderão ser removidos e reconstruídos, desde que a origem e a versão permaneçam disponíveis.

---

# 142. Estratégia de Identificadores

## 142.1 UUID

A estratégia padrão de identificadores canônicos será UUID.

A decisão final entre UUID v4 e UUID v7 deverá ocorrer antes da implementação do G5.

---

## 142.2 UUID v4

Características:

- aleatório;
- amplamente suportado;
- simples;
- pode causar fragmentação maior em índices.

---

## 142.3 UUID v7

Características:

- ordenável temporalmente;
- melhor localidade de índice;
- adequado para sistemas distribuídos;
- suporte deverá ser validado na stack escolhida.

---

## 142.4 Decisão preliminar

A preferência arquitetural será UUID v7, desde que:

- PostgreSQL;
- SQLAlchemy;
- bibliotecas;
- testes;
- serialização;

possuam suporte adequado.

Caso contrário, UUID v4 será utilizado inicialmente.

---

## 142.5 IDs de alto volume

Tabelas de alto volume poderão utilizar chave técnica sequencial adicional.

Exemplos:

- OddsSnapshot;
- MatchEvent;
- raw payload;
- outbox;
- inbox;
- audit log.

A identidade canônica ou pública continuará separada.

---

# 143. Projeções e Read Models

## 143.1 Definição

Read Models são estruturas otimizadas para consulta.

Eles poderão reunir dados de múltiplos contextos.

---

## 143.2 Exemplos

- página completa da partida;
- dashboard de competição;
- forma recente da equipe;
- comparação de odds;
- relatório de recomendação;
- desempenho de banca;
- painel de modelos.

---

## 143.3 Propriedade

Read Models não serão fontes oficiais.

Eles poderão ser:

- apagados;
- reconstruídos;
- reprocessados;
- atualizados eventualmente.

---

## 143.4 Desnormalização

Read Models poderão duplicar:

- nomes;
- placares;
- status;
- métricas;
- labels;
- valores calculados.

A duplicação será aceitável por ser orientada à leitura.

---

## 143.5 Atualização

Read Models poderão ser atualizados por:

- eventos;
- jobs;
- refresh;
- materialized views;
- processamento em lote;
- reconstrução completa.

---

# 144. CQRS

## 144.1 Uso parcial

O UltraStats AI poderá utilizar separação conceitual entre escrita e leitura sem adotar CQRS completo em todos os contextos.

---

## 144.2 Escrita

A escrita utilizará:

- Commands;
- Application Services;
- Aggregate Roots;
- repositories;
- Unit of Work;
- eventos.

---

## 144.3 Leitura

A leitura utilizará:

- Query Services;
- projections;
- views;
- queries SQL especializadas;
- cache;
- read models.

---

## 144.4 Critério

CQRS mais explícito deverá ser utilizado onde houver:

- leitura muito maior que escrita;
- consultas complexas;
- múltiplas agregações;
- necessidade de baixa latência;
- alto volume;
- modelos de leitura muito diferentes do domínio de escrita.

---

# 145. Cache

## 145.1 Objetivo

Cache deverá reduzir custo de consultas sem assumir responsabilidade sobre o estado oficial.

---

## 145.2 Possíveis usos

- dados geográficos;
- competições;
- equipes;
- configurações de provider;
- dashboards;
- rankings;
- features;
- previsões recentes;
- odds agregadas.

---

## 145.3 Chaves

Chaves deverão incluir:

- tipo;
- identificador;
- versão;
- parâmetros;
- período;
- algoritmo quando aplicável.

Exemplo:

```text
match:{match_id}:view:v3
```

---

## 145.4 Invalidação

A invalidação poderá ocorrer por:

- TTL;
- evento;
- versão;
- exclusão explícita;
- troca de namespace.

---

## 145.5 Cache stampede

Deverão ser considerados:

- locks curtos;
- stale-while-revalidate;
- jitter de TTL;
- preenchimento antecipado;
- limitação de concorrência.

---

# 146. Sagas e Workflows

## 146.1 Definição

Saga representa um processo que coordena múltiplas operações entre contextos sem transação distribuída.

---

## 146.2 Exemplo: processamento de partida encerrada

```text
MatchFinished
    ↓
StatisticsCalculationRequested
    ↓
StatisticsCalculated
    ↓
PredictionRequested
    ↓
PredictionPublished
    ↓
RecommendationCreated
```

---

## 146.3 Estado da saga

Uma saga persistente deverá registrar:

- saga_id;
- tipo;
- estado atual;
- evento inicial;
- etapas concluídas;
- etapa pendente;
- tentativas;
- erro;
- timestamps;
- correlation_id.

---

## 146.4 Compensação

Nem toda etapa possuirá rollback real.

A compensação poderá consistir em:

- invalidar resultado derivado;
- gerar nova versão;
- cancelar recomendação;
- solicitar reprocessamento;
- marcar estado inconsistente;
- registrar correção.

---

# 147. Evolução de Schemas

## 147.1 Migrations

Toda alteração persistente deverá utilizar migrations versionadas.

Migrations não deverão ser editadas após utilização compartilhada.

---

## 147.2 Compatibilidade progressiva

Mudanças deverão preferencialmente seguir:

```text
1. adicionar nova estrutura;
2. suportar estrutura antiga e nova;
3. migrar dados;
4. atualizar consumidores;
5. remover estrutura antiga.
```

---

## 147.3 Expand and contract

A estratégia expand and contract será preferencial para mudanças incompatíveis.

---

## 147.4 Backfill

Backfills deverão registrar:

- script;
- versão;
- período;
- quantidade;
- erros;
- duração;
- checkpoint;
- possibilidade de retomada.

---

## 147.5 Alterações destrutivas

Remoções de colunas ou tabelas deverão ocorrer apenas após confirmação de que:

- código antigo não utiliza;
- consumers foram atualizados;
- dados foram migrados;
- rollback foi avaliado;
- backup existe.

---

# 148. Versionamento de Contratos

## 148.1 APIs

APIs deverão possuir estratégia de versionamento.

Possibilidades:

- versão na URL;
- versão em header;
- evolução compatível;
- endpoints separados.

---

## 148.2 Eventos

Eventos deverão possuir:

```text
event_name
event_version
```

---

## 148.3 Payloads de providers

Contratos de providers deverão registrar:

- provider;
- endpoint;
- schema version;
- parser version;
- collected_at.

---

## 148.4 Modelos preditivos

Predictions deverão registrar:

- model_name;
- model_version;
- feature_version;
- dataset_version;
- calibration_version;
- code_version;
- artifact_hash.

---

# 149. Arquitetura de Integração

## 149.1 Camadas

```text
Provider Client
    ↓
Collector
    ↓
Raw Storage
    ↓
Validator
    ↓
Normalizer
    ↓
Identity Resolution
    ↓
Data Fusion
    ↓
Canonical Command
```

---

## 149.2 Provider Client

Responsável por:

- autenticação;
- HTTP;
- paginação;
- headers;
- timeout;
- rate limit;
- resposta bruta.

Não deverá conhecer o modelo canônico.

---

## 149.3 Collector

Responsável por:

- coordenar coleta;
- definir endpoints;
- registrar execução;
- persistir payload;
- controlar retry;
- emitir evento de payload recebido.

---

## 149.4 Validator

Responsável por:

- validar estrutura;
- detectar campos obrigatórios;
- registrar incompatibilidades;
- separar erro total e parcial;
- impedir entrada de payload corrompido.

---

## 149.5 Normalizer

Responsável por converter payload externo em representação normalizada intermediária.

A representação normalizada ainda não será canônica.

---

## 149.6 Identity Resolution

Responsável por encontrar ou propor identidade canônica.

---

## 149.7 Data Fusion

Responsável por decidir qual valor deverá ser proposto ao contexto proprietário.

---

## 149.8 Canonical Command

A última etapa deverá gerar Command explícito.

Exemplo:

```text
UpdateMatchFromFusionProposal
```

O contexto proprietário continuará responsável por aceitar ou rejeitar a alteração.

---

# 150. Raw Data Architecture

## 150.1 Imutabilidade

Payloads brutos deverão ser imutáveis.

---

## 150.2 Estrutura

```text
RawPayload
    id
    provider_id
    endpoint
    request_parameters
    response_status
    headers
    body
    body_hash
    collected_at
    sync_execution_id
    parser_version
    processing_status
```

---

## 150.3 Deduplicação

Payloads idênticos poderão ser deduplicados por hash, desde que:

- a ocorrência seja registrada;
- o horário seja preservado;
- o relacionamento com a execução seja mantido.

---

## 150.4 Reprocessamento

O raw storage deverá permitir reprocessar dados com:

- novo parser;
- nova normalização;
- nova regra de identidade;
- nova regra de fusão.

---

# 151. Data Lineage

## 151.1 Objetivo

Data Lineage deverá permitir rastrear um dado canônico até sua origem.

Fluxo esperado:

```text
Campo canônico
    ↓
FusionDecision
    ↓
NormalizedRecord
    ↓
RawPayload
    ↓
ProviderRequest
```

---

## 151.2 Proveniência por campo

Quando diferentes campos possuírem origens diferentes, a proveniência deverá ser registrada individualmente.

Exemplo:

```text
Match.scheduled_at
    provider A

Match.venue_id
    provider B

Match.status
    provider C
```

---

## 151.3 Uso

Lineage será utilizada para:

- auditoria;
- correção;
- reprocessamento;
- confiança;
- comparação de providers;
- explicabilidade;
- diagnóstico.

---

# 152. Arquitetura Estatística

## 152.1 Dados de origem

O Statistics Context deverá consumir apenas:

- dados canônicos;
- snapshots versionados;
- eventos confirmados;
- dados de mercado rastreáveis.

---

## 152.2 Features

Cada feature deverá possuir:

```text
feature_name
feature_version
subject_type
subject_id
reference_time
value
sample_size
quality
generated_at
source_versions
```

---

## 152.3 Point-in-time correctness

Features utilizadas em previsão deverão utilizar apenas informações disponíveis no instante de referência.

Dados futuros não poderão vazar para o treinamento ou inferência histórica.

---

## 152.4 Reprodutibilidade

O cálculo deverá registrar:

- código;
- versão;
- parâmetros;
- janela;
- filtros;
- fonte;
- horário de corte.

---

## 152.5 Materialização

Features poderão ser:

- calculadas sob demanda;
- materializadas;
- armazenadas em feature store;
- atualizadas por eventos;
- recalculadas em lote.

---

# 153. Arquitetura de Modelos Preditivos

## 153.1 Model Registry

O sistema deverá possuir registro de modelos.

Estrutura conceitual:

```text
ModelRegistryEntry
    model_id
    name
    version
    artifact_uri
    artifact_hash
    feature_version
    training_dataset_version
    metrics
    status
    created_at
    activated_at
```

---

## 153.2 Estados do modelo

Exemplos:

```text
draft
training
validated
active
deprecated
blocked
archived
```

---

## 153.3 Inferência

Cada PredictionRun deverá registrar:

- model version;
- feature version;
- input snapshot;
- execution time;
- output;
- warnings;
- environment;
- code version.

---

## 153.4 Imutabilidade

Uma Prediction publicada não deverá ser alterada.

Correção ou nova inferência gera nova Prediction.

---

## 153.5 Explicabilidade

A explicação deverá registrar:

- fatores relevantes;
- contribuição;
- limitações;
- qualidade da amostra;
- versão do método.

---

## 153.6 Monitoramento

Modelos deverão ser monitorados quanto a:

- calibração;
- acurácia;
- drift;
- cobertura;
- erro por mercado;
- erro por competição;
- desempenho temporal;
- falhas de inferência.

---

# 154. Arquitetura de Recomendações

## 154.1 Entrada

Recommendation deverá utilizar:

- Prediction;
- odd atual;
- ExpectedValue;
- SampleQuality;
- ConfidenceScore;
- políticas de risco;
- disponibilidade do mercado.

---

## 154.2 Snapshot

A recomendação deverá preservar:

- odd utilizada;
- probabilidade utilizada;
- horário;
- mercado;
- bookmaker;
- modelo;
- policy version;
- métricas de qualidade.

---

## 154.3 Expiração

Recomendações deverão possuir regras de expiração.

Motivos:

- odd alterada;
- mercado suspenso;
- partida iniciada;
- nova previsão;
- informação crítica atualizada;
- limite de tempo.

---

## 154.4 Reavaliação

Mudanças relevantes poderão gerar nova recomendação.

A recomendação anterior deverá permanecer histórica.

---

# 155. Arquitetura de Banca e Apostas

## 155.1 Ledger

A Bankroll deverá utilizar conceito de ledger.

O saldo deverá ser derivável a partir das transações.

---

## 155.2 Tipos de transação

Exemplos:

```text
deposit
withdrawal
stake_reserved
stake_released
bet_return
adjustment
bonus
fee
```

---

## 155.3 Reserva de stake

A confirmação de uma aposta poderá gerar reserva de stake.

Após liquidação:

- stake poderá ser consumida;
- retorno poderá ser creditado;
- reserva poderá ser liberada em void.

---

## 155.4 Reliquidação

Uma Bet já liquidada poderá ser reliquidada quando o resultado oficial mudar.

A reliquidação deverá:

- preservar liquidação anterior;
- gerar compensações;
- recalcular saldo;
- registrar motivo;
- publicar evento.

---

# 156. Segurança e Autorização

## 156.1 Autorização antes da operação

Application Services deverão verificar autorização antes de carregar ou modificar dados sensíveis quando apropriado.

---

## 156.2 Perfis

Possíveis perfis:

- usuário;
- analista;
- operador;
- administrador;
- auditor;
- processo interno;
- provider integration.

---

## 156.3 Operações restritas

Exemplos:

- merge de identidades;
- correção de resultado;
- alteração financeira;
- reliquidação;
- ativação de modelo;
- mudança de provider priority;
- exclusão lógica;
- reprocessamento em massa.

---

## 156.4 Segredos

Credenciais deverão permanecer fora do domínio.

Elas deverão ser armazenadas em configuração segura ou secret manager.

---

# 157. Observabilidade

## 157.1 Logs

Logs deverão ser estruturados.

Campos recomendados:

```text
timestamp
level
service
context
operation
correlation_id
causation_id
command_id
event_id
aggregate_id
provider_id
duration
status
error_code
```

---

## 157.2 Métricas

Métricas deverão incluir:

- duração de requests;
- duração de collectors;
- payloads coletados;
- erros de provider;
- retries;
- backlog;
- eventos publicados;
- eventos falhos;
- tempo de processamento;
- previsões geradas;
- falhas de inferência;
- cache hit;
- conflitos de concorrência.

---

## 157.3 Tracing

Fluxos distribuídos deverão propagar:

- correlation_id;
- trace_id;
- span_id;
- causation_id.

---

## 157.4 Alertas

Alertas deverão considerar:

- provider indisponível;
- aumento de erro;
- atraso de sincronização;
- fila acumulada;
- consumer parado;
- falha de publicação;
- inconsistência financeira;
- drift de modelo;
- queda de cobertura.

---

# 158. Reconciliação

## 158.1 Objetivo

Reconciliação identifica divergências entre:

- estado atual;
- histórico;
- providers;
- projeções;
- saldo;
- eventos;
- resultados derivados.

---

## 158.2 Jobs de reconciliação

Exemplos:

- comparar partidas com providers;
- verificar odds ausentes;
- verificar eventos sem projeção;
- verificar outbox não publicada;
- verificar inbox travada;
- recalcular saldo;
- verificar apostas não liquidadas;
- verificar Prediction sem Recommendation.

---

## 158.3 Resultado

Reconciliação deverá:

- registrar divergência;
- classificar gravidade;
- corrigir automaticamente quando seguro;
- solicitar revisão quando ambíguo;
- preservar evidências.

---

# 159. Backups e Recuperação

## 159.1 Backups

A estratégia deverá incluir:

- backups completos;
- backups incrementais quando aplicável;
- retenção;
- criptografia;
- teste de restauração;
- cópia em ambiente separado.

---

## 159.2 Point-in-time recovery

O PostgreSQL deverá ser configurado para permitir recuperação até um ponto no tempo quando o ambiente exigir.

---

## 159.3 Teste

Backup não será considerado válido sem teste periódico de restauração.

---

# 160. Ambiente e Configuração

## 160.1 Separação

Deverão existir configurações separadas para:

- development;
- test;
- staging;
- production.

---

## 160.2 Configuração versionada

Configurações não sensíveis poderão ser versionadas.

Segredos não poderão ser adicionados ao Git.

---

## 160.3 Feature flags

Feature flags poderão controlar:

- providers;
- mercados;
- modelos;
- recomendações;
- collectors;
- novos fluxos;
- mudanças graduais.

---

# 161. Estratégia de Testes Arquiteturais

## 161.1 Testes de Value Objects

Deverão validar:

- limites;
- igualdade;
- imutabilidade;
- serialização;
- operações.

---

## 161.2 Testes de entidades

Deverão validar:

- transições;
- regras locais;
- estados inválidos;
- histórico.

---

## 161.3 Testes de agregados

Deverão validar:

- invariantes;
- ownership;
- eventos gerados;
- concorrência;
- comandos repetidos.

---

## 161.4 Testes de Domain Services

Deverão validar:

- regras multiagregado;
- policies;
- casos limítrofes;
- versões;
- determinismo.

---

## 161.5 Testes de integração

Deverão validar:

- repositories;
- transactions;
- constraints;
- migrations;
- outbox;
- inbox;
- queries.

---

## 161.6 Testes de contrato

Deverão validar:

- APIs;
- eventos;
- providers;
- schemas;
- compatibilidade entre versões.

---

## 161.7 Testes de reprocessamento

Deverão confirmar que:

- processamento repetido não duplica dados;
- resultados são reproduzíveis;
- checkpoints funcionam;
- erros podem ser retomados.

---

# 162. Decisões da G4.A.4.3

As seguintes decisões passam a integrar a arquitetura oficial:

1. Unit of Work controlará transações.
2. A regra preferencial será um Aggregate Root por transação.
3. Optimistic Locking será a estratégia padrão de concorrência.
4. Pessimistic Locking será utilizado apenas em casos específicos.
5. agregados possuirão versão.
6. fatos históricos relevantes serão preservados.
7. Audit Logs serão imutáveis.
8. exclusão lógica será utilizada quando adequada.
9. Read Models não serão fontes oficiais.
10. CQRS será adotado de forma seletiva.
11. cache será descartável e versionado.
12. Sagas coordenarão workflows entre contextos.
13. migrations utilizarão evolução progressiva.
14. contratos de APIs e eventos serão versionados.
15. raw payloads serão imutáveis.
16. Data Lineage deverá permitir rastreamento por campo.
17. features deverão respeitar point-in-time correctness.
18. Predictions publicadas serão imutáveis.
19. recomendações preservarão snapshot.
20. Bankroll utilizará ledger.
21. observabilidade utilizará logs, métricas e tracing.
22. jobs de reconciliação verificarão divergências.
23. backups deverão possuir testes de restauração.
24. testes arquiteturais cobrirão domínio, persistência e contratos.

---

# 163. Pontos de Decisão Antes do G5

Antes de iniciar a implementação persistente, deverão ser definidos:

- UUID v4 ou UUID v7;
- estrutura inicial de pacotes;
- biblioteca de UUID;
- estratégia de Unit of Work;
- padrão de repositories;
- estratégia de Domain Events;
- implementação de Outbox;
- implementação de Inbox;
- campos padrão de auditoria;
- campos padrão de versionamento;
- política de soft delete;
- formato de erros de domínio;
- estratégia de serializers;
- precisão de tipos Decimal;
- padrão de timezone;
- estratégia de migrations;
- granularidade dos Aggregate Roots;
- Season como Aggregate Root ou entidade interna;
- Tie como Aggregate Root ou entidade interna;
- Bet como Aggregate Root ou entidade interna;
- estrutura definitiva de Odds;
- separação entre MatchStatistic oficial e estatística derivada;
- banco ou estrutura de raw payload;
- estratégia de feature store;
- estratégia de model registry.

---

# 164. Checklist de Prontidão para o G5

A implementação do G5 somente deverá iniciar após confirmar:

- [ ] Bounded Contexts aprovados;
- [ ] Aggregate Roots aprovados;
- [ ] entidades internas aprovadas;
- [ ] ownership aprovado;
- [ ] Value Objects aprovados;
- [ ] estratégia de IDs definida;
- [ ] estratégia de concorrência definida;
- [ ] regras de histórico definidas;
- [ ] padrão de auditoria definido;
- [ ] padrão de repositories definido;
- [ ] padrão de Unit of Work definido;
- [ ] padrão de Domain Events definido;
- [ ] Outbox definida;
- [ ] erros de domínio definidos;
- [ ] pontos pendentes revisados;
- [ ] roadmap atualizado.

---

# 165. Resultado da G4.A.4.3

Com a conclusão desta parte, ficam definidos:

- limites transacionais;
- Unit of Work;
- concorrência;
- Optimistic Locking;
- histórico;
- auditoria;
- retenção;
- IDs;
- projeções;
- CQRS;
- cache;
- Sagas;
- migrations;
- contratos;
- arquitetura de integração;
- raw payloads;
- Data Lineage;
- arquitetura estatística;
- arquitetura preditiva;
- arquitetura de recomendações;
- arquitetura de banca;
- segurança;
- observabilidade;
- reconciliação;
- backups;
- testes arquiteturais.

---

# 166. Conclusão da G4.A.4

A etapa G4.A.4 — Arquitetura dos Agregados e Regras do Domínio está concluída.

Foram concluídas:

```text
G4.A.4.1 — Agregados, Bounded Contexts e Value Objects

G4.A.4.2 — Regras de Consistência, Serviços, Políticas e Eventos de Domínio

G4.A.4.3 — Arquitetura Transacional, Histórico e Evolução
```

A arquitetura agora define:

- como o domínio é dividido;
- quem possui cada informação;
- quais entidades controlam os ciclos de vida;
- quais regras devem ser preservadas;
- como diferentes contextos se comunicam;
- como eventos serão publicados;
- como transações serão controladas;
- como concorrência será tratada;
- como histórico e auditoria serão preservados;
- como dados externos chegarão ao domínio canônico;
- como estatísticas e previsões serão produzidas;
- como a plataforma poderá evoluir de forma segura.

A próxima grande etapa será a implementação do domínio canônico no código.

Essa implementação deverá transformar as decisões arquiteturais em:

- estrutura de pacotes;
- modelos de domínio;
- Value Objects;
- enums;
- entidades;
- Aggregate Roots;
- Domain Services;
- Domain Policies;
- repositories;
- Unit of Work;
- modelos SQLAlchemy;
- migrations;
- testes.

A etapa seguinte do roadmap será:

```text
G5 — Domínio Canônico
```