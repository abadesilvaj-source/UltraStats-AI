"""Painel operacional dos providers canônicos."""

import streamlit as st

from app.database.session import SessionLocal
from ultrastats_ai.infrastructure.providers import (
    ProviderConfigurationError,
    ProviderDashboard,
    SqlAlchemyHealthStore,
    build_football_data_provider,
)


st.set_page_config(page_title="Providers", page_icon="🌐", layout="wide")
st.title("🌐 Providers")
st.caption("Disponibilidade, latência e histórico das integrações externas.")

st.subheader("Matriz de capacidades")
st.dataframe(
    [
        {"Provider": "Football-Data.org", "Jogos": True, "Ao vivo": False, "Estatísticas": False, "Odds": False, "xG": False},
        {"Provider": "API-Football", "Jogos": True, "Ao vivo": True, "Estatísticas": True, "Odds": True, "xG": False},
        {"Provider": "Football-Data.co.uk", "Jogos": True, "Ao vivo": False, "Estatísticas": False, "Odds": True, "xG": False},
        {"Provider": "StatsBomb Open Data", "Jogos": True, "Ao vivo": False, "Estatísticas": True, "Odds": False, "xG": True},
        {"Provider": "OpenLigaDB", "Jogos": True, "Ao vivo": False, "Estatísticas": False, "Odds": False, "xG": False},
    ],
    use_container_width=True,
)
st.caption(
    "API-Football requer API_FOOTBALL_KEY. O motor registra proveniência e "
    "continua em modo degradado quando uma fonte falha."
)

if st.button("Verificar Football-Data.org", type="primary"):
    try:
        provider = build_football_data_provider()
        with SessionLocal() as session:
            store = SqlAlchemyHealthStore(session)
            health = ProviderDashboard().snapshot((provider,), store.save)[0]
            session.commit()
        provider.close()
        if health.available:
            st.success(f"{health.provider}: {health.message} ({health.latency_ms} ms)")
        else:
            st.error(f"{health.provider}: {health.message}")
    except ProviderConfigurationError as error:
        st.warning(str(error))

with SessionLocal() as session:
    rows = SqlAlchemyHealthStore(session).latest()

if rows:
    st.dataframe(
        [
            {
                "Provider": item.provider,
                "Disponível": item.available,
                "Latência (ms)": item.latency_ms,
                "Mensagem": item.message,
                "Verificado em": item.checked_at,
            }
            for item in rows
        ],
        use_container_width=True,
    )
else:
    st.info("Nenhum health check persistido.")
