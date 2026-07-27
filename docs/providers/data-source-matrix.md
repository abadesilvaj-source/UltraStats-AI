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

## Fonte gratuita complementar

TheSportsDB é o próximo conector recomendado para redundância de metadados,
elencos, agenda e escalações quando disponíveis. A API gratuita informa limite
de 30 requisições por minuto, mas livescore completo e parte dos recursos são
restritos. Ela deve entrar como fonte complementar, nunca substituir a
API-Football para estatísticas detalhadas.

Não é recomendado automatizar scraping de páginas de SofaScore, FBref ou
Understat sem API/licença explícita: além da instabilidade técnica, isso cria
risco de termos de uso e bloqueio.
