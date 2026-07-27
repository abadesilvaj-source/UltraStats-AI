# G26 — Motor estatístico e recomendador avançados

## Arquitetura implementada

O motor passou a separar previsão, confiança e decisão de aposta.

### Força contextual

- Elo online com vantagem de mando e multiplicador por diferença de gols;
- ataque e defesa atualizados após cada partida;
- forma ponderada por recência;
- ajuste pela força do adversário;
- desempenho contextual de mandante e visitante;
- penalização por descanso inferior a quatro dias;
- escalações e continuidade já coletadas pelos provedores capazes.

### Modelos especializados

- 1X2: Poisson, força contextual, Elo e consenso de mercado sem margem;
- gols e ambas marcam: distribuição de placares;
- escanteios: cauda de Poisson com ritmo e ratings específicos;
- cartões: cauda de Poisson com intensidade e ratings disciplinares.

O consenso das odds não substitui o modelo. Ele integra o ensemble somente
quando o mercado 1X2 está completo. Cotações incompletas não são usadas como
prova de força.

### Calibração e validação

- calibração segmentada por competição e mercado;
- fallback por mercado quando a amostra da competição é pequena;
- validação walk-forward, champion/challenger e drift continuam no ciclo de
  inteligência operacional;
- previsões e oportunidades são recalculadas após atualização do modelo.

### Política de recomendação

Uma previsão não é automaticamente uma aposta. O recomendador exige:

- modelo aprovado;
- odd disponível e atual;
- valor esperado conservador;
- amostra e evidência suficientes;
- ausência de bloqueios operacionais.

Quando essas condições não existem, a interface apresenta **Sem aposta**, com
a margem entre cenários. Mercados de gols correlacionados são deduplicados:
somente a melhor oportunidade permanece acionável por partida.

### Neutralidade multiprovedor

As observações continuam com peso-base igual por provedor. Confiança é
determinada por disponibilidade do campo, consenso, recência, cobertura de
escalação e amostra — nunca pelo nome da API.

## Garantias

- nenhuma recomendação segura sem EV conservador;
- favoritos visitantes podem superar o prior de mando;
- probabilidades variam por confronto;
- exposição correlacionada é bloqueada;
- baixa evidência produz “Sem aposta”;
- ratings evoluem automaticamente após liquidação.
