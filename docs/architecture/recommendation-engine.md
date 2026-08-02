# Motor de Recomendações

> Regra vigente: sem odd real e atual não existe recomendação acionável. ML ou
> ensemble reprovado retorna ao baseline; métricas financeiras usam somente
> apostas oficiais liquidadas.

## Objetivo

A G10 transforma probabilidades calibradas e cotações observadas em
oportunidades explicáveis, comparáveis e auditáveis. O motor não executa
apostas: ele aprova ou bloqueia recomendações conforme uma política explícita.

## Fluxo

```text
probabilidade + confiança + confiabilidade + cotações
                         |
                         v
        filtro de disponibilidade, idade e liquidez
                         |
                         v
    melhor odd -> odd justa -> EV -> edge -> Opportunity Score
                         |
                         v
        filtros de segurança + classificação de risco
                         |
                         v
       ranking -> diversificação -> histórico auditável
```

## Métricas

- `probabilidade implícita = 1 / odd oferecida`;
- `odd justa = 1 / probabilidade do modelo`;
- `EV = probabilidade do modelo × odd oferecida - 1`;
- `edge = probabilidade do modelo - probabilidade implícita`;
- `confiança = confiança do modelo × confiabilidade da amostra`;
- `Opportunity Score` combina EV positivo, confiança e liquidez, penalizando
  odds mais altas.

O score só ordena oportunidades que passaram pelos filtros. Ele nunca torna
segura uma recomendação bloqueada.

## Evidência de jogadores

Cobertura individual suficiente acrescenta evidência ao forecast, mas não
substitui odds, histórico ou validação do mercado. As explicações registram
força dos titulares, estado da escalação e impacto ponderado dos desfalques.
Cobertura abaixo de 45% mantém a previsão coletiva e gera o fator adverso
`cobertura_individual_insuficiente`; ausências relevantes geram
`desfalque_de_jogador_relevante`.

## Segurança e risco

A política define EV, confiança e liquidez mínimos, odd máxima e idade máxima
da cotação. Cotações indisponíveis, antigas ou futuras são descartadas.
Oportunidades sem cotação elegível, abaixo dos limites ou acima da odd máxima
são persistidas como bloqueadas, mas não aparecem no histórico público seguro.

O risco possui cinco faixas: `conservative`, `moderate`, `aggressive`,
`high_risk` e `speculative`. Odds maiores ou confiança menor elevam a
classificação. A seleção de portfólio também limita itens com a mesma chave de
correlação.

## Persistência e auditoria

`recommendation_opportunities` guarda snapshots imutáveis com métricas,
explicações, bloqueios e classificação. `recommendation_audit` registra ação,
responsável, motivo e instante. A migration `c3ae0150c006` cria e reverte as
duas estruturas.

O painel `14_Motor_de_Recomendacoes.py` consulta somente o histórico seguro.
Bloqueios continuam disponíveis para investigação e auditoria no banco.

## Garantias

A G10 foi concluída com 2.489 testes e 100% de cobertura de linhas e branches.
Os testes incluem validações, cinco faixas de risco, filtros de segurança,
comparação de odds, ranking, correlação, persistência, auditoria e reversão da
migration.
