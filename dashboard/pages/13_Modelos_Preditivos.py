"""Comparação operacional dos modelos preditivos versionados."""

import streamlit as st

from app.database.session import SessionLocal
from ultrastats_ai.infrastructure.prediction import PredictiveModelStore


st.set_page_config(page_title="Modelos Preditivos", page_icon="🧠", layout="wide")
st.title("🧠 Modelos Preditivos")
st.caption("Backtests, versões e comparação de desempenho dos modelos.")

with SessionLocal() as session:
    comparison = PredictiveModelStore(session).comparison()

if comparison:
    st.dataframe(comparison, use_container_width=True)
    best = min(comparison, key=lambda item: float(item["log_loss"]))
    st.success(
        f"Melhor log loss: {best['model_name']} v{best['model_version']} "
        f"({float(best['log_loss']):.4f})"
    )
else:
    st.info("Nenhum backtest preditivo persistido.")

st.subheader("Critérios")
st.markdown(
    """
    - **Brier score e log loss:** menores são melhores.
    - **Acurácia:** proporção do resultado mais provável corretamente previsto.
    - **Erro de calibração:** distância entre confiança e frequência observada.
    """
)
