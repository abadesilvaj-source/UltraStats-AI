# Avaliação integral do sistema — 2 de agosto de 2026

## Resumo executivo

O UltraStats possui uma fundação de engenharia ampla: API, scheduler,
PostgreSQL, autenticação, frontends web/mobile, domínio canônico, coleta,
estatística, modelos, recomendação, risco, auditoria e testes. O principal risco
agora não é ausência de funcionalidades, mas transformar volume técnico em
evidência prospectiva confiável.

Classificação atual:

| Dimensão | Estado | Avaliação |
|---|---|---|
| Software local | saudável | serviços e builds operacionais |
| Arquitetura | forte, complexa | boa separação conceitual, duas camadas Python ainda coexistem |
| Dados | desigual | grande volume, mas odds, escalações e detalhes variam por competição |
| Estatística | madura como baseline | Poisson/Elo e mercados especializados com fallback |
| Machine learning | promissor | validação temporal existe; evidência financeira prospectiva ainda insuficiente |
| Recomendação | seletiva v2 iniciada | política anterior demonstrou sobreconfiança e excesso de exposição |
| Risco | corrigido no paper v2 | limites precisam ser observados em janela prospectiva |
| Produto | funcional, técnico | jornada ainda privilegia quantidade e administração |
| Operação externa | não autorizada | aplicação permanece local |

## Evidências observadas

- API e cinco serviços locais podem operar em Docker com PostgreSQL persistente.
- A API registrava 15.118 partidas, 357.922 previsões e 125 mercados na
  fotografia operacional desta avaliação.
- O pipeline de aprendizado possuía 27.843 previsões auditadas e validação
  walk-forward aprovada globalmente, com diferenças importantes entre mercados.
- Havia milhares de incidentes de qualidade, principalmente odds ausentes ou
  antigas e estatísticas pós-jogo incompletas.
- A suíte completa do backend e o build de produção do frontend passaram após
  a implantação da política de paper trading v2.

Esses números são fotografias, não garantias permanentes.

## Avaliação por subsistema

### Produto e UX

Pontos fortes: identidade consistente, central de partidas, recomendações,
banca, apostas, análises e visão técnica integradas. Web e mobile compartilham
backend.

Lacunas: excesso de informação técnica para o usuário comum, pouca hierarquia
entre projeção e recomendação executável, ausência de onboarding orientado a
risco, feedback ainda não estruturado e necessidade de acessibilidade/E2E.

### Dados e provedores

A API-Football é a única fonte ativa por decisão operacional. Isso simplifica
identidade e suporte, mas cria dependência de fornecedor e não garante que odds
existam para todas as ligas/mercados. Cobertura só melhora com o tempo quando o
provedor realmente oferece o dado e o coletor o captura dentro da cota.

Prioridade: tratar cada combinação competição/capacidade como um SLA, com
frescor, causa de ausência e custo de aquisição. Volume bruto não deve definir
o núcleo.

### Motor estatístico

Poisson, Elo contextual e distribuições especializadas são bons baselines e
devem continuar disponíveis. O risco está na proliferação de mercados com
amostra pequena e na interpretação de bom Brier em eventos raros como prova de
rentabilidade.

Prioridade: reduzir o catálogo decisório inicial a poucos mercados, validar
resíduos e calibração por regime e manter os demais em observação.

### Machine learning

Há feature store temporal, walk-forward, champion/challenger, drift e fallback.
Isso é uma base correta. Contudo, ML não corrige automaticamente identidade
ruim, odds atrasadas, leakage, mudança de liga ou função objetivo inadequada.
Treinar continuamente sem gates pode automatizar degradação.

Prioridade: datasets versionados, testes temporais de contrato, model cards,
calibração segmentada e promoção canário reversível.

### Motor de recomendações

A auditoria da política anterior encontrou sobreconfiança, mercados extremos,
odds longas, exposição superior à banca e categorias de risco desalinhadas. A
v2 corrige a execução: alta confiança, intervalo conservador, odds 1,60–2,99,
horizonte de seis horas, reserva de pendências, limites diário/partida e shadow
mode. O histórico v1 permanece arquivado.

Prioridade: acumular amostra prospectiva limpa. Nenhum ajuste deve ser aprovado
por observar somente os vencedores do histórico.

### Gestão de risco e banca

As regras de domínio são amplas, mas precisam de invariantes integradas entre
recomendação, bilhete e liquidação. A política final deve incluir concentração
por competição/mercado, correlação, drawdown e kill switch além dos limites já
aplicados no paper trading.

### Operação, banco e segurança

Containers, migrations, health checks, backup/runbooks e autenticação existem.
Riscos restantes: scheduler ainda concentra responsabilidades, crescimento do
PostgreSQL/Docker, segredos locais, observabilidade limitada fora da interface e
ausência de ensaio recente de desastre completo.

## Maiores riscos do projeto

1. confundir cobertura ou volume de previsões com qualidade;
2. otimizar repetidamente sobre o mesmo histórico;
3. usar odds ausentes, antigas ou incompatíveis com a seleção;
4. liberar mercados antes da amostra prospectiva;
5. treinar continuamente sem promoção e rollback controlados;
6. esconder segmentos ruins em uma métrica global;
7. aumentar complexidade antes de estabilizar a jornada principal;
8. publicar externamente antes de segurança e operação estarem demonstradas.

## Decisão recomendada

Congelar expansão de funcionalidades por um ciclo. O próximo trabalho deve
concentrar-se em confiabilidade, redução do escopo decisório, validação
prospectiva, risco, experiência principal e operação. O roadmap vigente traduz
essa decisão em fases e gates verificáveis.
