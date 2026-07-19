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