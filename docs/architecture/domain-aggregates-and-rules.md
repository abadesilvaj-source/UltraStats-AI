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