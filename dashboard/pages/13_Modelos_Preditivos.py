"""Resumo dos modelos que produziram previsões operacionais."""

import pandas as pd
import streamlit as st
from sqlalchemy import text

from app.database.session import SessionLocal


st.set_page_config(page_title="Modelos Preditivos", page_icon="🧠", layout="wide")
st.title("🧠 Modelos Preditivos")
st.caption("Versões em operação e cobertura das previsões persistidas.")

with SessionLocal() as session:
    rows = session.execute(
        text(
            """
            SELECT model_version,
                   count(*) AS previsões,
                   count(expected_value) AS com_ev,
                   avg(confidence) AS confiança_média,
                   min(created_at) AS primeira_execução,
                   max(created_at) AS última_execução
            FROM predictions
            GROUP BY model_version
            ORDER BY última_execução DESC
            """
        )
    ).mappings().all()

if not rows:
    st.info("Nenhuma previsão foi persistida.")
else:
    data = pd.DataFrame([dict(row) for row in rows])
    first, second, third = st.columns(3)
    first.metric("Modelos ativos", len(data))
    second.metric("Previsões", int(data["previsões"].sum()))
    third.metric("Com odds e EV", int(data["com_ev"].sum()))
    st.dataframe(data, use_container_width=True, hide_index=True)
    st.warning(
        "operational-poisson-v1 começa com priors neutros e evidência baixa. "
        "A confiança deve crescer somente após histórico suficiente e calibração."
    )
