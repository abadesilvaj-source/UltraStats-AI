# Matriz de fontes de dados

## Regra arquitetural

Uma fonte só participa de uma previsão quando possui a capacidade necessária e
uma identidade de partida/equipe conciliada. Estar online não significa fornecer
todos os tipos de dado. O sistema não inventa estatísticas ausentes nem mistura
partidas apenas por semelhança de nomes.

| Fonte | Uso operacional atual | Limitação relevante |
|---|---|---|
| API-Football | agenda, placar, status, odds, estatísticas, eventos e escalações | cota diária e cobertura variável por competição |
| football-data.org | agenda, status e placares entram no consenso canônico | não fornece odds nem estatísticas detalhadas no plano gratuito |
| Football-Data.co.uk | resultados e odds históricas atualizam ratings e priors do modelo | não é uma fonte ao vivo |
| OpenLigaDB | agenda e placares entram no consenso e cobrem lacunas | cobertura concentrada em ligas específicas |
| StatsBomb Open Data | eventos, escalações históricas e xG validam/treinam modelos offline | conjunto histórico selecionado, não agenda mundial ao vivo |
| TheSportsDB | agenda, resultados, equipes, estádios e metadados entram na fusão canônica | API v1 gratuita; livescore e alguns métodos são premium |
| Sportmonks | agenda, eventos, estatísticas, escalações e xG entram na fusão/enriquecimento | sem token fica desativada; plano gratuito cobre Superliga Dinamarquesa e Premiership Escocesa |
| The Odds API | odds 1X2 e totais de múltiplas casas são associadas às partidas canônicas | sem chave fica desativada; consumo depende de mercados e regiões consultados |

O endpoint `GET /api/v1/health` expõe disponibilidade, latência, última
verificação e capacidades de cada conector.

## Fusão por campo

Cada observação é conciliada com uma partida canônica por identificador externo,
horário (tolerância de três horas) e similaridade normalizada dos dois clubes.
O vínculo fica persistido e é reutilizado nas sincronizações seguintes.

Para cada campo (`kickoff_at`, `status`, placar e estádio), a decisão considera:

1. consenso entre fontes independentes;
2. terminalidade do status;
3. qualidade declarada da fonte para aquele campo;
4. instante da observação.

Cada decisão grava fonte selecionada, fontes participantes, qualidade, conflitos
e horário da fusão. A API oferece:

- `GET /api/v1/providers/contributions`, com campos escolhidos por provedor;
- `data_fusion` em `/matches/{id}`, com procedência por campo;
- resumo de fusão em `/health`.

Fontes secundárias também podem criar uma partida canônica ausente na
API-Football. Depois da fusão, o motor gera previsões para todas as partidas
ativas, independentemente da fonte que as originou.

## Escalações

O coletor consulta escalações da API-Football apenas para partidas entre uma hora
antes e duas horas depois do início. Para proteger a cota gratuita:

- no máximo três partidas são consultadas por sincronização;
- uma partida já coletada não consome nova chamada;
- escalação confirmada aumenta confiança, confluência e nível de evidência;
- ausência de escalação aumenta o risco da recomendação, sem fabricar nomes.

Escalações podem ser publicadas somente perto do início e, em algumas
competições, apenas depois da partida.

## Novas fontes complementares

TheSportsDB está habilitada por padrão com a chave pública gratuita `123`.
Sportmonks e The Odds API são habilitadas somente quando
`SPORTMONKS_API_TOKEN` e `THE_ODDS_API_KEY` estão preenchidas. A ausência de uma
credencial não interrompe as demais fontes.

As odds externas são conciliadas por horário (tolerância de três horas) e
similaridade dos dois clubes. Nenhuma odd é associada apenas pela posição do
registro ou pelo nome de uma liga.

Variáveis operacionais:

- `THESPORTSDB_API_KEY` e `THESPORTSDB_BASE_URL`;
- `SPORTMONKS_API_TOKEN` e `SPORTMONKS_BASE_URL`;
- `THE_ODDS_API_KEY`, `THE_ODDS_API_SPORT_KEYS`,
  `THE_ODDS_API_REGIONS` e `THE_ODDS_API_MARKETS`.

Não é recomendado automatizar scraping de páginas de SofaScore, FBref ou
Understat sem API/licença explícita: além da instabilidade técnica, isso cria
risco de termos de uso e bloqueio.
