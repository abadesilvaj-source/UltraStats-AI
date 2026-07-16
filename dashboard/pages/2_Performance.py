import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
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
from dashboard.components import (
    render_home_metrics,
)
from dashboard.services import (
    DashboardService,
)


st.set_page_config(
    page_title="Performance | UltraStats AI",
    page_icon="📊",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_data() -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).get_performance_data()

    finally:
        session.close()


data = load_data()

summary = data["summary"]
markets = data["markets"]
competitions = data["competitions"]
timeline = data["timeline"]


st.title("📊 Performance")

st.caption(
    "Resultados históricos do UltraStats AI"
)

st.divider()


render_home_metrics(
    summary
)


st.divider()

st.subheader("Evolução do lucro")


if timeline:
    timeline_df = pd.DataFrame(
        timeline
    )

    timeline_df["settled_at"] = (
        pd.to_datetime(
            timeline_df["settled_at"]
        )
    )

    chart = px.line(
        timeline_df,
        x="settled_at",
        y="accumulated_profit",
        markers=True,
        labels={
            "settled_at": "Data",
            "accumulated_profit": (
                "Lucro acumulado (u)"
            ),
        },
    )

    st.plotly_chart(
        chart,
        use_container_width=True,
    )

else:
    st.info(
        "Ainda não existem apostas liquidadas."
    )


st.divider()


left_column, right_column = st.columns(2)


with left_column:
    st.subheader(
        "Desempenho por mercado"
    )

    if markets:
        markets_df = pd.DataFrame(
            markets
        )

        chart = px.bar(
            markets_df,
            x="market_name",
            y="roi",
            labels={
                "market_name": "Mercado",
                "roi": "ROI (%)",
            },
        )

        st.plotly_chart(
            chart,
            use_container_width=True,
        )

        st.dataframe(
            markets_df,
            use_container_width=True,
            hide_index=True,
        )


with right_column:
    st.subheader(
        "Desempenho por competição"
    )

    if competitions:
        competitions_df = pd.DataFrame(
            competitions
        )

        chart = px.bar(
            competitions_df,
            x="competition_name",
            y="roi",
            labels={
                "competition_name": (
                    "Competição"
                ),
                "roi": "ROI (%)",
            },
        )

        st.plotly_chart(
            chart,
            use_container_width=True,
        )

        st.dataframe(
            competitions_df,
            use_container_width=True,
            hide_index=True,
        )