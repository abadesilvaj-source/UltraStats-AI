import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
import pandas as pd
import plotly.express as px
import streamlit as st

from app.database.session import SessionLocal
from app.services import PerformanceService


st.set_page_config(
    page_title="UltraStats AI",
    page_icon="⚽",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_dashboard_data() -> dict:
    """
    Busca os dados do banco.

    O cache dura 30 segundos para evitar
    consultas repetidas desnecessárias.
    """

    session = SessionLocal()

    try:
        service = PerformanceService(session)

        return {
            "summary": (
                service.get_general_summary()
            ),
            "markets": (
                service.get_market_performance()
            ),
            "competitions": (
                service
                .get_competition_performance()
            ),
            "timeline": (
                service.get_profit_timeline()
            ),
        }

    finally:
        session.close()


data = load_dashboard_data()

summary = data["summary"]
markets = data["markets"]
competitions = data["competitions"]
timeline = data["timeline"]


st.title("⚽ UltraStats AI")

st.caption(
    "Painel oficial de desempenho quantitativo"
)

st.divider()


column_1, column_2, column_3, column_4 = (
    st.columns(4)
)

column_1.metric(
    label="Apostas oficiais",
    value=summary["total_bets"],
)

column_2.metric(
    label="Taxa de acerto",
    value=f"{summary['win_rate']:.2f}%",
)

column_3.metric(
    label="Lucro acumulado",
    value=f"{summary['total_profit']:.2f}u",
)

column_4.metric(
    label="ROI",
    value=f"{summary['roi']:.2f}%",
)


column_5, column_6, column_7, column_8 = (
    st.columns(4)
)

column_5.metric(
    label="Vitórias",
    value=summary["won_bets"],
)

column_6.metric(
    label="Derrotas",
    value=summary["lost_bets"],
)

column_7.metric(
    label="Odd média",
    value=f"{summary['average_odd']:.2f}",
)

column_8.metric(
    label="EV médio",
    value=f"{summary['average_ev']:.2%}",
)


st.divider()

st.subheader("Evolução do lucro")


if timeline:
    timeline_df = pd.DataFrame(timeline)

    timeline_df["settled_at"] = pd.to_datetime(
        timeline_df["settled_at"]
    )

    profit_chart = px.line(
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
        profit_chart,
        use_container_width=True,
    )

else:
    st.info(
        "Ainda não há apostas liquidadas "
        "para exibir a evolução do lucro."
    )


st.divider()

left_column, right_column = st.columns(2)


with left_column:
    st.subheader("Desempenho por mercado")

    if markets:
        markets_df = pd.DataFrame(markets)

        market_chart = px.bar(
            markets_df,
            x="market_name",
            y="roi",
            labels={
                "market_name": "Mercado",
                "roi": "ROI (%)",
            },
        )

        st.plotly_chart(
            market_chart,
            use_container_width=True,
        )

        st.dataframe(
            markets_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "Ainda não há dados por mercado."
        )


with right_column:
    st.subheader(
        "Desempenho por competição"
    )

    if competitions:
        competitions_df = pd.DataFrame(
            competitions
        )

        competition_chart = px.bar(
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
            competition_chart,
            use_container_width=True,
        )

        st.dataframe(
            competitions_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "Ainda não há dados "
            "por competição."
        )