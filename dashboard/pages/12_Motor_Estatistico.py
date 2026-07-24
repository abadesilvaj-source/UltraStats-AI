"""Explorador dos snapshots produzidos pelo Motor Estatístico."""

import streamlit as st

from app.database.session import SessionLocal
from ultrastats_ai.infrastructure.statistics import StatisticalSnapshotStore


st.set_page_config(page_title="Motor Estatístico", page_icon="📊", layout="wide")
st.title("📊 Motor Estatístico")
st.caption("Indicadores temporais auditáveis usados pelas próximas camadas analíticas.")

team_id = st.text_input("Identificador canônico da equipe")
if team_id:
    with SessionLocal() as session:
        snapshot = StatisticalSnapshotStore(session).latest(team_id.strip())
    if snapshot is None:
        st.info("Nenhum snapshot disponível para esta equipe.")
    else:
        first, second, third = st.columns(3)
        first.metric("Amostras", snapshot.sample_size)
        second.metric("Amostra efetiva", f"{snapshot.effective_sample_size:.2f}")
        third.metric("Confiabilidade", f"{snapshot.reliability:.1%}")
        st.subheader("Métricas")
        st.dataframe(
            [{"Métrica": key, "Valor": float(value)} for key, value in snapshot.metrics.items()],
            use_container_width=True,
        )
        st.subheader("Tendências e contextos")
        st.json(
            {
                "trends": {key: str(value) for key, value in snapshot.trends.items()},
                "contexts": {key: str(value) for key, value in snapshot.contexts.items()},
            }
        )
