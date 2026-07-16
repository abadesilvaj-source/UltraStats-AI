# UltraStats AI

Plataforma de análise quantitativa para apostas esportivas.

## Objetivos

- Armazenar jogos e estatísticas.
- Calcular probabilidades.
- Comparar probabilidades com odds.
- Identificar apostas com valor esperado positivo.
- Registrar resultados.
- Auditar previsões.
- Acompanhar ROI, CLV, Yield e Drawdown.

## Tecnologias

- Python
- PostgreSQL
- Docker
- SQLAlchemy
- Pandas
- Streamlit
- Git

## Status

Projeto em desenvolvimento.
## Arquitetura atual

O projeto utiliza uma arquitetura em camadas:

- `models`: representam as tabelas do banco.
- `repositories`: realizam consultas e persistência.
- `services`: concentram regras de negócio.
- `scripts`: executam tarefas manuais.
- `tests`: validam o comportamento do sistema.

## Estrutura principal

```text
app/
├── core/
├── database/
├── models/
├── repositories/
├── schemas/
├── services/
└── utils/
