"""Visão operacional das equipes e partidas promovidas."""

import pandas as pd
import streamlit as st
from sqlalchemy import text

from app.database.session import SessionLocal


st.set_page_config(page_title="Motor Estatístico", page_icon="📊", layout="wide")
st.title("📊 Motor Estatístico")
st.caption("Cobertura e ratings usados nas previsões operacionais.")

with SessionLocal() as session:
    rows = session.execute(
        text(
            """
            SELECT t.id, t.name AS equipe, t.league AS competição,
                   t.power_rating, t.attack_rating, t.defense_rating,
                   count(m.id) AS partidas
            FROM teams t
            LEFT JOIN matches m
              ON m.home_team_id = t.id OR m.away_team_id = t.id
            WHERE t.source = 'api_football'
            GROUP BY t.id, t.name, t.league, t.power_rating,
                     t.attack_rating, t.defense_rating
            ORDER BY partidas DESC, t.name
            """
        )
    ).mappings().all()

if not rows:
    st.info("Nenhuma equipe real foi processada.")
else:
    data = pd.DataFrame([dict(row) for row in rows])
    first, second, third = st.columns(3)
    first.metric("Equipes processadas", len(data))
    second.metric("Partidas vinculadas", int(data["partidas"].sum() / 2))
    third.metric("Com histórico", int((data["partidas"] > 0).sum()))
    query = st.text_input("Filtrar equipe ou competição").strip()
    if query:
        mask = (
            data["equipe"].str.contains(query, case=False, na=False)
            | data["competição"].str.contains(query, case=False, na=False)
        )
        data = data[mask]
    st.dataframe(data, use_container_width=True, hide_index=True)
    st.caption(
        "Ratings 50 representam o prior neutro. Eles serão recalibrados conforme "
        "resultados e estatísticas históricas forem acumulados."
    )
