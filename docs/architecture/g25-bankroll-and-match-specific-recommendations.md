# G25 — Banca operacional e recomendações específicas por confronto

## Gestão de banca

- depósitos e saques são operações persistidas e auditáveis;
- o saldo da tela é sempre o saldo devolvido pelo backend;
- edição local fictícia do saldo foi removida;
- o histórico exibido vem de `bet_slips`, não de dados demonstrativos;
- lucro, ganhos e perdas podem ser filtrados por 7 dias, 1 mês, 1 ano ou
  todo o período.

## Motor estatístico

A previsão de vencedor combina:

1. ataque e defesa aprendidos com partidas liquidadas;
2. `power_rating` relativo das equipes;
3. Poisson com vantagem de mando;
4. consenso sem margem das odds disponíveis para o confronto.

O consenso de mercado responde por 65% do blend quando há cotações completas
de 1X2; o modelo estatístico responde por 35%. Sem odds completas, o modelo
continua funcionando, mas a baixa evidência permanece explícita.

## Motor de recomendações

As previsões existentes são recalculadas após a atualização dos ratings e das
odds. O recomendador continua exigindo odds atuais, valor esperado conservador,
validação do modelo e evidência mínima para marcar uma indicação como
acionável. Projeções não aprovadas continuam visíveis como leitura do modelo,
mas não são tratadas como aposta segura.

Um teste de regressão garante que um visitante claramente favorito no consenso
das odds supere o prior de mando, evitando a repetição automática de `Home`.
