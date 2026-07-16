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
    render_bankroll_metrics,
)
from dashboard.services import (
    DashboardService,
)


st.set_page_config(
    page_title="Banca | UltraStats AI",
    page_icon="💰",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_bankrolls() -> list[dict]:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).get_bankrolls()

    finally:
        session.close()


@st.cache_data(ttl=30)
def load_bankroll_details(
    bankroll_id: int,
) -> dict:
    session = SessionLocal()

    try:
        return DashboardService(
            session
        ).get_bankroll_details(
            bankroll_id
        )

    finally:
        session.close()


st.title("💰 Gestão de Banca")

st.caption(
    "Saldo, transações, unidades e drawdown"
)

st.divider()


bankrolls = load_bankrolls()


if not bankrolls:
    st.warning(
        "Nenhuma banca foi cadastrada."
    )
    st.stop()


bankroll_options = {
    bankroll["name"]: bankroll["id"]
    for bankroll in bankrolls
}


selected_name = st.selectbox(
    "Selecione a banca",
    options=list(
        bankroll_options.keys()
    ),
)


selected_id = bankroll_options[
    selected_name
]


data = load_bankroll_details(
    selected_id
)

bankroll = data["bankroll"]
transactions = data["transactions"]


render_bankroll_metrics(
    bankroll
)


st.divider()


column_1, column_2 = st.columns(2)


with column_1:
    st.metric(
        "Saldo inicial",
        (
            f"{bankroll['currency']} "
            f"{bankroll['initial_balance']:.2f}"
        ),
    )


with column_2:
    st.metric(
        "Drawdown atual",
        (
            f"{bankroll['current_drawdown']:.2f}%"
        ),
    )


st.divider()

st.subheader("Evolução do saldo")


if transactions:
    transactions_df = pd.DataFrame(
        transactions
    )

    transactions_df["date"] = pd.to_datetime(
        transactions_df["date"]
    )

    balance_chart = px.line(
        transactions_df,
        x="date",
        y="balance_after",
        markers=True,
        labels={
            "date": "Data",
            "balance_after": "Saldo",
        },
    )

    st.plotly_chart(
        balance_chart,
        use_container_width=True,
    )

    st.subheader(
        "Histórico de transações"
    )

    st.dataframe(
        transactions_df,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info(
        "A banca ainda não possui transações."
    )