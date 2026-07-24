"""Histórico seguro e auditável do motor de recomendações."""

import streamlit as st

from app.database.session import SessionLocal
from ultrastats_ai.infrastructure.recommendation import RecommendationStore


st.set_page_config(page_title="Motor de Recomendações", page_icon="🎯", layout="wide")
st.title("🎯 Motor de Recomendações")
st.caption("Oportunidades aprovadas pelos filtros de valor, confiança, liquidez e segurança.")

with SessionLocal() as session:
    history = RecommendationStore(session).safe_history()

if history:
    conservative = sum(item["risk"] == "conservative" for item in history)
    moderate = sum(item["risk"] == "moderate" for item in history)
    speculative = sum(item["risk"] in {"high_risk", "speculative"} for item in history)
    first, second, third, fourth = st.columns(4)
    first.metric("Recomendações seguras", len(history))
    second.metric("Conservadoras", conservative)
    third.metric("Moderadas", moderate)
    fourth.metric("Alto risco/especulativas", speculative)
    st.dataframe(history, use_container_width=True)
else:
    st.info("Nenhuma recomendação segura foi persistida.")

st.subheader("Proteções ativas")
st.markdown(
    """
    - cotações indisponíveis, antigas, futuras ou sem liquidez são descartadas;
    - recomendações abaixo do EV ou da confiança mínimos são bloqueadas;
    - odds acima do limite de segurança nunca são publicadas;
    - o portfólio limita recomendações correlacionadas;
    - decisões e justificativas permanecem auditáveis no histórico.
    """
)
