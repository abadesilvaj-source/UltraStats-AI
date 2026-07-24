"""Oportunidades operacionais derivadas de odds reais e EV positivo."""

import pandas as pd
import streamlit as st
from sqlalchemy import text

from app.database.session import SessionLocal


st.set_page_config(page_title="Motor de Recomendações", page_icon="🎯", layout="wide")
st.title("🎯 Motor de Recomendações")
st.caption("Sinais com odd real correspondente e valor esperado positivo.")

with SessionLocal() as session:
    rows = session.execute(
        text(
            """
            SELECT p.id, h.name AS mandante, a.name AS visitante,
                   m.kickoff_at, mk.name AS mercado, p.selection AS seleção,
                   p.probability AS probabilidade,
                   p.implied_probability AS probabilidade_implícita,
                   p.expected_value AS ev, p.confidence AS confiança,
                   p.evidence_level AS evidência, p.risk_level AS risco
            FROM predictions p
            JOIN matches m ON m.id = p.match_id
            JOIN teams h ON h.id = m.home_team_id
            JOIN teams a ON a.id = m.away_team_id
            JOIN markets mk ON mk.id = p.market_id
            WHERE p.expected_value > 0
              AND m.status IN ('scheduled', 'in_progress')
            ORDER BY p.expected_value DESC, m.kickoff_at
            """
        )
    ).mappings().all()

if not rows:
    st.info("Nenhuma oportunidade com EV positivo e odd real está disponível.")
else:
    data = pd.DataFrame([dict(row) for row in rows])
    minimum_ev = st.slider("EV mínimo", 0.0, 1.0, 0.01, 0.01)
    data = data[data["ev"] >= minimum_ev]
    first, second, third = st.columns(3)
    first.metric("Oportunidades", len(data))
    second.metric("Partidas", data[["mandante", "visitante"]].drop_duplicates().shape[0])
    third.metric("EV máximo", f"{data['ev'].max():.2%}" if len(data) else "—")
    st.dataframe(data, use_container_width=True, hide_index=True)
    st.warning(
        "Os sinais atuais têm evidência baixa e servem para observação. "
        "Não constituem garantia de resultado ou recomendação financeira."
    )
