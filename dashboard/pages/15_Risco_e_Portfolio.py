"""Painel de exposição, desempenho e snapshots de portfólio."""

from decimal import Decimal

import streamlit as st

from app.database.session import SessionLocal
from ultrastats_ai.infrastructure.risk import RiskPortfolioStore


st.set_page_config(page_title="Risco e Portfólio", page_icon="🛡️", layout="wide")
st.title("🛡️ Risco e Portfólio")
st.caption("Banca, exposição, limites e desempenho dos portfólios calculados.")

user_id = st.text_input("Usuário", value="default")
with SessionLocal() as session:
    history = RiskPortfolioStore(session).history(user_id)

if history:
    current = history[0]
    bankroll = Decimal(current.bankroll)
    exposure = Decimal(current.total_exposure)
    metrics = current.metrics
    first, second, third, fourth = st.columns(4)
    first.metric("Banca", f"{bankroll:.2f}")
    second.metric("Exposição", f"{exposure:.2f}")
    third.metric("ROI", f"{Decimal(str(metrics['roi'])):.2%}")
    fourth.metric("Drawdown máximo", f"{Decimal(str(metrics['maximum_drawdown'])):.2%}")
    st.subheader("Posições")
    st.dataframe(current.positions, use_container_width=True)
    if current.blocked:
        st.subheader("Oportunidades bloqueadas")
        st.json(current.blocked)
else:
    st.info("Nenhum snapshot de portfólio foi persistido para este usuário.")

st.subheader("Controles aplicados")
st.markdown(
    """
    - Kelly integral e fracionado conforme o perfil de risco;
    - limites por aposta, dia, competição e mercado;
    - limite de posições correlacionadas;
    - otimização determinística pelo Opportunity Score;
    - acompanhamento de ROI, yield e drawdown máximo.
    """
)
