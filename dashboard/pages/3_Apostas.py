import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.database.session import SessionLocal
from dashboard.services import (
    DashboardService,
)


st.set_page_config(
    page_title="Apostas | UltraStats AI",
    page_icon="🎯",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_bets() -> list[dict]:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).get_bets()

    finally:
        session.close()


st.title("🎯 Apostas")

st.caption(
    "Histórico completo das apostas registradas"
)

st.divider()


bets = load_bets()


if not bets:
    st.info(
        "Nenhuma aposta foi registrada."
    )
    st.stop()


bets_df = pd.DataFrame(bets)


status_options = [
    "Todos",
    "pending",
    "settled",
]


selected_status = st.selectbox(
    "Filtrar por status",
    status_options,
)


if selected_status != "Todos":
    bets_df = bets_df[
        bets_df["status"]
        == selected_status
    ]


only_official = st.checkbox(
    "Mostrar apenas apostas oficiais",
    value=True,
)


if only_official:
    bets_df = bets_df[
        bets_df["official"] == True
    ]


st.dataframe(
    bets_df,
    use_container_width=True,
    hide_index=True,
)