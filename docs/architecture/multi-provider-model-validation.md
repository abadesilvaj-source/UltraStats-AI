# G15.1 e G15.2 — Multi-provider e validação de modelos

## Escopo entregue

O motor trata fontes externas por capacidade. Cada observação conserva
provider, identidade externa, instante e payload. Falhas isoladas produzem um
relatório degradado sem interromper fontes saudáveis.

| Provider | Uso |
|---|---|
| Football-Data.org | competições, equipes, partidas e classificação |
| API-Football | fixtures, live, estatísticas, eventos e odds |
| Football-Data.co.uk | histórico de resultados e odds em CSV |
| StatsBomb Open Data | eventos históricos e xG de pesquisa |
| OpenLigaDB | calendário e resultados complementares |

Understat, FBref, Transfermarkt e endpoints internos do SofaScore não fazem
parte do motor. Uma integração futura depende de API ou licença explícita.

## Prioridade, identidade e continuidade

`PROVIDER_PRIORITY` define a ordem determinística. `MultiSourceEngine` consulta
fontes aptas, agrega observações e registra falhas por provider.
`DataFusionEngine` e `IdentityResolutionEngine` resolvem proveniência por campo
e identidades canônicas. Nenhuma identidade externa vira chave do domínio.

Odds são snapshots temporais identificados por provider, partida, bookmaker,
mercado, seleção e instante. Assim uma odd futura não contamina um backtest.

## Validação de modelos

`TemporalDatasetBuilder` cria treino, validação, teste e janelas rolling sem
embaralhar o tempo. `BacktestEngine` calcula Brier multiclasse, log loss,
acurácia, expected calibration error e ROI simulado quando existem odds.
`CalibrationModel` aplica temperature scaling. `ModelGate` exige amostra
mínima e limites explícitos; qualquer falha bloqueia a promoção.

## Persistência

A migration `b8151a2c9e10` cria `provider_capabilities`, `odds_snapshots`,
`training_datasets` e `model_validations`. Datasets registram versão, cutoff,
esquema, cobertura e checksum. Validações ligam modelo e dataset e guardam a
decisão auditável.

## Credenciais

`API_FOOTBALL_KEY` habilita a API-Football. Sem a chave, o factory não a
instancia e o sistema continua com fontes públicas. Tokens não são persistidos.
