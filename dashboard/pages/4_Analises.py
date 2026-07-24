import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.session import SessionLocal
from dashboard.services import DashboardService

st.set_page_config(
    page_title="Análises | UltraStats AI",
    page_icon="📈",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_predictions() -> list[dict]:
    with SessionLocal() as session:
        return DashboardService(session).get_predictions()


st.title("📈 Análises")
st.caption("Previsões do modelo, contextualizadas por partida e mercado.")
st.info(
    "As previsões atuais usam evidência limitada. Elas são apoio à decisão, "
    "não garantia de resultado."
)

predictions = load_predictions()
if not predictions:
    st.info(
        "Nenhuma previsão foi registrada. Aguarde a próxima sincronização "
        "ou execute-a em Collectors."
    )
    st.stop()

df = pd.DataFrame(predictions)
col1, col2, col3 = st.columns(3)
with col1:
    competition = st.selectbox(
        "Competição",
        ["Todas", *sorted(df["competicao"].dropna().unique())],
    )
with col2:
    market = st.selectbox(
        "Mercado",
        ["Todos", *sorted(df["mercado"].dropna().unique())],
    )
with col3:
    only_with_odds = st.checkbox("Somente com odds", value=False)

filtered = df.copy()
if competition != "Todas":
    filtered = filtered[filtered["competicao"] == competition]
if market != "Todos":
    filtered = filtered[filtered["mercado"] == market]
if only_with_odds:
    filtered = filtered[filtered["odd"].notna()]

metrics = st.columns(3)
metrics[0].metric("Previsões exibidas", len(filtered))
metrics[1].metric("Com odds", int(filtered["odd"].notna().sum()))
metrics[2].metric(
    "Com valor esperado",
    int(filtered["expected_value"].notna().sum()),
)

view = filtered[
    [
        "partida",
        "competicao",
        "inicio",
        "mercado",
        "selecao",
        "probability",
        "odd",
        "expected_value",
        "confidence",
        "evidence_level",
        "bookmaker",
    ]
].rename(
    columns={
        "partida": "Partida",
        "competicao": "Competição",
        "inicio": "Início",
        "mercado": "Mercado",
        "selecao": "Seleção",
        "probability": "Probabilidade",
        "odd": "Odd",
        "expected_value": "Valor esperado",
        "confidence": "Confiança",
        "evidence_level": "Evidência",
        "bookmaker": "Casa",
    }
)
for percentage_column in ("Probabilidade", "Valor esperado", "Confiança"):
    view[percentage_column] = view[percentage_column] * 100

st.dataframe(
    view,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Início": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm"),
        "Probabilidade": st.column_config.ProgressColumn(
            format="%.1f%%", min_value=0, max_value=100
        ),
        "Odd": st.column_config.NumberColumn(format="%.2f"),
        "Valor esperado": st.column_config.NumberColumn(format="%.1f%%"),
        "Confiança": st.column_config.NumberColumn(format="%.0f%%"),
    },
)

st.caption(
    "“Sem odd” significa que há previsão, mas nenhuma cotação compatível foi "
    "recebida. Nesse caso o valor esperado não pode ser calculado."
)
