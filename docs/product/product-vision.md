# Visão de produto — UltraStats AI

Atualizado em: 2 de agosto de 2026.

## Propósito

O UltraStats AI será uma plataforma pessoal e, futuramente, multiusuário de
inteligência para futebol. Seu trabalho não é prometer apostas vencedoras, mas
transformar dados esportivos e preços de mercado em decisões seletivas,
explicáveis, calibradas e compatíveis com limites rigorosos de risco.

## Produto final

A versão final desejada é um assistente de decisão que:

1. coleta dados confiáveis antes, durante e depois das partidas;
2. mede a qualidade e a atualidade de cada evidência;
3. produz probabilidades reproduzíveis, com incerteza explícita;
4. compara probabilidade e odd observada sem inventar preços ausentes;
5. recomenda **apostar** ou **não apostar**;
6. dimensiona exposição sem comprometer a banca;
7. explica fatores, limitações e motivos de bloqueio;
8. acompanha todas as decisões prospectivamente;
9. aprende apenas por processos temporais auditáveis;
10. protege identidade, banca e histórico de cada usuário.

## Promessa ao usuário

> Poucas recomendações, melhores evidências e risco controlado.

O produto não utilizará “próximo de 100%” como promessa. A taxa de acerto pode
ser aumentada artificialmente escolhendo odds muito baixas e ainda gerar
prejuízo. As metas corretas são calibração, vantagem sobre o preço, CLV, retorno
ajustado ao risco, drawdown e transparência da abstenção.

## Público e superfícies

- **Inicial:** proprietário e grupo pequeno de testadores convidados.
- **Web:** estação principal para análise, administração e auditoria.
- **Mobile:** experiência responsiva para partidas, alertas, recomendações e
  acompanhamento; usa a mesma API e não replica regras de negócio.
- **Visão técnica:** superfície do operador, não do usuário comum.

## Jornada principal

1. Usuário encontra uma partida.
2. Visualiza cobertura, frescor e disponibilidade de escalações/odds.
3. Recebe uma projeção com intervalo de incerteza.
4. O motor decide entre alta confiança, observação ou sem aposta.
5. Quando executável, a recomendação mostra mercado, seleção, odd mínima,
   validade, stake máximo e motivos.
6. O usuário registra ou ignora a decisão.
7. Resultado, CLV e impacto na banca são conciliados automaticamente.
8. O histórico mostra acertos, erros, calibração e evolução sem ocultar perdas.

## Princípios irrenunciáveis

- nenhuma informação posterior ao kickoff entra em uma previsão pré-jogo;
- dados ausentes nunca são preenchidos para melhorar cobertura;
- recomendação sem odd recente é “sem aposta”;
- modelo novo não substitui o champion sem validação prospectiva;
- aprendizado não usa o resultado da aposta como feature circular;
- banca real e paper trading permanecem isolados;
- exposição pendente é reservada;
- nenhum segmento é promovido apenas por tamanho de amostra;
- toda decisão pode ser reconstruída com dados, versão e cutoff;
- jogo responsável faz parte do produto, não apenas do texto jurídico.

## Métricas de sucesso

### Produto

- tempo até encontrar e compreender uma recomendação;
- taxa de tarefas concluídas sem ajuda;
- retenção dos testadores e feedback resolvido;
- zero acesso cruzado entre usuários.

### Dados

- cobertura elegível, frescor, completude e taxa de identidade correta;
- percentual de partidas com abertura, preço atual e closing odds;
- cobertura de escalação confirmada antes da decisão.

### Modelos

- Brier, log loss e ECE por mercado, competição, odds e horizonte;
- ganho fora da amostra sobre baseline;
- estabilidade e drift por segmento;
- cobertura seletiva e taxa de abstenção.

### Decisão e risco

- CLV médio e percentual de decisões com CLV positivo;
- ROI/yield prospectivo flat-stake e pela política de stake;
- drawdown máximo, exposição e concentração;
- acerto por faixa de probabilidade, nunca isoladamente.

## Definição de versão final v1.0

A v1.0 só poderá ser declarada quando:

- operação contínua demonstrar recuperação automática e backups restauráveis;
- dados-alvo cumprirem SLA por competição por pelo menos 30 dias;
- pelo menos dois mercados tiverem validação prospectiva suficiente;
- paper trading v2 tiver no mínimo 1.000 decisões liquidadas e 100 por segmento
  promovido, sem mistura com backfill;
- política apresentar calibração aceitável, CLV não negativo e drawdown dentro
  do limite aprovado; lucro não é presumido;
- piloto multiusuário não encontrar falhas P0/P1 abertas;
- segurança, privacidade e jogo responsável forem revisados;
- implantação e rollback forem ensaiados antes de qualquer acesso externo.

## Fora da promessa

- garantia de lucro ou acerto;
- automação de apostas com dinheiro real;
- venda de sinais sem evidência prospectiva;
- promoção de mercados baseada em backtest isolado;
- expansão para outros esportes antes da maturidade no futebol.
