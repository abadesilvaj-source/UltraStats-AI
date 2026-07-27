# Matriz de fontes de dados

## Regra arquitetural

Uma fonte só participa de uma previsão quando possui a capacidade necessária e
uma identidade de partida/equipe conciliada. Estar online não significa fornecer
todos os tipos de dado. O sistema não inventa estatísticas ausentes nem mistura
partidas apenas por semelhança de nomes.

| Fonte | Uso operacional atual | Limitação relevante |
|---|---|---|
| API-Football | agenda, placar, status, odds, estatísticas, eventos e escalações | cota diária e cobertura variável por competição |
| football-data.org | competições, agenda e placares de confirmação | não fornece odds nem estatísticas detalhadas no plano gratuito |
| Football-Data.co.uk | resultados e odds históricas para treinamento | não é uma fonte ao vivo |
| OpenLigaDB | agenda e placares de confirmação | cobertura concentrada em ligas específicas |
| StatsBomb Open Data | eventos, escalações históricas e xG para treinamento/validação | conjunto histórico selecionado, não agenda mundial ao vivo |

O endpoint `GET /api/v1/health` expõe disponibilidade, latência, última
verificação e capacidades de cada conector.

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
