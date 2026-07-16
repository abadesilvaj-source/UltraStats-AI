import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

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
    page_title="UltraStats AI",
    page_icon="⚽",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_home_data() -> dict:
    session = SessionLocal()

    try:
        service = DashboardService(
            session
        )

        return service.get_home_data()

    finally:
        session.close()


data = load_home_data()

performance = data["performance"]
bankroll = data["bankroll"]


st.title("⚽ UltraStats AI")

st.caption(
    "Plataforma quantitativa de análise esportiva"
)

st.divider()


render_home_metrics(
    performance
)


st.divider()


left_column, right_column = st.columns(2)


with left_column:
    st.subheader("Resumo da banca")

    if bankroll:
        st.metric(
            "Saldo atual",
            (
                f"{bankroll['currency']} "
                f"{bankroll['current_balance']:.2f}"
            ),
        )

        st.metric(
            "Valor de 1 unidade",
            (
                f"{bankroll['currency']} "
                f"{bankroll['unit_value']:.2f}"
            ),
        )

        st.write(
            f"Banca ativa: **{bankroll['name']}**"
        )

    else:
        st.warning(
            "Nenhuma banca ativa foi encontrada."
        )


with right_column:
    st.subheader("Operação atual")

    st.metric(
        "Apostas pendentes",
        data["pending_bets"],
    )

    st.metric(
        "Apostas registradas",
        data["official_bets"],
    )

    if data["pending_bets"] > 0:
        st.warning(
            "Existem apostas aguardando liquidação."
        )
    else:
        st.success(
            "Não há apostas pendentes."
        )


st.divider()

st.subheader("Saúde inicial do modelo")

if performance["total_bets"] < 30:
    st.info(
        "A base ainda possui poucas apostas. "
        "ROI e taxa de acerto não são "
        "estatisticamente representativos."
    )
else:
    st.success(
        "A base já possui volume suficiente "
        "para iniciar análises históricas."
    )