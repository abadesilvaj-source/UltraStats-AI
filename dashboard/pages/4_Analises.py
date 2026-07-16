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
    page_title="Análises | UltraStats AI",
    page_icon="📈",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_predictions() -> list[dict]:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).get_predictions()

    finally:
        session.close()


st.title("📈 Análises")

st.caption(
    "Previsões produzidas pelo modelo"
)

st.divider()


predictions = load_predictions()


if not predictions:
    st.info(
        "Nenhuma previsão foi registrada."
    )
    st.stop()


predictions_df = pd.DataFrame(
    predictions
)


minimum_ev = st.slider(
    "EV mínimo",
    min_value=-0.50,
    max_value=1.00,
    value=0.00,
    step=0.01,
    format="%.2f",
)


filtered_df = predictions_df[
    predictions_df[
        "expected_value"
    ].fillna(0)
    >= minimum_ev
]


st.metric(
    "Análises encontradas",
    len(filtered_df),
)


st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
)