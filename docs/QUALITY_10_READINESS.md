# Qualidade operacional e critérios de maturidade

O UltraStats separa qualidade de software de qualidade preditiva. A primeira é
verificável imediatamente por testes, saúde, latência e integridade; a segunda
depende de dados pós-jogo e só pode subir com validação temporal fora da amostra.

## Critérios usados pelo painel

- **Cobertura estatística:** considera apenas competições habilitadas pelo catálogo
  operacional. Uma janela sem partidas elegíveis vale 0%, e não 100%.
- **Cobertura de odds:** exige preço coletado nas últimas oito horas; odd antiga não
  confirma valor de mercado.
- **Escalações:** só entra no denominador quando existe partida elegível na janela.
- **Neutralidade:** pesos-base são iguais, mas o painel também mostra contribuição
  efetiva, candidatos e participação do maior provedor.
- **Recomendação:** probabilidade e odd justa continuam disponíveis sem preço atual,
  porém valor esperado confirmado exige odd recente de bookmaker.
- **Machine learning:** promoção de modelo depende de validação walk-forward,
  calibração, Brier score e ausência de regressão contra o baseline.

## Rotina operacional

1. Atualização ao vivo a cada minuto.
2. Backfill estatístico em lotes compatíveis com a cota Ultra.
3. Odds a cada 15 minutos, dividindo ligas em lotes rotativos para não bloquear o
   worker ao vivo.
4. Payloads brutos sobrevivem a interrupções e são promovidos de forma idempotente.
5. Execuções abandonadas são encerradas automaticamente no ciclo seguinte.

## O que impede uma nota literal 10/10

- indisponibilidade, atraso ou ausência de mercado nos provedores externos;
- competições sem estatísticas, escalações ou odds cobertas pelo plano contratado;
- ausência de amostra suficiente de apostas liquidadas para provar ROI e CLV;
- mudança de comportamento entre temporadas, treinadores e elencos.

Essas condições não são mascaradas: aparecem como cobertura, frescor, incidentes,
contribuição por provedor e bloqueios de recomendação. O objetivo operacional é
maximizar cobertura e estabilidade sem transformar ausência de evidência em certeza.
